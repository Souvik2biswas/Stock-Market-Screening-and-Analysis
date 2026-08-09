"""
Natural Language SQL Analytics & Indian Income Tax Advisory UI Component (PyQt6).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt
from app.analytics.sql_query_agent import SQLQueryAgent, SQLQueryResult
from app.analytics.tax_advisor import IndianTaxAdvisor, TaxCalculationResult

class AnalyticsTaxTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.sql_agent = SQLQueryAgent()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 14, 14, 14)
        self.layout.setSpacing(12)

        # 1. Natural Language Query Input Box
        grp_nl = QGroupBox("💬 Natural Language & SQL Financial Analytics Engine")
        grp_nl.setStyleSheet("QGroupBox { font-weight: bold; color: #a6adc8; border: 1px solid #313244; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }")
        nl_layout = QVBoxLayout(grp_nl)

        search_box = QHBoxLayout()
        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("Ask a question in plain English (e.g. 'Show top liquid stocks by 5-minute ETQ volume')...")
        self.txt_query.returnPressed.connect(self._run_nl_query)

        btn_run_sql = QPushButton("Execute Query")
        btn_run_sql.setObjectName("accentButton")
        btn_run_sql.clicked.connect(self._run_nl_query)

        search_box.addWidget(self.txt_query)
        search_box.addWidget(btn_run_sql)
        nl_layout.addLayout(search_box)

        # Preset Shortcut Buttons
        preset_box = QHBoxLayout()
        btn_p1 = QPushButton("🔥 Top 5 ETQ Volume Stocks")
        btn_p1.clicked.connect(lambda: self._set_query("Show top 5 stocks by 5-minute ETQ volume"))
        btn_p2 = QPushButton("🎯 Active BUY & ACCEPTED Signals")
        btn_p2.clicked.connect(lambda: self._set_query("Find all ACCEPTED BUY signals"))
        btn_p3 = QPushButton("✅ Screened Liquid Universe")
        btn_p3.clicked.connect(lambda: self._set_query("Show all screened liquid stocks"))

        preset_box.addWidget(btn_p1)
        preset_box.addWidget(btn_p2)
        preset_box.addWidget(btn_p3)
        preset_box.addStretch()
        nl_layout.addLayout(preset_box)

        # Generated SQL Label
        self.lbl_sql = QLabel("SQL: SELECT * FROM market_data WHERE is_screened_in = 1")
        self.lbl_sql.setStyleSheet("color: #89b4fa; font-family: monospace; font-size: 11px;")
        nl_layout.addWidget(self.lbl_sql)

        # Results Table
        self.tbl_results = QTableWidget(0, 0)
        self.tbl_results.setStyleSheet("background-color: #181825; font-size: 11px;")
        nl_layout.addWidget(self.tbl_results)

        self.layout.addWidget(grp_nl)

        # 2. Indian Capital Gains Tax Advisory Panel
        grp_tax = QGroupBox("🏛 Indian Income Tax Advisory (Sections 111A, 112A & STT)")
        grp_tax.setStyleSheet("QGroupBox { font-weight: bold; color: #a6adc8; border: 1px solid #313244; border-radius: 6px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }")
        tax_layout = QHBoxLayout(grp_tax)

        self.lbl_tax_stats = QLabel("STCG Tax (Sec 111A @ 20%): ₹0.00\nLTCG Tax (Sec 112A @ 12.5%): ₹0.00\nSTT Tax Estimated: ₹0.00\nNet Realized Profit After Tax: ₹0.00")
        self.lbl_tax_stats.setStyleSheet("font-size: 12px; color: #cdd6f4; line-height: 1.5;")
        tax_layout.addWidget(self.lbl_tax_stats)

        self.txt_tax_recs = QTextEdit()
        self.txt_tax_recs.setReadOnly(True)
        self.txt_tax_recs.setStyleSheet("background-color: #181825; border: none; color: #a6e3a1; font-size: 11px;")
        self.txt_tax_recs.setText("Tax Advisory Recommendations:\n• STCG gains taxed at 20% under Section 111A.\n• LTCG gains tax-free up to ₹1,25,000 per year under Section 112A.")
        tax_layout.addWidget(self.txt_tax_recs)

        self.layout.addWidget(grp_tax)

    def _set_query(self, text: str):
        self.txt_query.setText(text)
        self._run_nl_query()

    def update_market_database(self, stock_data_dict: dict, closed_trades: list):
        self.sql_agent.update_database(stock_data_dict)
        self._run_nl_query()

        # Update Tax Calculation
        tax_res: TaxCalculationResult = IndianTaxAdvisor.calculate_taxes(closed_trades)
        self.lbl_tax_stats.setText(
            f"Total Realized Trade Profit: ₹{tax_res.total_realized_profit:,.2f}\n"
            f"STCG Tax (Sec 111A @ 20%): ₹{tax_res.stcg_tax_payable:,.2f}\n"
            f"LTCG Tax (Sec 112A @ 12.5%): ₹{tax_res.ltcg_tax_payable:,.2f}\n"
            f"Estimated STT: ₹{tax_res.stt_tax_estimated:,.2f}\n"
            f"Net Profit After Tax: ₹{tax_res.net_profit_after_tax:,.2f}"
        )
        self.txt_tax_recs.setText("Tax Advisory Recommendations:\n" + "\n".join(f"• {r}" for r in tax_res.tax_saving_recommendations))

    def _run_nl_query(self):
        query_text = self.txt_query.text().strip() or "Show screened liquid stocks"
        res: SQLQueryResult = self.sql_agent.query_natural_language(query_text)

        self.lbl_sql.setText(f"Generated SQL: {res.generated_sql}")

        if res.error_message:
            self.tbl_results.setRowCount(1)
            self.tbl_results.setColumnCount(1)
            self.tbl_results.setItem(0, 0, QTableWidgetItem(res.error_message))
            return

        self.tbl_results.setColumnCount(len(res.columns))
        self.tbl_results.setHorizontalHeaderLabels(res.columns)
        self.tbl_results.setRowCount(len(res.rows))

        for r_idx, row in enumerate(res.rows):
            for c_idx, val in enumerate(row):
                self.tbl_results.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        
        self.tbl_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
