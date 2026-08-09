"""
Live Tabular Dashboard Grid Component (PyQt6).
Displays real-time stock metrics, SMMA indicators, ETQ, Market Depth, and AI predictions.
"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class StockTableView(QTableWidget):
    stock_selected = pyqtSignal(str)  # Emits symbol when user clicks a row

    COLUMNS = [
        "Symbol", "LTP (₹)", "Bid Price", "Bid Qty (Lakhs)", "Ask Price", "Ask Qty (Lakhs)",
        "SMMA (20)", "SMMA (120)", "Signal", "5m ETQ", "20m ETQ", "60m ETQ",
        "20m Avg LTP", "60m Avg LTP", "Liquidity Filter", "AI Prediction", "Confidence"
    ]

    def __init__(self):
        super().__init__()
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.itemSelectionChanged.connect(self._on_selection_changed)

        self._symbol_to_row = {}

    def _on_selection_changed(self):
        selected_items = self.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            symbol_item = self.item(row, 0)
            if symbol_item:
                self.stock_selected.emit(symbol_item.text())

    def update_stock_row(self, data: dict):
        symbol = data.get("symbol", "")
        if not symbol:
            return

        if symbol not in self._symbol_to_row:
            row = self.rowCount()
            self.insertRow(row)
            self._symbol_to_row[symbol] = row
        else:
            row = self._symbol_to_row[symbol]

        # Formatted fields
        ltp = f"₹{data.get('ltp', 0.0):.2f}"
        bid_p = f"₹{data.get('bid_price', 0.0):.2f}"
        bid_q_lakhs = f"{data.get('bid_qty', 0) / 100000.0:.2f} L"
        ask_p = f"₹{data.get('ask_price', 0.0):.2f}"
        ask_q_lakhs = f"{data.get('ask_qty', 0) / 100000.0:.2f} L"
        smma20 = f"₹{data.get('smma_20', 0.0):.2f}"
        smma120 = f"₹{data.get('smma_120', 0.0):.2f}"
        signal = data.get("signal", "NONE")
        etq5m = f"{data.get('etq_5m', 0):,}"
        etq20m = f"{data.get('etq_20m', 0):,}"
        etq60m = f"{data.get('etq_60m', 0):,}"
        avg20m = f"₹{data.get('avg_price_20m', 0.0):.2f}"
        avg60m = f"₹{data.get('avg_price_60m', 0.0):.2f}"
        liq_status = "PASS" if data.get("is_screened_in", False) else "FAIL"
        ai_decision = data.get("ai_decision", "N/A")
        ai_conf = f"{data.get('ai_confidence', 0.0):.1f}%" if ai_decision != "N/A" else "N/A"

        row_values = [
            symbol, ltp, bid_p, bid_q_lakhs, ask_p, ask_q_lakhs,
            smma20, smma120, signal, etq5m, etq20m, etq60m,
            avg20m, avg60m, liq_status, ai_decision, ai_conf
        ]

        for col, val in enumerate(row_values):
            item = self.item(row, col)
            if not item:
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col > 0 else Qt.AlignmentFlag.AlignLeft)
                self.setItem(row, col, item)

            item.setText(str(val))

            # Style Signal Column
            if col == 8: # Signal
                if val == "BUY":
                    item.setForeground(QColor("#a6e3a1"))
                    item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                elif val == "SELL":
                    item.setForeground(QColor("#f38ba8"))
                    item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                else:
                    item.setForeground(QColor("#6c7086"))

            # Style Liquidity Status Column
            elif col == 14: # Liquidity Filter
                if val == "PASS":
                    item.setForeground(QColor("#a6e3a1"))
                else:
                    item.setForeground(QColor("#f38ba8"))

            # Style AI Decision Column
            elif col == 15: # AI Decision
                if val == "ACCEPTED":
                    item.setForeground(QColor("#a6e3a1"))
                    item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                elif val == "REJECTED":
                    item.setForeground(QColor("#f38ba8"))
                    item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
