"""
SMMA (Smoothed Moving Average) Indicator Engine.
Computes streaming SMMA(20) and SMMA(120) and detects Buy/Sell crossovers.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from app.config import SMMA_SHORT_PERIOD, SMMA_LONG_PERIOD

@dataclass
class SMMAResult:
    symbol: str
    smma_fast: float   # SMMA (20)
    smma_slow: float   # SMMA (120)
    signal: str        # "BUY", "SELL", "NONE"
    is_crossover: bool # True if a crossover occurred on the current tick

class SMMASingleTracker:
    """
    Tracks SMMA for a single symbol over ticks/bars.
    """

    def __init__(self, fast_period: int = SMMA_SHORT_PERIOD, slow_period: int = SMMA_LONG_PERIOD):
        self.fast_period = fast_period
        self.slow_period = slow_period

        self.fast_prices: List[float] = []
        self.slow_prices: List[float] = []

        self.prev_fast_smma: Optional[float] = None
        self.prev_slow_smma: Optional[float] = None

        self.current_fast_smma: Optional[float] = None
        self.current_slow_smma: Optional[float] = None

        self.prev_signal: str = "NONE"

    def update(self, price: float) -> SMMAResult:
        # Update Fast SMMA (20)
        if self.prev_fast_smma is None:
            self.fast_prices.append(price)
            if len(self.fast_prices) >= self.fast_period:
                self.current_fast_smma = sum(self.fast_prices[-self.fast_period:]) / self.fast_period
                self.prev_fast_smma = self.current_fast_smma
            else:
                self.current_fast_smma = price
        else:
            self.current_fast_smma = (self.prev_fast_smma * (self.fast_period - 1) + price) / self.fast_period
            self.prev_fast_smma = self.current_fast_smma

        # Update Slow SMMA (120)
        if self.prev_slow_smma is None:
            self.slow_prices.append(price)
            if len(self.slow_prices) >= self.slow_period:
                self.current_slow_smma = sum(self.slow_prices[-self.slow_period:]) / self.slow_period
                self.prev_slow_smma = self.current_slow_smma
            else:
                # Fast warm-up interpolation if < 120 ticks available
                self.current_slow_smma = sum(self.slow_prices) / len(self.slow_prices)
        else:
            self.current_slow_smma = (self.prev_slow_smma * (self.slow_period - 1) + price) / self.slow_period
            self.prev_slow_smma = self.current_slow_smma

        # Detect Crossover Signal
        current_signal = "NONE"
        is_crossover = False

        if self.current_fast_smma is not None and self.current_slow_smma is not None:
            if self.current_fast_smma > self.current_slow_smma:
                current_signal = "BUY"
            elif self.current_fast_smma < self.current_slow_smma:
                current_signal = "SELL"

            # Check if signal flipped from previous tick
            if self.prev_signal != "NONE" and current_signal != self.prev_signal and current_signal != "NONE":
                is_crossover = True

            self.prev_signal = current_signal

        return SMMAResult(
            symbol="",
            smma_fast=round(self.current_fast_smma or price, 2),
            smma_slow=round(self.current_slow_smma or price, 2),
            signal=current_signal,
            is_crossover=is_crossover
        )

class SMMAEngine:
    """
    Multi-symbol SMMA Engine.
    """

    def __init__(self, fast_period: int = SMMA_SHORT_PERIOD, slow_period: int = SMMA_LONG_PERIOD):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self._trackers: Dict[str, SMMASingleTracker] = {}

    def update_tick(self, symbol: str, price: float) -> SMMAResult:
        if symbol not in self._trackers:
            self._trackers[symbol] = SMMASingleTracker(self.fast_period, self.slow_period)

        res = self._trackers[symbol].update(price)
        res.symbol = symbol
        return res

    def get_result(self, symbol: str) -> Optional[SMMAResult]:
        if symbol in self._trackers:
            tr = self._trackers[symbol]
            if tr.current_fast_smma is not None and tr.current_slow_smma is not None:
                return SMMAResult(
                    symbol=symbol,
                    smma_fast=round(tr.current_fast_smma, 2),
                    smma_slow=round(tr.current_slow_smma, 2),
                    signal=tr.prev_signal,
                    is_crossover=False
                )
        return None
