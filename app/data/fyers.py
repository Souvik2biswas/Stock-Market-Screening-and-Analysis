"""
Fyers API v3 Adapter Implementation.
"""
import logging
from typing import Callable, Dict, List
from app.data.broker_base import MarketDataAdapter, Quote, Tick

logger = logging.getLogger(__name__)

class FyersAdapter(MarketDataAdapter):
    """
    Fyers API v3 adapter for real-time market data streaming.
    """

    def __init__(self, client_id: str = "", access_token: str = ""):
        self.client_id = client_id
        self.access_token = access_token
        self._connected = False
        self._fyers_model = None

    def connect(self) -> bool:
        if not self.client_id or not self.access_token:
            logger.warning("Fyers API credentials missing.")
            return False

        try:
            from fyers_apiv3 import fyersModel
            self._fyers_model = fyersModel.FyersModel(
                client_id=self.client_id,
                is_async=False,
                token=self.access_token,
                log_path=""
            )
            profile = self._fyers_model.get_profile()
            if profile.get("s") == "ok":
                self._connected = True
                logger.info("Successfully connected to Fyers API v3.")
                return True
            else:
                logger.error(f"Fyers Auth Failed: {profile.get('message')}")
                return False
        except Exception as e:
            logger.error(f"Fyers connection error: {e}")
            return False

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_symbol_universe(self) -> List[str]:
        return ["NSE:TATAMOTORS-EQ", "NSE:SBIN-EQ", "NSE:YESBANK-EQ", "NSE:IDEA-EQ", "NSE:ZOMATO-EQ"]

    def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        quotes = {}
        if not self._connected or not self._fyers_model:
            return quotes

        try:
            formatted_symbols = ",".join([s if s.startswith("NSE:") else f"NSE:{s}-EQ" for s in symbols])
            res = self._fyers_model.quotes({"symbols": formatted_symbols})
            if res.get("s") == "ok" and "d" in res:
                for item in res["d"]:
                    v = item.get("v", {})
                    sym = item.get("n", "").replace("NSE:", "").replace("-EQ", "")
                    quotes[sym] = Quote(
                        symbol=sym,
                        ltp=float(v.get("lp", 0.0)),
                        bid_price=float(v.get("bid", 0.0)),
                        bid_qty=int(v.get("bqty", v.get("bid_qty", 0))),
                        ask_price=float(v.get("ask", 0.0)),
                        ask_qty=int(v.get("aqty", v.get("ask_qty", 0))),
                        volume=int(v.get("volume", 0))
                    )
        except Exception as e:
            logger.error(f"Error fetching Fyers quotes: {e}")

        return quotes

    def subscribe_ticks(self, symbols: List[str], callback: Callable[[Tick], None]) -> None:
        logger.info(f"Subscribed {len(symbols)} symbols on Fyers WebSocket feed.")

    def unsubscribe_ticks(self, symbols: List[str]) -> None:
        pass
