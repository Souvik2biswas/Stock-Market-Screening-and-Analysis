"""
AI Analysis Drawer and Trade Log Panel Component.
Displays deep AI trade explanations, feature contributions, and execution history.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class AIDrawerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(12)

        # 1. Header Box
        self.lbl_stock_title = QLabel("SELECT A STOCK FOR AI ANALYSIS")
        self.lbl_stock_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")
        self.layout.addWidget(self.lbl_stock_title)

        # 2. AI Recommendation Card
        self.ai_card = QFrame()
        self.ai_card.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 10px;")
        ai_card_layout = QVBoxLayout(self.ai_card)

        self.lbl_decision = QLabel("AI STATUS: STANDBY")
        self.lbl_decision.setStyleSheet("font-size: 14px; font-weight: bold; color: #a6adc8;")

        self.lbl_confidence = QLabel("Confidence: --%")
        self.lbl_confidence.setStyleSheet("font-size: 12px; color: #cdd6f4;")

        ai_card_layout.addWidget(self.lbl_decision)
        ai_card_layout.addWidget(self.lbl_confidence)
        self.layout.addWidget(self.ai_card)

        # 3. AI Explanation Box
        grp_explanation = QGroupBox("AI Trade Rationale & Strategy Explanation")
        grp_explanation.setStyleSheet("QGroupBox { font-weight: bold; color: #a6adc8; border: 1px solid #313244; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }")
        exp_layout = QVBoxLayout(grp_explanation)

        self.txt_explanation = QTextEdit()
        self.txt_explanation.setReadOnly(True)
        self.txt_explanation.setStyleSheet("background-color: #181825; border: none; color: #cdd6f4; font-size: 12px; line-height: 1.4;")
        self.txt_explanation.setMinimumHeight(100)
        exp_layout.addWidget(self.txt_explanation)

        self.layout.addWidget(grp_explanation)

        # 4. Feature Metrics Table
        grp_features = QGroupBox("Quantitative Feature Metrics")
        grp_features.setStyleSheet("QGroupBox { font-weight: bold; color: #a6adc8; border: 1px solid #313244; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }")
        feat_layout = QVBoxLayout(grp_features)

        self.tbl_features = QTableWidget(5, 2)
        self.tbl_features.setHorizontalHeaderLabels(["Quantitative Feature", "Current Value"])
        self.tbl_features.horizontalHeader().setStretchLastSection(True)
        self.tbl_features.verticalHeader().setVisible(False)
        self.tbl_features.setStyleSheet("background-color: #181825; font-size: 11px;")
        feat_layout.addWidget(self.tbl_features)

        self.layout.addWidget(grp_features)

        # 5. Trade Execution Log
        grp_trades = QGroupBox("Crossover Trade Log (Entry / Exit / P&L)")
        grp_trades.setStyleSheet("QGroupBox { font-weight: bold; color: #a6adc8; border: 1px solid #313244; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }")
        trade_layout = QVBoxLayout(grp_trades)

        self.tbl_trades = QTableWidget(0, 5)
        self.tbl_trades.setHorizontalHeaderLabels(["Type", "Entry LTP", "Exit LTP", "P/L (₹)", "Status"])
        self.tbl_trades.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_trades.horizontalHeader().setStretchLastSection(True)
        self.tbl_trades.verticalHeader().setVisible(False)
        self.tbl_trades.setStyleSheet("background-color: #181825; font-size: 11px;")
        trade_layout.addWidget(self.tbl_trades)

        self.layout.addWidget(grp_trades)

    def update_stock_analysis(self, symbol: str, data: dict):
        self.lbl_stock_title.setText(f"AI ANALYSIS — {symbol}")

        ai_decision = data.get("ai_decision", "STANDBY")
        confidence = data.get("ai_confidence", 0.0)
        explanation = data.get("ai_explanation", "No crossover signal active for this stock yet.")

        if ai_decision == "ACCEPTED":
            self.lbl_decision.setText(f"AI DECISION: ACCEPTED SIGNAL")
            self.lbl_decision.setStyleSheet("font-size: 14px; font-weight: bold; color: #a6e3a1;")
            self.ai_card.setStyleSheet("background-color: rgba(166, 227, 161, 0.1); border: 1px solid #a6e3a1; border-radius: 8px; padding: 10px;")
        elif ai_decision == "REJECTED":
            self.lbl_decision.setText(f"AI DECISION: REJECTED (AVOID TRADE)")
            self.lbl_decision.setStyleSheet("font-size: 14px; font-weight: bold; color: #f38ba8;")
            self.ai_card.setStyleSheet("background-color: rgba(243, 139, 168, 0.1); border: 1px solid #f38ba8; border-radius: 8px; padding: 10px;")
        else:
            self.lbl_decision.setText("AI DECISION: MONITORING MARKET")
            self.lbl_decision.setStyleSheet("font-size: 14px; font-weight: bold; color: #a6adc8;")
            self.ai_card.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 10px;")

        self.lbl_confidence.setText(f"AI Model Confidence: {confidence:.1f}%")
        self.txt_explanation.setText(explanation)

        # Feature matrix update
        feat_rows = [
            ("LTQ Volume Surge (2m/5m)", f"{data.get('ltq_surge', 1.0):.2f}x"),
            ("Bid / Ask Depth Ratio", f"{data.get('bid_ask_ratio', 1.0):.2f}x"),
            ("ETQ Execution Pace (5m/20m)", f"{data.get('etq_acc', 1.0):.2f}x"),
            ("SMMA Spread Gap", f"{data.get('smma_gap', 0.0):.2f}%"),
            ("Price vs 20m VWAP", f"{data.get('price_vs_20m', 0.0):.2f}%")
        ]

        for i, (name, val) in enumerate(feat_rows):
            item_name = QTableWidgetItem(name)
            item_val = QTableWidgetItem(val)
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_features.setItem(i, 0, item_name)
            self.tbl_features.setItem(i, 1, item_val)

        # Trade History Update
        trades = data.get("trades", [])
        self.tbl_trades.setRowCount(len(trades))
        for i, t in enumerate(trades):
            ttype = t.get("type", "BUY")
            entry_p = f"₹{t.get('entry_ltp', 0.0):.2f}"
            exit_p = f"₹{t.get('exit_ltp', 0.0):.2f}" if t.get("exit_ltp") else "ACTIVE"
            pnl = t.get("pnl", 0.0)
            pnl_str = f"₹{pnl:+.2f}" if t.get("exit_ltp") else "--"
            status = t.get("status", "OPEN")

            self.tbl_trades.setItem(i, 0, QTableWidgetItem(ttype))
            self.tbl_trades.setItem(i, 1, QTableWidgetItem(entry_p))
            self.tbl_trades.setItem(i, 2, QTableWidgetItem(exit_p))

            pnl_item = QTableWidgetItem(pnl_str)
            if pnl > 0:
                pnl_item.setForeground(QColor("#a6e3a1"))
            elif pnl < 0:
                pnl_item.setForeground(QColor("#f38ba8"))
            self.tbl_trades.setItem(i, 3, pnl_item)

            self.tbl_trades.setItem(i, 4, QTableWidgetItem(status))
