"""
Stock Price & Liquidity Screener Module.
Filters NSE-listed stocks by LTP (₹30-₹500) and top-of-book depth (>10L Bid/Ask Qty).
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple
from app.config import MIN_LTP, MAX_LTP, MIN_BID_QTY, MIN_ASK_QTY
from app.data.broker_base import Quote, Tick

@dataclass
class ScreeningResult:
    symbol: str
    ltp: float
    bid_qty: int
    ask_qty: int
    passes_price: bool
    passes_liquidity: bool
    is_screened_in: bool
    reason: str

class StockScreener:
    """
    Two-Stage Stock Screener & Filter.
    """

    def __init__(self, min_ltp: float = MIN_LTP, max_ltp: float = MAX_LTP, min_bid_qty: int = MIN_BID_QTY, min_ask_qty: int = MIN_ASK_QTY):
        self.min_ltp = min_ltp
        self.max_ltp = max_ltp
        self.min_bid_qty = min_bid_qty
        self.min_ask_qty = min_ask_qty

    def evaluate_quote(self, quote: Quote) -> ScreeningResult:
        passes_price = self.min_ltp <= quote.ltp <= self.max_ltp
        passes_liquidity = (quote.bid_qty > self.min_bid_qty) and (quote.ask_qty > self.min_ask_qty)
        is_screened_in = passes_price and passes_liquidity

        reasons = []
        if not passes_price:
            reasons.append(f"LTP ₹{quote.ltp} out of range [₹{self.min_ltp}-₹{self.max_ltp}]")
        if quote.bid_qty <= self.min_bid_qty:
            reasons.append(f"Bid Qty {quote.bid_qty:,} ≤ 10,00,000")
        if quote.ask_qty <= self.min_ask_qty:
            reasons.append(f"Ask Qty {quote.ask_qty:,} ≤ 10,00,000")

        reason_str = "PASSED: All filters met" if is_screened_in else "FAILED: " + ", ".join(reasons)

        return ScreeningResult(
            symbol=quote.symbol,
            ltp=quote.ltp,
            bid_qty=quote.bid_qty,
            ask_qty=quote.ask_qty,
            passes_price=passes_price,
            passes_liquidity=passes_liquidity,
            is_screened_in=is_screened_in,
            reason=reason_str
        )

    def evaluate_tick(self, tick: Tick) -> ScreeningResult:
        passes_price = self.min_ltp <= tick.ltp <= self.max_ltp
        passes_liquidity = (tick.bid_qty > self.min_bid_qty) and (tick.ask_qty > self.min_ask_qty)
        is_screened_in = passes_price and passes_liquidity

        reasons = []
        if not passes_price:
            reasons.append(f"LTP ₹{tick.ltp} out of range [₹{self.min_ltp}-₹{self.max_ltp}]")
        if tick.bid_qty <= self.min_bid_qty:
            reasons.append(f"Bid Qty {tick.bid_qty:,} ≤ 10,00,000")
        if tick.ask_qty <= self.min_ask_qty:
            reasons.append(f"Ask Qty {tick.ask_qty:,} ≤ 10,00,000")

        reason_str = "PASSED: All filters met" if is_screened_in else "FAILED: " + ", ".join(reasons)

        return ScreeningResult(
            symbol=tick.symbol,
            ltp=tick.ltp,
            bid_qty=tick.bid_qty,
            ask_qty=tick.ask_qty,
            passes_price=passes_price,
            passes_liquidity=passes_liquidity,
            is_screened_in=is_screened_in,
            reason=reason_str
        )

    def screen_universe(self, quotes: Dict[str, Quote]) -> Tuple[List[str], List[ScreeningResult]]:
        shortlist = []
        results = []
        for sym, q in quotes.items():
            res = self.evaluate_quote(q)
            results.append(res)
            if res.is_screened_in:
                shortlist.append(sym)
        return shortlist, results
