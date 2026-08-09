"""
Interactive Real-Time SMMA Chart Component.
Plots LTP price stream, SMMA(20), and SMMA(120) with crossover signals.
"""
from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

try:
    import pyqtgraph as pg
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

class SMMAChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.current_symbol = ""
        self.max_points = 120

        self.price_history = deque(maxlen=self.max_points)
        self.smma20_history = deque(maxlen=self.max_points)
        self.smma120_history = deque(maxlen=self.max_points)
        self.timestamps = deque(maxlen=self.max_points)

        if PG_AVAILABLE:
            pg.setConfigOption('background', '#181825')
            pg.setConfigOption('foreground', '#cdd6f4')

            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
            self.plot_widget.setLabel('left', 'Price (₹)', color='#a6adc8')
            self.plot_widget.setLabel('bottom', 'Ticks / Time', color='#a6adc8')

            # Create plot curves
            self.curve_price = self.plot_widget.plot(pen=pg.mkPen(color='#89b4fa', width=2), name="LTP")
            self.curve_smma20 = self.plot_widget.plot(pen=pg.mkPen(color='#a6e3a1', width=2, style=Qt.PenStyle.DashLine), name="SMMA (20)")
            self.curve_smma120 = self.plot_widget.plot(pen=pg.mkPen(color='#f38ba8', width=2), name="SMMA (120)")

            self.plot_widget.addLegend(offset=(10, 10))
            self.layout.addWidget(self.plot_widget)
        else:
            self.lbl_fallback = QLabel("pyqtgraph library unavailable. Install pyqtgraph for interactive chart.")
            self.lbl_fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.lbl_fallback)

    def set_symbol(self, symbol: str):
        if self.current_symbol != symbol:
            self.current_symbol = symbol
            self.price_history.clear()
            self.smma20_history.clear()
            self.smma120_history.clear()
            self.timestamps.clear()
            if PG_AVAILABLE:
                self.plot_widget.setTitle(f"Real-Time SMMA Crossover Chart — {symbol}", color="#89b4fa", size="12pt")

    def add_data_point(self, ltp: float, smma20: float, smma120: float):
        self.price_history.append(ltp)
        self.smma20_history.append(smma20)
        self.smma120_history.append(smma120)
        self.timestamps.append(len(self.price_history))

        if PG_AVAILABLE and len(self.price_history) > 1:
            x = list(self.timestamps)
            self.curve_price.setData(x, list(self.price_history))
            self.curve_smma20.setData(x, list(self.smma20_history))
            self.curve_smma120.setData(x, list(self.smma120_history))
