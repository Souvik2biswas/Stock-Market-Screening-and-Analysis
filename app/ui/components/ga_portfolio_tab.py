"""
Genetic Algorithm (GA) Portfolio Optimizer UI Component (PyQt6).
Displays optimal asset allocation weights, Sharpe Ratio, expected return %, and volatility.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt
from app.analytics.portfolio_optimizer import GAPortfolioOptimizer, PortfolioOptimizationResult

class GAPortfolioTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.optimizer = GAPortfolioOptimizer()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 14, 14, 14)
        self.layout.setSpacing(14)

        # 1. Header & Run Controls
        top_box = QHBoxLayout()
        lbl_title = QLabel("🧬 Genetic Algorithm Cardinality-Constrained Portfolio Optimizer")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #89b4fa;")

        self.spin_k = QSpinBox()
        self.spin_k.setRange(2, 10)
        self.spin_k.setValue(5)

        btn_run = QPushButton("⚡ Run GA Optimization")
        btn_run.setObjectName("accentButton")
        btn_run.clicked.connect(self._run_optimization)

        top_box.addWidget(lbl_title)
        top_box.addStretch()
        top_box.addWidget(QLabel("Max Assets (K):"))
        top_box.addWidget(self.spin_k)
        top_box.addWidget(btn_run)

        self.layout.addLayout(top_box)

        # 2. Portfolio Metric Cards (Return, Volatility, Sharpe)
        cards_layout = QHBoxLayout()
        self.card_ret = self._create_card("Expected Annual Return", "0.0%", "#a6e3a1")
        self.card_vol = self._create_card("Annualized Volatility", "0.0%", "#fab387")
        self.card_sharpe = self._create_card("Optimal Sharpe Ratio", "0.00", "#cba6f7")

        cards_layout.addWidget(self.card_ret["frame"])
        cards_layout.addWidget(self.card_vol["frame"])
        cards_layout.addWidget(self.card_sharpe["frame"])
        self.layout.addLayout(cards_layout)

        # 3. Weights Table & Summary Text
        grp_weights = QGroupBox("Optimal Portfolio Asset Weight Allocations")
        grp_weights.setStyleSheet("QGroupBox { font-weight: bold; color: #a6adc8; border: 1px solid #313244; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }")
        w_layout = QVBoxLayout(grp_weights)

        self.tbl_weights = QTableWidget(0, 3)
        self.tbl_weights.setHorizontalHeaderLabels(["Asset Symbol", "Optimal Weight (%)", "Allocation Share"])
        self.tbl_weights.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_weights.setStyleSheet("background-color: #181825; font-size: 12px;")
        w_layout.addWidget(self.tbl_weights)

        self.lbl_summary = QLabel("Run GA Optimization to generate cardinality-constrained asset weights.")
        self.lbl_summary.setStyleSheet("color: #6c7086; font-style: italic; font-size: 11px;")
        w_layout.addWidget(self.lbl_summary)

        self.layout.addWidget(grp_weights)

        self.current_symbols = []
        self.current_prices = {}

    def _create_card(self, title: str, val: str, color: str) -> dict:
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 10px;")
        vbox = QVBoxLayout(frame)
        t = QLabel(title)
        t.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        v = QLabel(val)
        v.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        vbox.addWidget(t)
        vbox.addWidget(v)
        return {"frame": frame, "val_lbl": v}

    def update_stock_data(self, symbols: List[str], prices: Dict[str, float]):
        self.current_symbols = symbols
        self.current_prices = prices

    def _run_optimization(self):
        k = self.spin_k.value()
        res: PortfolioOptimizationResult = self.optimizer.optimize_portfolio(
            symbols=self.current_symbols,
            stock_prices=self.current_prices,
            max_assets=k
        )

        self.card_ret["val_lbl"].setText(f"{res.expected_return_pct:.2f}%")
        self.card_vol["val_lbl"].setText(f"{res.volatility_pct:.2f}%")
        self.card_sharpe["val_lbl"].setText(f"{res.sharpe_ratio:.2f}")

        # Update Table
        self.tbl_weights.setRowCount(len(res.weights))
        for i, (sym, w) in enumerate(res.weights.items()):
            pct = w * 100.0
            share_bar = "█" * int(pct // 5)
            self.tbl_weights.setItem(i, 0, QTableWidgetItem(sym))
            self.tbl_weights.setItem(i, 1, QTableWidgetItem(f"{pct:.2f}%"))
            self.tbl_weights.setItem(i, 2, QTableWidgetItem(share_bar))

        self.lbl_summary.setText(res.summary_text)
