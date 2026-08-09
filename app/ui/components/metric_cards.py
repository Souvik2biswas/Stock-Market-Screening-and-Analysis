"""
Top KPI Summary Metric Cards Bar Component.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "0", subtext: str = "", color: str = "#89b4fa"):
        super().__init__()
        self.setObjectName("metricCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 10, 12, 10)
        self.layout.setSpacing(4)

        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("metricTitle")

        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("metricValue")
        self.lbl_value.setStyleSheet(f"color: {color};")

        self.lbl_subtext = QLabel(subtext)
        self.lbl_subtext.setObjectName("metricSubtext")

        self.layout.addWidget(self.lbl_title)
        self.layout.addWidget(self.lbl_value)
        self.layout.addWidget(self.lbl_subtext)

    def set_value(self, val: str, subtext: str = ""):
        self.lbl_value.setText(val)
        if subtext:
            self.lbl_subtext.setText(subtext)

class MetricCardsBar(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

        self.card_total = MetricCard("Total Universe", "30", "NSE Stocks Monitored", "#89b4fa")
        self.card_screened = MetricCard("Screened Liquid", "11", "₹30-₹500 & Bid/Ask > 10L", "#a6e3a1")
        self.card_signals = MetricCard("Active Signals", "4", "SMMA(20) × SMMA(120)", "#fab387")
        self.card_ai_win = MetricCard("AI Acceptance", "75%", "Crossover Profit Predictor", "#cba6f7")

        self.layout.addWidget(self.card_total)
        self.layout.addWidget(self.card_screened)
        self.layout.addWidget(self.card_signals)
        self.layout.addWidget(self.card_ai_win)

    def update_metrics(self, total: int, screened: int, signals: int, ai_accept_pct: float):
        self.card_total.set_value(str(total))
        self.card_screened.set_value(str(screened), f"{screened}/{total} Passed Filters")
        self.card_signals.set_value(str(signals))
        self.card_ai_win.set_value(f"{ai_accept_pct:.0f}%", "AI Trade Accept Rate")
