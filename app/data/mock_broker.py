"""
High-Fidelity Mock Live Market Tick and Depth Simulator.
Simulates real-time NSE market data, order book dynamics, volume bursts, and SMMA crossovers.
"""
import random
import threading
import time
from typing import Callable, Dict, List
from app.config import MOCK_STOCK_UNIVERSE
from app.data.broker_base import MarketDataAdapter, Quote, Tick

class MockBrokerAdapter(MarketDataAdapter):
    """
    Simulates live market feeds for testing, demo recording, and offline usage.
    """

    def __init__(self):
        self._connected = False
        self._subscribed_symbols: List[str] = []
        self._callback: Callable[[Tick], None] = None
        self._streaming_thread: threading.Thread = None
        self._stop_event = threading.Event()

        # Initialize symbol state: price, volume, depth, smma trend state
        self._symbols_state: Dict[str, dict] = {}
        self._init_states()

    def _init_states(self):
        for item in MOCK_STOCK_UNIVERSE:
            sym = item["symbol"]
            base_ltp = item["base_ltp"]
            
            # Generate high bid/ask quantities (some >10L, some <10L for screening tests)
            # Make popular high volume stocks exceed 10L liquidity threshold
            high_liquidity_stocks = {"TATAMOTORS", "SBIN", "YESBANK", "IDEA", "ZOMATO", "PNB", "TATASTEEL", "ITC", "SUZLON", "IRFC", "BHEL"}
            if sym in high_liquidity_stocks:
                bid_qty = random.randint(1200000, 3500000)
                ask_qty = random.randint(1100000, 3200000)
            else:
                bid_qty = random.randint(300000, 950000)
                ask_qty = random.randint(400000, 980000)

            spread = round(base_ltp * 0.0005, 2)
            if spread < 0.05:
                spread = 0.05

            self._symbols_state[sym] = {
                "company": item["company"],
                "ltp": base_ltp,
                "bid_price": round(base_ltp - spread/2, 2),
                "bid_qty": bid_qty,
                "ask_price": round(base_ltp + spread/2, 2),
                "ask_qty": ask_qty,
                "volume": random.randint(5000000, 20000000),
                "trend": random.choice([-1, 1]),
                "trend_ticks_left": random.randint(10, 30),
                "ltq": random.randint(100, 5000)
            }

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False
        self._stop_event.set()
        if self._streaming_thread and self._streaming_thread.is_alive():
            self._streaming_thread.join(timeout=2.0)

    def is_connected(self) -> bool:
        return self._connected

    def get_symbol_universe(self) -> List[str]:
        return [item["symbol"] for item in MOCK_STOCK_UNIVERSE]

    def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        quotes = {}
        now = time.time()
        for sym in symbols:
            if sym in self._symbols_state:
                st = self._symbols_state[sym]
                quotes[sym] = Quote(
                    symbol=sym,
                    ltp=st["ltp"],
                    bid_price=st["bid_price"],
                    bid_qty=st["bid_qty"],
                    ask_price=st["ask_price"],
                    ask_qty=st["ask_qty"],
                    volume=st["volume"],
                    timestamp=now
                )
        return quotes

    def subscribe_ticks(self, symbols: List[str], callback: Callable[[Tick], None]) -> None:
        self._subscribed_symbols = list(set(symbols))
        self._callback = callback

        if not self._streaming_thread or not self._streaming_thread.is_alive():
            self._stop_event.clear()
            self._streaming_thread = threading.Thread(target=self._run_stream, daemon=True)
            self._streaming_thread.start()

    def unsubscribe_ticks(self, symbols: List[str]) -> None:
        self._subscribed_symbols = [s for s in self._subscribed_symbols if s not in symbols]

    def _run_stream(self):
        """Simulate real-time tick streaming loop."""
        while not self._stop_event.is_set() and self._connected:
            if not self._subscribed_symbols:
                time.sleep(0.5)
                continue

            # Pick a subset of subscribed symbols to update per tick slice
            active_batch = random.sample(
                self._subscribed_symbols,
                min(len(self._subscribed_symbols), max(3, len(self._subscribed_symbols) // 2))
            )

            now = time.time()
            for sym in active_batch:
                st = self._symbols_state[sym]

                # Update trend drift
                st["trend_ticks_left"] -= 1
                if st["trend_ticks_left"] <= 0:
                    st["trend"] = random.choice([-1, 1])
                    st["trend_ticks_left"] = random.randint(15, 40)

                # Calculate price change
                volatility = st["ltp"] * 0.0015
                change = (st["trend"] * volatility * 0.6) + random.gauss(0, volatility * 0.4)
                new_ltp = round(max(10.0, st["ltp"] + change), 2)
                st["ltp"] = new_ltp

                # Simulate LTQ volume burst occasionally
                is_surge = random.random() < 0.12
                if is_surge:
                    ltq = random.randint(25000, 150000)
                else:
                    ltq = random.randint(500, 8000)

                st["ltq"] = ltq
                st["volume"] += ltq

                # Update order book depth
                spread = round(max(0.05, new_ltp * 0.0004), 2)
                st["bid_price"] = round(new_ltp - spread / 2, 2)
                st["ask_price"] = round(new_ltp + spread / 2, 2)

                # Fluctuate bid/ask quantities
                st["bid_qty"] = max(10000, st["bid_qty"] + random.randint(-50000, 50000))
                st["ask_qty"] = max(10000, st["ask_qty"] + random.randint(-50000, 50000))

                tick = Tick(
                    symbol=sym,
                    ltp=new_ltp,
                    ltq=ltq,
                    volume=st["volume"],
                    bid_price=st["bid_price"],
                    bid_qty=st["bid_qty"],
                    ask_price=st["ask_price"],
                    ask_qty=st["ask_qty"],
                    timestamp=now
                )

                if self._callback:
                    try:
                        self._callback(tick)
                    except Exception as e:
                        logger.error(f"Error in mock broker tick callback: {e}")

            time.sleep(0.3)  # Tick streaming interval
