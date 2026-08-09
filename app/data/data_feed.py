"""
Central Data Feed Manager for Broker Selection and Tick Aggregation.
"""
import logging
from typing import Callable, Dict, List, Optional
from app.config import DEFAULT_MODE
from app.data.broker_base import MarketDataAdapter, Quote, Tick
from app.data.mock_broker import MockBrokerAdapter
from app.data.angel_one import AngelOneAdapter
from app.data.fyers import FyersAdapter

logger = logging.getLogger(__name__)

class DataFeedManager:
    """
    Manages active broker feed, tick callbacks, and quote aggregation.
    """

    def __init__(self, mode: str = DEFAULT_MODE, credentials: Optional[dict] = None):
        self.mode = mode
        self.credentials = credentials or {}
        self.adapter: MarketDataAdapter = self._create_adapter(mode, self.credentials)
        self._tick_listeners: List[Callable[[Tick], None]] = []
        self._price_histories: Dict[str, List[float]] = {}

    def _create_adapter(self, mode: str, creds: dict) -> MarketDataAdapter:
        if mode == "ANGEL_ONE":
            return AngelOneAdapter(
                api_key=creds.get("angel_api_key", ""),
                client_code=creds.get("angel_client_code", ""),
                password=creds.get("angel_password", ""),
                totp_secret=creds.get("angel_totp_secret", "")
            )
        elif mode == "FYERS":
            return FyersAdapter(
                client_id=creds.get("fyers_client_id", ""),
                access_token=creds.get("fyers_access_token", "")
            )
        else:
            return MockBrokerAdapter()

    def set_mode(self, mode: str, credentials: Optional[dict] = None) -> bool:
        if self.adapter:
            self.adapter.disconnect()

        self.mode = mode
        self.credentials = credentials or {}
        self.adapter = self._create_adapter(mode, self.credentials)
        self._price_histories.clear()
        connected = self.adapter.connect()
        logger.info(f"Switched data feed mode to {mode}. Connection status: {connected}")
        return connected

    def start(self) -> bool:
        return self.adapter.connect()

    def stop(self) -> None:
        if self.adapter:
            self.adapter.disconnect()

    def add_tick_listener(self, callback: Callable[[Tick], None]) -> None:
        if callback not in self._tick_listeners:
            self._tick_listeners.append(callback)

    def remove_tick_listener(self, callback: Callable[[Tick], None]) -> None:
        if callback in self._tick_listeners:
            self._tick_listeners.remove(callback)

    def _on_tick(self, tick: Tick) -> None:
        if tick.symbol not in self._price_histories:
            self._price_histories[tick.symbol] = []
        self._price_histories[tick.symbol].append(tick.ltp)
        if len(self._price_histories[tick.symbol]) > 500:
            self._price_histories[tick.symbol].pop(0)

        for listener in self._tick_listeners:
            try:
                listener(tick)
            except Exception as e:
                logger.error(f"Error in tick listener: {e}")

    def get_symbol_universe(self) -> List[str]:
        return self.adapter.get_symbol_universe()

    def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        quotes = self.adapter.get_bulk_quotes(symbols)
        for sym, q in quotes.items():
            if sym not in self._price_histories:
                self._price_histories[sym] = [q.ltp]
        return quotes

    def get_price_histories(self, symbols: Optional[List[str]] = None) -> Dict[str, List[float]]:
        if symbols:
            return {s: self._price_histories.get(s, []) for s in symbols}
        return self._price_histories.copy()

    def subscribe_shortlist(self, symbols: List[str]) -> None:
        self.adapter.subscribe_ticks(symbols, self._on_tick)
