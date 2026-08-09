"""
Main Live Dashboard Application Window (PyQt6).
Integrates real-time screening, technical indicators, ETQ tracking, AI ML analysis, and chart visualization.
"""
import time
import logging
from typing import Dict, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QToolBar,
    QPushButton, QLabel, QFrame, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QColor

from app.config import DEFAULT_MODE, UI_REFRESH_INTERVAL_MS
from app.data.data_feed import DataFeedManager
from app.data.broker_base import Tick, Quote
from app.indicators.screener import StockScreener
from app.indicators.smma import SMMAEngine, SMMAResult
from app.indicators.etq_engine import ETQEngine, ETQResult
from app.ml.feature_extractor import FeatureExtractor, CrossoverFeatures
from app.ml.model import SignalPredictor, PredictionResult
from app.ml.explainer import AIExplainer

from app.ui.styles import DARK_THEME_QSS
from app.ui.components.metric_cards import MetricCardsBar
from app.ui.components.stock_table import StockTableView
from app.ui.components.ai_drawer import AIDrawerPanel
from app.ui.components.chart_widget import SMMAChartWidget
from app.ui.settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)

class TickSignalBridge(QObject):
    tick_received = pyqtSignal(object)

class LiveDashboardWindow(QMainWindow):
    """
    Main Stock Market Screening and AI Analysis System Window.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI/ML Stock Market Screener & Analysis System (NSE Live)")
        self.resize(1440, 900)
        self.setStyleSheet(DARK_THEME_QSS)

        # Core Engines
        self.feed_manager = DataFeedManager(mode=DEFAULT_MODE)
        self.screener = StockScreener()
        self.smma_engine = SMMAEngine()
        self.etq_engine = ETQEngine()
        self.ml_predictor = SignalPredictor()

        # Thread Bridge for Safe Qt UI updates from tick callbacks
        self.bridge = TickSignalBridge()
        self.bridge.tick_received.connect(self._process_tick)

        # State Data Structures
        self.stock_data: Dict[str, dict] = {}
        self.shortlist: List[str] = []
        self.selected_symbol: str = ""
        self.trades_history: Dict[str, list] = {}  # symbol -> list of trade dicts
        self.active_trades: Dict[str, dict] = {}    # symbol -> current open trade dict

        # Build User Interface
        self._init_ui()

        # Register Tick Listener & Connect Feed
        self.feed_manager.add_tick_listener(lambda t: self.bridge.tick_received.emit(t))
        self._start_feed()

        # QTimer for automatic UI Table Refresh
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_ui_table)
        self.refresh_timer.start(UI_REFRESH_INTERVAL_MS)

    def _init_ui(self):
        # 1. Top Toolbar
        toolbar = QToolBar("Main Controls")
        self.addToolBar(toolbar)

        self.btn_settings = QPushButton("⚙ Broker Settings")
        self.btn_settings.clicked.connect(self._open_settings)
        toolbar.addWidget(self.btn_settings)

        self.btn_refresh_screen = QPushButton("🔍 Re-Screen Universe")
        self.btn_refresh_screen.clicked.connect(self._perform_screening)
        toolbar.addWidget(self.btn_refresh_screen)

        self.lbl_feed_status = QLabel(f" Feed: {DEFAULT_MODE} (CONNECTED) ")
        self.lbl_feed_status.setStyleSheet("color: #a6e3a1; font-weight: bold; margin-left: 15px;")
        toolbar.addWidget(self.lbl_feed_status)

        # 2. Main Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # 3. Top Metrics Cards Bar
        self.metrics_bar = MetricCardsBar()
        main_layout.addWidget(self.metrics_bar)

        # 4. Main Content Splitter (Left: Table, Right: AI Drawer & Chart Tabs)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Container (Stock Table Grid)
        self.table_view = StockTableView()
        self.table_view.stock_selected.connect(self._on_stock_selected)
        splitter.addWidget(self.table_view)

        # Right Container (Tabs: AI Drawer & Real-Time Chart)
        right_tab_widget = QTabWidget()

        self.ai_drawer = AIDrawerPanel()
        right_tab_widget.addTab(self.ai_drawer, "🤖 AI Analysis & Strategy")

        self.chart_widget = SMMAChartWidget()
        right_tab_widget.addTab(self.chart_widget, "📈 Live SMMA Chart")

        splitter.addWidget(right_tab_widget)
        splitter.setSizes([850, 590])  # Initial column width ratio

        main_layout.addWidget(splitter)

    def _start_feed(self):
        connected = self.feed_manager.start()
        if connected:
            self._perform_screening()

    def _perform_screening(self):
        universe = self.feed_manager.get_symbol_universe()
        quotes = self.feed_manager.get_bulk_quotes(universe)

        # Evaluate screening
        shortlist, results = self.screener.screen_universe(quotes)
        self.shortlist = shortlist

        for res in results:
            sym = res.symbol
            if sym not in self.stock_data:
                self.stock_data[sym] = {
                    "symbol": sym,
                    "ltp": res.ltp,
                    "bid_price": res.ltp * 0.9995,
                    "bid_qty": res.bid_qty,
                    "ask_price": res.ltp * 1.0005,
                    "ask_qty": res.ask_qty,
                    "smma_20": res.ltp,
                    "smma_120": res.ltp,
                    "signal": "NONE",
                    "etq_5m": 0,
                    "etq_20m": 0,
                    "etq_60m": 0,
                    "avg_price_20m": res.ltp,
                    "avg_price_60m": res.ltp,
                    "is_screened_in": res.is_screened_in,
                    "ai_decision": "STANDBY",
                    "ai_confidence": 0.0,
                    "ai_explanation": "Awaiting live crossover event.",
                    "ltq_surge": 1.0,
                    "bid_ask_ratio": 1.0,
                    "etq_acc": 1.0,
                    "smma_gap": 0.0,
                    "price_vs_20m": 0.0,
                    "trades": []
                }
            else:
                self.stock_data[sym]["is_screened_in"] = res.is_screened_in

        # Subscribe tick stream for shortlisted symbols
        self.feed_manager.subscribe_shortlist(self.shortlist)

        # Select first stock by default if none selected
        if not self.selected_symbol and self.shortlist:
            self._on_stock_selected(self.shortlist[0])

        self._refresh_ui_table()

    def _process_tick(self, tick: Tick):
        sym = tick.symbol
        if sym not in self.stock_data:
            return

        now = tick.timestamp
        ltp = tick.ltp
        ltq = tick.ltq

        # 1. Update Indicators & ETQ
        smma_res = self.smma_engine.update_tick(sym, ltp)
        etq_res = self.etq_engine.update_tick(sym, now, ltp, ltq)

        d = self.stock_data[sym]
        d["ltp"] = ltp
        d["bid_price"] = tick.bid_price
        d["bid_qty"] = tick.bid_qty
        d["ask_price"] = tick.ask_price
        d["ask_qty"] = tick.ask_qty

        d["smma_20"] = smma_res.smma_fast
        d["smma_120"] = smma_res.smma_slow
        d["signal"] = smma_res.signal

        d["etq_5m"] = etq_res.etq_5m
        d["etq_20m"] = etq_res.etq_20m
        d["etq_60m"] = etq_res.etq_60m

        d["avg_price_20m"] = etq_res.avg_price_20m
        d["avg_price_60m"] = etq_res.avg_price_60m

        d["ltq_surge"] = etq_res.ltq_surge_ratio
        d["bid_ask_ratio"] = round(tick.bid_qty / max(1, tick.ask_qty), 2)
        d["etq_acc"] = round(etq_res.etq_5m / max(1.0, etq_res.etq_20m / 4.0), 2)
        d["smma_gap"] = round(abs(smma_res.smma_fast - smma_res.smma_slow) / max(0.01, smma_res.smma_slow) * 100.0, 2)
        d["price_vs_20m"] = round((ltp - etq_res.avg_price_20m) / max(0.01, etq_res.avg_price_20m) * 100.0, 2)

        # Check screening compliance on live tick
        scr_res = self.screener.evaluate_tick(tick)
        d["is_screened_in"] = scr_res.is_screened_in

        # 2. Crossover Signal & AI Prediction Evaluation
        if smma_res.is_crossover and smma_res.signal in ["BUY", "SELL"]:
            features = FeatureExtractor.extract(tick, smma_res, etq_res)
            prediction = self.ml_predictor.predict(features)
            explanation = AIExplainer.explain(prediction)

            prediction.explanation = explanation
            d["ai_decision"] = prediction.decision
            d["ai_confidence"] = prediction.confidence_pct
            d["ai_explanation"] = explanation

            # Handle Trade Logic (Entry / Exit / P/L)
            self._handle_crossover_trade(sym, smma_res.signal, ltp)

        # 3. Update Chart if selected symbol
        if sym == self.selected_symbol:
            self.chart_widget.add_data_point(ltp, smma_res.smma_fast, smma_res.smma_slow)
            self.ai_drawer.update_stock_analysis(sym, d)

    def _handle_crossover_trade(self, symbol: str, signal_type: str, ltp: float):
        """
        Manages Buy/Sell Trade Entries, Exits, and P/L calculations according to assignment logic:
        Profit/Loss = Sell LTP - Buy LTP
        """
        if symbol not in self.trades_history:
            self.trades_history[symbol] = []

        active_trade = self.active_trades.get(symbol)

        # Close existing open trade if opposite crossover signal occurs
        if active_trade:
            if (active_trade["type"] == "BUY" and signal_type == "SELL") or \
               (active_trade["type"] == "SELL" and signal_type == "BUY"):

                active_trade["exit_ltp"] = ltp
                active_trade["status"] = "CLOSED"

                # Calculate P/L: Sell LTP - Buy LTP
                if active_trade["type"] == "BUY":
                    buy_ltp = active_trade["entry_ltp"]
                    sell_ltp = ltp
                else:  # SELL
                    sell_ltp = active_trade["entry_ltp"]
                    buy_ltp = ltp

                pnl = round(sell_ltp - buy_ltp, 2)
                active_trade["pnl"] = pnl

                self.trades_history[symbol].append(active_trade)
                self.active_trades[symbol] = None

        # Open new trade
        new_trade = {
            "type": signal_type,
            "entry_ltp": ltp,
            "exit_ltp": None,
            "pnl": 0.0,
            "status": "OPEN",
            "timestamp": time.time()
        }
        self.active_trades[symbol] = new_trade
        self.stock_data[symbol]["trades"] = self.trades_history[symbol] + [new_trade]

    def _refresh_ui_table(self):
        total_count = len(self.stock_data)
        screened_count = sum(1 for d in self.stock_data.values() if d["is_screened_in"])
        signal_count = sum(1 for d in self.stock_data.values() if d["signal"] in ["BUY", "SELL"])

        accepted_count = sum(1 for d in self.stock_data.values() if d["ai_decision"] == "ACCEPTED")
        evaluated_count = sum(1 for d in self.stock_data.values() if d["ai_decision"] in ["ACCEPTED", "REJECTED"])
        ai_accept_pct = (accepted_count / evaluated_count * 100.0) if evaluated_count > 0 else 75.0

        self.metrics_bar.update_metrics(total_count, screened_count, signal_count, ai_accept_pct)

        for sym, d in self.stock_data.items():
            self.table_view.update_stock_row(d)

    def _on_stock_selected(self, symbol: str):
        self.selected_symbol = symbol
        self.chart_widget.set_symbol(symbol)
        if symbol in self.stock_data:
            d = self.stock_data[symbol]
            self.ai_drawer.update_stock_analysis(symbol, d)

    def _open_settings(self):
        dlg = SettingsDialog(current_mode=self.feed_manager.mode, parent=self)
        if dlg.exec():
            new_mode = dlg.selected_mode
            creds = dlg.credentials
            connected = self.feed_manager.set_mode(new_mode, creds)
            self.lbl_feed_status.setText(f" Feed: {new_mode} ({'CONNECTED' if connected else 'DISCONNECTED'}) ")
            self.lbl_feed_status.setStyleSheet("color: #a6e3a1;" if connected else "color: #f38ba8;")
            self._perform_screening()

    def closeEvent(self, event):
        self.feed_manager.stop()
        event.accept()
