"""
ETQ (Exchange Traded Quantity), Rolling Average Price, and LTQ Dynamics Engine.
Maintains O(1) rolling time windows for 5m, 20m, 60m execution totals and prices.
"""
from collections import deque
from dataclasses import dataclass
import time
from typing import Dict, Optional, Tuple
from app.config import (
    ETQ_5M_SECONDS, ETQ_20M_SECONDS, ETQ_60M_SECONDS,
    AVG_PRICE_20M_SECONDS, AVG_PRICE_60M_SECONDS,
    LTQ_FAST_WINDOW_SECONDS, LTQ_SLOW_WINDOW_SECONDS
)

@dataclass
class ETQResult:
    symbol: str
    etq_5m: int
    etq_20m: int
    etq_60m: int
    avg_price_20m: float
    avg_price_60m: float
    ltq_2m_avg: float
    ltq_5m_avg: float
    ltq_surge_ratio: float  # ltq_2m_avg / ltq_5m_avg

class RollingTimeWindow:
    """
    O(1) Rolling window for quantity sums or price averages over a given time duration in seconds.
    """

    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.buffer = deque()  # (timestamp, value)
        self.total_sum: float = 0.0

    def add(self, timestamp: float, value: float) -> None:
        self.buffer.append((timestamp, value))
        self.total_sum += value
        self._evict_old(timestamp)

    def _evict_old(self, current_time: float) -> None:
        cutoff = current_time - self.duration
        while self.buffer and self.buffer[0][0] < cutoff:
            _, old_val = self.buffer.popleft()
            self.total_sum -= old_val

    def get_sum(self, current_time: float) -> float:
        self._evict_old(current_time)
        return max(0.0, self.total_sum)

    def get_average(self, current_time: float) -> float:
        self._evict_old(current_time)
        if not self.buffer:
            return 0.0
        return self.total_sum / len(self.buffer)

    def get_count(self, current_time: float) -> int:
        self._evict_old(current_time)
        return len(self.buffer)

class ETQSingleTracker:
    """
    Tracks ETQ, Avg Price, and LTQ ratio per stock.
    """

    def __init__(self):
        self.etq_5m_win = RollingTimeWindow(ETQ_5M_SECONDS)
        self.etq_20m_win = RollingTimeWindow(ETQ_20M_SECONDS)
        self.etq_60m_win = RollingTimeWindow(ETQ_60M_SECONDS)

        self.price_20m_win = RollingTimeWindow(AVG_PRICE_20M_SECONDS)
        self.price_60m_win = RollingTimeWindow(AVG_PRICE_60M_SECONDS)

        self.ltq_2m_win = RollingTimeWindow(LTQ_FAST_WINDOW_SECONDS)
        self.ltq_5m_win = RollingTimeWindow(LTQ_SLOW_WINDOW_SECONDS)

        self.latest_ltp: float = 0.0

    def update(self, timestamp: float, ltp: float, ltq: int) -> ETQResult:
        self.latest_ltp = ltp

        # Add LTQ to ETQ windows
        self.etq_5m_win.add(timestamp, ltq)
        self.etq_20m_win.add(timestamp, ltq)
        self.etq_60m_win.add(timestamp, ltq)

        # Add LTP to price windows
        self.price_20m_win.add(timestamp, ltp)
        self.price_60m_win.add(timestamp, ltp)

        # Add LTQ to dynamics windows
        self.ltq_2m_win.add(timestamp, ltq)
        self.ltq_5m_win.add(timestamp, ltq)

        avg_p_20m = self.price_20m_win.get_average(timestamp) or ltp
        avg_p_60m = self.price_60m_win.get_average(timestamp) or ltp

        ltq_2m = self.ltq_2m_win.get_average(timestamp)
        ltq_5m = self.ltq_5m_win.get_average(timestamp)

        ratio = (ltq_2m / ltq_5m) if ltq_5m > 0 else 1.0

        return ETQResult(
            symbol="",
            etq_5m=int(self.etq_5m_win.get_sum(timestamp)),
            etq_20m=int(self.etq_20m_win.get_sum(timestamp)),
            etq_60m=int(self.etq_60m_win.get_sum(timestamp)),
            avg_price_20m=round(avg_p_20m, 2),
            avg_price_60m=round(avg_p_60m, 2),
            ltq_2m_avg=round(ltq_2m, 1),
            ltq_5m_avg=round(ltq_5m, 1),
            ltq_surge_ratio=round(ratio, 2)
        )

class ETQEngine:
    """
    Multi-symbol ETQ and Average Price Manager.
    """

    def __init__(self):
        self._trackers: Dict[str, ETQSingleTracker] = {}

    def update_tick(self, symbol: str, timestamp: float, ltp: float, ltq: int) -> ETQResult:
        if symbol not in self._trackers:
            self._trackers[symbol] = ETQSingleTracker()

        res = self._trackers[symbol].update(timestamp, ltp, ltq)
        res.symbol = symbol
        return res

    def get_result(self, symbol: str, timestamp: Optional[float] = None) -> Optional[ETQResult]:
        if symbol in self._trackers:
            ts = timestamp or time.time()
            tr = self._trackers[symbol]
            avg_p_20m = tr.price_20m_win.get_average(ts) or tr.latest_ltp
            avg_p_60m = tr.price_60m_win.get_average(ts) or tr.latest_ltp
            ltq_2m = tr.ltq_2m_win.get_average(ts)
            ltq_5m = tr.ltq_5m_win.get_average(ts)
            ratio = (ltq_2m / ltq_5m) if ltq_5m > 0 else 1.0

            return ETQResult(
                symbol=symbol,
                etq_5m=int(tr.etq_5m_win.get_sum(ts)),
                etq_20m=int(tr.etq_20m_win.get_sum(ts)),
                etq_60m=int(tr.etq_60m_win.get_sum(ts)),
                avg_price_20m=round(avg_p_20m, 2),
                avg_price_60m=round(avg_p_60m, 2),
                ltq_2m_avg=round(ltq_2m, 1),
                ltq_5m_avg=round(ltq_5m, 1),
                ltq_surge_ratio=round(ratio, 2)
            )
        return None
