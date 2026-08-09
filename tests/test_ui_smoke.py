"""
Headless UI Smoke Tests for PyQt6 Dashboard and Components.
Verifies clean import chains and component initialization without GUI display.
"""
import os
import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

def test_ui_imports_and_instantiation():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])

    from app.ui.dashboard import LiveDashboardWindow
    from app.ui.components.stock_table import StockTableView
    from app.ui.components.ga_portfolio_tab import GAPortfolioTabWidget
    from app.ui.components.analytics_tax_tab import AnalyticsTaxTabWidget

    window = LiveDashboardWindow()
    assert window is not None
    assert window.windowTitle() != ""
