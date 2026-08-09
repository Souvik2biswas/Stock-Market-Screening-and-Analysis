"""
Quantitative Feature Extraction Engine for SMMA Crossover Evaluation.
Converts real-time market data ticks and indicators into numerical ML vectors.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any
from app.data.broker_base import Tick
from app.indicators.smma import SMMAResult
from app.indicators.etq_engine import ETQResult

@dataclass
class CrossoverFeatures:
    symbol: str
    signal: str                # "BUY" or "SELL"
    ltp: float
    ltq_surge_ratio: float     # LTQ 2m avg / LTQ 5m avg
    bid_ask_qty_ratio: float   # Bid Qty / Ask Qty
    etq_acceleration: float    # 5m ETQ normalized vs 20m ETQ rate
    smma_spread_pct: float     # abs(SMMA20 - SMMA120) / SMMA120 * 100
    price_vs_avg20_pct: float  # (LTP - AvgPrice20m) / AvgPrice20m * 100
    spread_pct: float          # (Ask - Bid) / LTP * 100
    signal_type_num: int       # 1 for BUY, 0 for SELL

    def to_feature_vector(self) -> list[float]:
        """Returns ordered list of feature values for sklearn model input."""
        return [
            self.ltq_surge_ratio,
            self.bid_ask_qty_ratio,
            self.etq_acceleration,
            self.smma_spread_pct,
            self.price_vs_avg20_pct,
            self.spread_pct,
            self.signal_type_num
        ]

    @staticmethod
    def feature_names() -> list[str]:
        return [
            "ltq_surge_ratio",
            "bid_ask_qty_ratio",
            "etq_acceleration",
            "smma_spread_pct",
            "price_vs_avg20_pct",
            "spread_pct",
            "signal_type_num"
        ]

class FeatureExtractor:
    """
    Extracts Quantitative Features at the instant an SMMA Crossover is detected.
    """

    @staticmethod
    def extract(tick: Tick, smma_res: SMMAResult, etq_res: ETQResult) -> CrossoverFeatures:
        ltp = tick.ltp
        signal = smma_res.signal

        # 1. LTQ Surge Ratio
        ltq_surge = etq_res.ltq_surge_ratio if etq_res else 1.0

        # 2. Bid/Ask Quantity Ratio
        bid_qty = max(1, tick.bid_qty)
        ask_qty = max(1, tick.ask_qty)
        bid_ask_ratio = round(bid_qty / ask_qty, 2)

        # 3. ETQ Execution Acceleration (5m vs 20m pace)
        etq_5m = etq_res.etq_5m if etq_res else 0
        etq_20m = etq_res.etq_20m if etq_res else 0
        expected_5m_from_20m = max(1.0, etq_20m / 4.0)
        etq_acc = round(etq_5m / expected_5m_from_20m, 2)

        # 4. SMMA Spread Percentage
        smma_fast = smma_res.smma_fast
        smma_slow = max(0.01, smma_res.smma_slow)
        smma_spread_pct = round(abs(smma_fast - smma_slow) / smma_slow * 100.0, 3)

        # 5. Price vs 20m Average Price Percentage
        avg_20m = etq_res.avg_price_20m if (etq_res and etq_res.avg_price_20m > 0) else ltp
        price_vs_avg20 = round((ltp - avg_20m) / avg_20m * 100.0, 3)

        # 6. Bid-Ask Spread Percentage
        ask_price = tick.ask_price
        bid_price = tick.bid_price
        spread_pct = round((ask_price - bid_price) / max(0.01, ltp) * 100.0, 3)

        # 7. Signal Type Numeric (1 for BUY, 0 for SELL)
        sig_num = 1 if signal == "BUY" else 0

        return CrossoverFeatures(
            symbol=tick.symbol,
            signal=signal,
            ltp=ltp,
            ltq_surge_ratio=ltq_surge,
            bid_ask_qty_ratio=bid_ask_ratio,
            etq_acceleration=etq_acc,
            smma_spread_pct=smma_spread_pct,
            price_vs_avg20_pct=price_vs_avg20,
            spread_pct=spread_pct,
            signal_type_num=sig_num
        )
