"""
Unit tests for Machine Learning Feature Extraction, Model Predictor, and Explainer.
"""
import pytest
from app.data.broker_base import Tick
from app.indicators.smma import SMMAResult
from app.indicators.etq_engine import ETQResult
from app.ml.feature_extractor import FeatureExtractor, CrossoverFeatures
from app.ml.model import SignalPredictor
from app.ml.explainer import AIExplainer

def test_feature_extractor():
    tick = Tick("TATAMOTORS", ltp=450.0, ltq=5000, volume=1000000, bid_price=449.8, bid_qty=1500000, ask_price=450.2, ask_qty=1000000)
    smma_res = SMMAResult("TATAMOTORS", smma_fast=452.0, smma_slow=450.0, signal="BUY", is_crossover=True)
    etq_res = ETQResult("TATAMOTORS", etq_5m=50000, etq_20m=150000, etq_60m=400000, avg_price_20m=448.0, avg_price_60m=445.0, ltq_2m_avg=6000.0, ltq_5m_avg=3000.0, ltq_surge_ratio=2.0)

    feats = FeatureExtractor.extract(tick, smma_res, etq_res)

    assert feats.symbol == "TATAMOTORS"
    assert feats.signal == "BUY"
    assert feats.ltq_surge_ratio == 2.0
    assert feats.bid_ask_qty_ratio == 1.5  # 1500000 / 1000000
    assert feats.signal_type_num == 1
    assert len(feats.to_feature_vector()) == 7

def test_ml_signal_predictor():
    predictor = SignalPredictor()
    feats = CrossoverFeatures(
        symbol="TATAMOTORS",
        signal="BUY",
        ltp=450.0,
        ltq_surge_ratio=2.5,     # High LTQ surge
        bid_ask_qty_ratio=1.8,   # High buyer depth
        etq_acceleration=1.4,
        smma_spread_pct=0.5,
        price_vs_avg20_pct=0.4,
        spread_pct=0.08,
        signal_type_num=1
    )

    pred = predictor.predict(feats)
    assert pred.decision in ["ACCEPTED", "REJECTED"]
    assert 0.0 <= pred.confidence_pct <= 100.0
    assert pred.decision == "ACCEPTED"  # Given strong surge & buyer depth

def test_ai_explainer():
    predictor = SignalPredictor()
    feats = CrossoverFeatures(
        symbol="SBIN",
        signal="BUY",
        ltp=480.0,
        ltq_surge_ratio=2.2,
        bid_ask_qty_ratio=1.5,
        etq_acceleration=1.3,
        smma_spread_pct=0.4,
        price_vs_avg20_pct=0.3,
        spread_pct=0.05,
        signal_type_num=1
    )
    pred = predictor.predict(feats)
    explanation = AIExplainer.explain(pred)

    assert len(explanation) > 10
    assert "ACCEPTED" in explanation or "REJECTED" in explanation
