"""
Unit tests for Technical Indicators (SMMA), ETQ Engine, and Stock Screener.
"""
import time
import pytest
from app.indicators.smma import SMMAEngine, SMMASingleTracker
from app.indicators.etq_engine import ETQEngine, RollingTimeWindow
from app.indicators.screener import StockScreener
from app.data.broker_base import Quote, Tick

def test_smma_calculation():
    tracker = SMMASingleTracker(fast_period=3, slow_period=5)
    prices = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0]

    for p in prices:
        res = tracker.update(p)

    assert res.smma_fast is not None
    assert res.smma_slow is not None
    assert res.smma_fast > 0
    assert res.smma_slow > 0

def test_smma_crossover_detection():
    engine = SMMAEngine(fast_period=3, slow_period=5)
    # Generate prices that cross up
    prices_down = [20.0, 18.0, 16.0, 14.0, 12.0]
    prices_up = [15.0, 20.0, 25.0, 30.0, 35.0]

    for p in prices_down:
        res = engine.update_tick("TATAMOTORS", p)

    crossover_detected = False
    for p in prices_up:
        res = engine.update_tick("TATAMOTORS", p)
        if res.is_crossover and res.signal == "BUY":
            crossover_detected = True

    assert crossover_detected, "BUY crossover should be detected when fast SMMA crosses slow SMMA"

def test_rolling_time_window():
    win = RollingTimeWindow(duration_seconds=5)
    now = time.time()
    win.add(now - 10, 100) # Expired
    win.add(now - 2, 50)   # Valid
    win.add(now, 50)       # Valid

    assert win.get_sum(now) == 100
    assert win.get_average(now) == 50.0

def test_stock_screener_filters():
    screener = StockScreener(min_ltp=30.0, max_ltp=500.0, min_bid_qty=1000000, min_ask_qty=1000000)

    # Valid Stock
    q_valid = Quote("SBIN", ltp=450.0, bid_price=449.9, bid_qty=1500000, ask_price=450.1, ask_qty=1200000, volume=5000000)
    res_valid = screener.evaluate_quote(q_valid)
    assert res_valid.is_screened_in == True
    assert res_valid.passes_price == True
    assert res_valid.passes_liquidity == True

    # Invalid Price (< ₹30)
    q_low_p = Quote("SUBEX", ltp=25.0, bid_price=24.9, bid_qty=1500000, ask_price=25.1, ask_qty=1200000, volume=5000000)
    res_low_p = screener.evaluate_quote(q_low_p)
    assert res_low_p.is_screened_in == False
    assert res_low_p.passes_price == False

    # Invalid Liquidity (< 10L Bid Qty)
    q_low_liq = Quote("XYZ", ltp=200.0, bid_price=199.9, bid_qty=500000, ask_price=200.1, ask_qty=1200000, volume=5000000)
    res_low_liq = screener.evaluate_quote(q_low_liq)
    assert res_low_liq.is_screened_in == False
    assert res_low_liq.passes_liquidity == False
