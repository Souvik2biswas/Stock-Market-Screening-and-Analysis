"""
Abstract Broker API Interface and Unified Data Models.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import time

@dataclass
class MarketDepth:
    bid_price: float
    bid_qty: int
    ask_price: float
    ask_qty: int

@dataclass
class Quote:
    symbol: str
    ltp: float
    bid_price: float
    bid_qty: int
    ask_price: float
    ask_qty: int
    volume: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class Tick:
    symbol: str
    ltp: float
    ltq: int
    volume: int
    bid_price: float
    bid_qty: int
    ask_price: float
    ask_qty: int
    timestamp: float = field(default_factory=time.time)

class MarketDataAdapter(ABC):
    """
    Abstract Interface for Broker Integrations (Angel One / Fyers / Mock)
    """

    @abstractmethod
    def connect(self) -> bool:
        """Initialize connection/session with the broker API."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Gracefully disconnect sessions and WebSocket streams."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if broker feed connection is active."""
        pass

    @abstractmethod
    def get_symbol_universe(self) -> List[str]:
        """Fetch list of all NSE-listed equity symbols."""
        pass

    @abstractmethod
    def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        """Fetch REST snapshot quotes for a batch of symbols."""
        pass

    @abstractmethod
    def subscribe_ticks(self, symbols: List[str], callback: Callable[[Tick], None]) -> None:
        """Subscribe to live tick updates for the given shortlist symbols."""
        pass

    @abstractmethod
    def unsubscribe_ticks(self, symbols: List[str]) -> None:
        """Unsubscribe from live tick updates."""
        pass
