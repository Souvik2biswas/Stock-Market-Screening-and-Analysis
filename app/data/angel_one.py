"""
Angel One SmartAPI Adapter Implementation.
"""
import json
import logging
import threading
import urllib.request
from typing import Callable, Dict, List, Optional
from app.data.broker_base import MarketDataAdapter, Quote, Tick

logger = logging.getLogger(__name__)

SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

DEFAULT_NSE_UNIVERSE = [
    "TATAMOTORS", "SBIN", "YESBANK", "IDEA", "ZOMATO", "PNB", "TATASTEEL", "ITC",
    "RELIANCE", "INFY", "HDFCBANK", "ICICIBANK", "AXISBANK", "BHARTIARTL", "TCS",
    "LT", "MARUTI", "SUNPHARMA", "WIPRO", "TITAN", "BAJFINANCE", "KOTAKBANK", "ONGC", "NTPC", "POWERGRID"
]

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
        self._feed_token = ""
        self._jwt_token = ""
        self._ws = None
        self._token_map: Dict[str, str] = {}    # symbol -> token
        self._symbol_map: Dict[str, str] = {}   # token -> symbol
        self._tick_callback: Optional[Callable[[Tick], None]] = None

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
                self._feed_token = data.get("data", {}).get("feedToken", "")
                self._jwt_token = data.get("data", {}).get("jwtToken", "")
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
        if self._ws:
            try:
                self._ws.close_connection()
            except Exception:
                pass
            self._ws = None

        if self._smart_api:
            try:
                self._smart_api.terminateSession(self.client_code)
            except Exception:
                pass

    def is_connected(self) -> bool:
        return self._connected

    def get_symbol_universe(self) -> List[str]:
        """
        Dynamically fetches and parses the official Angel One Scrip Master JSON for all NSE equities.
        Falls back to representative 25-stock shortlist if offline.
        """
        try:
            req = urllib.request.Request(SCRIP_MASTER_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    raw_data = json.loads(resp.read().decode('utf-8'))
                    symbols = []
                    for row in raw_data:
                        if row.get("exch_seg") == "NSE":
                            raw_sym = row.get("symbol", "")
                            name = row.get("name", "")
                            token = row.get("token", "")
                            if raw_sym.endswith("-EQ") or row.get("instrumenttype") in ["", "EQ"]:
                                sym = name.strip() if (name and not name.endswith("-EQ")) else raw_sym.replace("-EQ", "").strip()
                                if sym and sym not in self._token_map:
                                    self._token_map[sym] = token
                                    self._symbol_map[token] = sym
                                    symbols.append(sym)
                    if symbols:
                        logger.info(f"Loaded {len(symbols)} NSE equity scrips from Angel One Scrip Master.")
                        return symbols
        except Exception as e:
            logger.warning(f"Could not load remote Angel One Scrip Master ({e}). Using standard shortlist.")

        # Fallback shortlist
        for sym in DEFAULT_NSE_UNIVERSE:
            self._token_map[sym] = sym
            self._symbol_map[sym] = sym
        return DEFAULT_NSE_UNIVERSE

    def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        quotes = {}
        if not self._connected or not self._smart_api:
            return quotes

        try:
            mode = "FULL"
            tokens = [self._token_map.get(s, s) for s in symbols]
            response = self._smart_api.getMarketData(mode, {"NSE": tokens})
            if response.get("status") and "fetched" in response.get("data", {}):
                for item in response["data"]["fetched"]:
                    sym = item.get("tradingSymbol", "").replace("-EQ", "")
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
        self._tick_callback = callback
        logger.info(f"Subscribed {len(symbols)} symbols on Angel One WebSocket feed.")

        if not self._connected or not self._jwt_token:
            return

        try:
            from SmartApi.smartWebSocketV2 import SmartWebSocketV2

            tokens = [self._token_map.get(s, s) for s in symbols]
            token_list = [{"exchangeType": 1, "tokens": tokens}]  # 1 = NSE Equity

            def on_data(wsapp, message):
                if self._tick_callback and isinstance(message, dict):
                    token = str(message.get("token", ""))
                    sym = self._symbol_map.get(token, token)
                    tick = Tick(
                        symbol=sym,
                        ltp=float(message.get("last_traded_price", 0.0)) / 100.0,
                        ltq=int(message.get("last_traded_quantity", 0)),
                        volume=int(message.get("volume_trade_for_the_day", 0)),
                        bid_price=float(message.get("best_bid_price", 0.0)) / 100.0,
                        bid_qty=int(message.get("best_bid_quantity", 0)),
                        ask_price=float(message.get("best_ask_price", 0.0)) / 100.0,
                        ask_qty=int(message.get("best_ask_quantity", 0))
                    )
                    self._tick_callback(tick)

            def on_open(wsapp):
                logger.info("Angel One SmartWebSocketV2 opened. Subscribing tokens...")
                sws.subscribe("correlation_id", 1, token_list)  # Mode 1 = Ticks

            def on_error(wsapp, error):
                logger.error(f"Angel One SmartWebSocketV2 error: {error}")

            def on_close(wsapp):
                logger.info("Angel One SmartWebSocketV2 connection closed.")

            sws = SmartWebSocketV2(self._jwt_token, self.api_key, self.client_code, self._feed_token)
            sws.on_data = on_data
            sws.on_open = on_open
            sws.on_error = on_error
            sws.on_close = on_close

            ws_thread = threading.Thread(target=sws.connect, daemon=True)
            ws_thread.start()
            self._ws = sws

        except Exception as e:
            logger.error(f"Could not initialize Angel One SmartWebSocketV2: {e}")

    def unsubscribe_ticks(self, symbols: List[str]) -> None:
        if self._ws:
            try:
                tokens = [self._token_map.get(s, s) for s in symbols]
                token_list = [{"exchangeType": 1, "tokens": tokens}]
                self._ws.unsubscribe("correlation_id", 1, token_list)
            except Exception as e:
                logger.error(f"Error unsubscribing Angel One ticks: {e}")

