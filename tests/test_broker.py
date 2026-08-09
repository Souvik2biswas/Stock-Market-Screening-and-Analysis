"""
Unit tests for Mock Broker Data Feeds and Adapter abstractions.
"""
import pytest
import time
from app.data.mock_broker import MockBrokerAdapter

def test_mock_broker_connection():
    broker = MockBrokerAdapter()
    assert broker.connect() == True
    assert broker.is_connected() == True

    universe = broker.get_symbol_universe()
    assert len(universe) >= 20
    assert "TATAMOTORS" in universe
    assert "SBIN" in universe

def test_mock_broker_bulk_quotes():
    broker = MockBrokerAdapter()
    broker.connect()
    symbols = ["TATAMOTORS", "SBIN", "YESBANK"]
    quotes = broker.get_bulk_quotes(symbols)

    assert len(quotes) == 3
    for sym in symbols:
        assert sym in quotes
        q = quotes[sym]
        assert q.ltp > 0
        assert q.bid_qty > 0
        assert q.ask_qty > 0

def test_mock_broker_tick_streaming():
    broker = MockBrokerAdapter()
    broker.connect()

    ticks_received = []
    def on_tick(tick):
        ticks_received.append(tick)

    broker.subscribe_ticks(["TATAMOTORS", "SBIN"], on_tick)
    time.sleep(1.0) # Wait for ticks
    broker.disconnect()

    assert len(ticks_received) > 0, "Ticks should be streamed from Mock Broker"
    assert ticks_received[0].symbol in ["TATAMOTORS", "SBIN"]

def test_angel_one_universe_fallback():
    from app.data.angel_one import AngelOneAdapter
    adapter = AngelOneAdapter()
    universe = adapter.get_symbol_universe()
    assert len(universe) >= 8
    assert "SBIN" in universe or "TATASTEEL" in universe

def test_data_feed_manager_history():
    from app.data.data_feed import DataFeedManager
    dfm = DataFeedManager(mode="MOCK")
    dfm.start()
    quotes = dfm.get_bulk_quotes(["TATAMOTORS", "SBIN"])
    histories = dfm.get_price_histories(["TATAMOTORS"])
    assert "TATAMOTORS" in histories
    assert len(histories["TATAMOTORS"]) >= 1
    dfm.stop()
