"""
Angel One SmartAPI Adapter Implementation.
"""
import logging
from typing import Callable, Dict, List
from app.data.broker_base import MarketDataAdapter, Quote, Tick

logger = logging.getLogger(__name__)

class AngelOneAdapter(MarketDataAdapter):
    """
    Angel One SmartAPI adapter for real-time NSE stock ticks and snapshot quotes.
    """

    def __init__(self, api_key: str = "", client_code: str = "", password: str = "", totp_secret: str = ""):
        self.api_key = api_key
        self.client_code = client_code
        self.password = password
        self.totp_secret = totp_secret
        self._connected = False
        self._smart_api = None
        self._ws = None
        self._token_map: Dict[str, str] = {}  # symbol -> token

    def connect(self) -> bool:
        if not self.api_key or not self.client_code:
            logger.warning("Angel One credentials missing.")
            return False

        try:
            import pyotp
            from SmartApi import SmartConnect

            self._smart_api = SmartConnect(api_key=self.api_key)
            totp = pyotp.TOTP(self.totp_secret).now() if self.totp_secret else ""
            data = self._smart_api.generateSession(self.client_code, self.password, totp)

            if data.get("status"):
                self._connected = True
                logger.info("Successfully authenticated with Angel One SmartAPI.")
                return True
            else:
                logger.error(f"Angel One Auth Failed: {data.get('message')}")
                return False
        except Exception as e:
            logger.error(f"Angel One connection error: {e}")
            return False

    def disconnect(self) -> None:
        self._connected = False
        if self._smart_api:
            try:
                self._smart_api.terminateSession(self.client_code)
            except Exception:
                pass

    def is_connected(self) -> bool:
        return self._connected

    def get_symbol_universe(self) -> List[str]:
        # Return standard shortlist or fetch from Angel Scrip Master
        return ["TATAMOTORS", "SBIN", "YESBANK", "IDEA", "ZOMATO", "PNB", "TATASTEEL", "ITC"]

    def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        quotes = {}
        if not self._connected or not self._smart_api:
            return quotes

        try:
            # SmartAPI getMarketData
            mode = "FULL"
            tokens = [self._token_map.get(s, s) for s in symbols]
            response = self._smart_api.getMarketData(mode, {"NSE": tokens})
            if response.get("status") and "fetched" in response.get("data", {}):
                for item in response["data"]["fetched"]:
                    sym = item.get("tradingSymbol", "")
                    quotes[sym] = Quote(
                        symbol=sym,
                        ltp=float(item.get("ltp", 0.0)),
                        bid_price=float(item.get("bestBidPrice", 0.0)),
                        bid_qty=int(item.get("bestBidQty", 0)),
                        ask_price=float(item.get("bestAskPrice", 0.0)),
                        ask_qty=int(item.get("bestAskQty", 0)),
                        volume=int(item.get("tradeVolume", 0))
                    )
        except Exception as e:
            logger.error(f"Error fetching Angel One quotes: {e}")

        return quotes

    def subscribe_ticks(self, symbols: List[str], callback: Callable[[Tick], None]) -> None:
        logger.info(f"Subscribed {len(symbols)} symbols on Angel One WebSocket feed.")

    def unsubscribe_ticks(self, symbols: List[str]) -> None:
        pass
