"""
Unit tests for GA Portfolio Optimizer, Tax Advisory, and Natural Language SQL Agent.
"""
import pytest
from app.analytics.portfolio_optimizer import GAPortfolioOptimizer
from app.analytics.tax_advisor import IndianTaxAdvisor
from app.analytics.sql_query_agent import SQLQueryAgent

def test_ga_portfolio_optimizer():
    optimizer = GAPortfolioOptimizer()
    symbols = ["TATAMOTORS", "SBIN", "YESBANK", "ZOMATO", "PNB"]
    prices = {"TATAMOTORS": 445.0, "SBIN": 485.0, "YESBANK": 38.0, "ZOMATO": 165.0, "PNB": 98.0}

    res = optimizer.optimize_portfolio(symbols, prices, max_assets=3)

    assert len(res.selected_symbols) <= 3
    assert res.sharpe_ratio is not None
    assert res.expected_return_pct > 0
    assert abs(sum(res.weights.values()) - 1.0) < 0.01

def test_ga_portfolio_optimizer_with_price_series():
    optimizer = GAPortfolioOptimizer()
    symbols = ["TATAMOTORS", "SBIN", "YESBANK"]
    price_series = {
        "TATAMOTORS": [400.0, 405.0, 410.0, 415.0, 420.0, 430.0, 445.0],
        "SBIN": [450.0, 455.0, 460.0, 465.0, 470.0, 475.0, 485.0],
        "YESBANK": [30.0, 32.0, 31.0, 33.0, 35.0, 36.0, 38.0]
    }

    res = optimizer.optimize_portfolio(symbols, price_series, max_assets=2, generations=20)
    assert len(res.selected_symbols) <= 2
    assert abs(sum(res.weights.values()) - 1.0) < 0.01
    assert "Generational GA Optimizer" in res.summary_text

def test_indian_tax_advisor():
    trades = [
        {"pnl": 15000.0, "entry_ltp": 400.0, "exit_ltp": 430.0, "holding_days": 30},
        {"pnl": -5000.0, "entry_ltp": 100.0, "exit_ltp": 90.0, "holding_days": 10},
        {"pnl": 150000.0, "entry_ltp": 200.0, "exit_ltp": 500.0, "holding_days": 400}
    ]

    res = IndianTaxAdvisor.calculate_taxes(trades)

    assert res.total_realized_profit == 160000.0
    assert res.stcg_realized_gains == 10000.0
    assert res.stcg_tax_payable == 2000.0 # 20% of 10000
    assert res.ltcg_realized_gains == 150000.0
    assert res.ltcg_tax_payable == 3125.0 # 12.5% of (150000 - 125000)
    assert len(res.tax_saving_recommendations) > 0

def test_sql_query_agent():
    agent = SQLQueryAgent()
    data = {
        "TATAMOTORS": {"ltp": 445.0, "bid_qty": 1500000, "ask_qty": 1200000, "etq_5m": 50000, "is_screened_in": True, "signal": "BUY", "ai_decision": "ACCEPTED", "ai_confidence": 85.0},
        "SBIN": {"ltp": 485.0, "bid_qty": 2000000, "ask_qty": 1800000, "etq_5m": 120000, "is_screened_in": True, "signal": "BUY", "ai_decision": "ACCEPTED", "ai_confidence": 92.0}
    }
    agent.update_database(data)

    res = agent.query_natural_language("Show top stocks by 5-minute ETQ volume")
    assert res.row_count > 0
    assert "symbol" in res.columns
    assert res.rows[0][0] == "SBIN" # 120000 > 50000
