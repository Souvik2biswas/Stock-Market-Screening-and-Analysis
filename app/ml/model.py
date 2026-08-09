"""
Machine Learning Classifier for SMMA Crossover Profitability Prediction.
"""
from dataclasses import dataclass
import logging
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.config import MODEL_FILE_PATH, ACCEPTANCE_THRESHOLD_CONFIDENCE
from app.ml.feature_extractor import CrossoverFeatures

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    symbol: str
    signal: str                 # "BUY" or "SELL"
    decision: str               # "ACCEPTED" or "REJECTED"
    confidence_pct: float       # 0.0 to 100.0%
    probability: float          # 0.0 to 1.0
    features: CrossoverFeatures
    explanation: str            # Natural language reason

class SignalPredictor:
    """
    Quantitative AI Signal Predictor.
    """

    def __init__(self, model_path: str = str(MODEL_FILE_PATH)):
        self.model_path = model_path
        self.model: RandomForestClassifier = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded ML Model from {self.model_path}")
                return
            except Exception as e:
                logger.error(f"Error loading model from {self.model_path}: {e}")

        # Train a new Random Forest Classifier model
        logger.info("Training initial Quantitative AI Random Forest Classifier...")
        self.model = self._train_bootstrap_model()
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Saved trained ML model to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    @staticmethod
    def _train_bootstrap_model() -> RandomForestClassifier:
        """
        Generates dataset by running simulated historical price bar trajectories through
        SMMAEngine and ETQEngine, labeling crossover events based on forward N-bar price returns.
        """
        from app.indicators.smma import SMMAEngine
        from app.indicators.etq_engine import ETQEngine
        from app.data.broker_base import Tick

        rng = np.random.default_rng(42)
        feature_rows = []
        labels = []

        symbols = [f"SIM_STOCK_{i}" for i in range(15)]
        num_bars = 250
        forward_window = 15

        for sym in symbols:
            # Simulate Geometric Brownian Motion price trajectory
            base_price = rng.uniform(50.0, 450.0)
            drift = rng.uniform(-0.0002, 0.0004)
            volatility = rng.uniform(0.008, 0.02)
            returns = rng.normal(loc=drift, scale=volatility, size=num_bars)
            prices = [base_price]
            for r in returns:
                prices.append(max(5.0, prices[-1] * (1.0 + r)))

            smma_engine = SMMAEngine(fast_period=20, slow_period=120)
            etq_engine = ETQEngine()

            history_features = []
            history_prices = []

            for t, p in enumerate(prices):
                # Simulate realistic bid/ask depth and volume surge
                spread = p * rng.uniform(0.0005, 0.003)
                bid_price = round(p - spread / 2.0, 2)
                ask_price = round(p + spread / 2.0, 2)
                volume_tick = int(rng.exponential(scale=5000))
                bid_qty = int(rng.uniform(50000, 1500000))
                ask_qty = int(rng.uniform(50000, 1500000))

                tick = Tick(
                    symbol=sym,
                    ltp=round(p, 2),
                    ltq=int(rng.uniform(10, 500)),
                    volume=volume_tick,
                    bid_price=bid_price,
                    bid_qty=bid_qty,
                    ask_price=ask_price,
                    ask_qty=ask_qty,
                    timestamp=float(t)
                )

                smma_res = smma_engine.update(tick.symbol, tick.ltp)
                etq_res = etq_engine.update(tick)

                history_prices.append(tick.ltp)

                # Check if an SMMA crossover occurred at this tick
                if smma_res.is_crossover:
                    feats = FeatureExtractor.extract(tick, smma_res, etq_res)
                    history_features.append((t, feats))

            # Forward-return labeling: evaluate price trajectory after crossover
            for t_idx, feats in history_features:
                if t_idx + forward_window < len(history_prices):
                    future_prices = history_prices[t_idx + 1 : t_idx + 1 + forward_window]
                    entry_p = feats.ltp
                    if feats.signal == "BUY":
                        max_p = max(future_prices)
                        # Profitable if price moves up >= +0.5%
                        label = 1 if (max_p - entry_p) / entry_p >= 0.005 else 0
                    else:
                        min_p = min(future_prices)
                        # Profitable if price drops >= 0.5%
                        label = 1 if (entry_p - min_p) / entry_p >= 0.005 else 0

                    feature_rows.append(feats.to_feature_vector())
                    labels.append(label)

        # Fallback if insufficient crossovers generated
        if len(feature_rows) < 50:
            return SignalPredictor._train_fallback_model()

        X = np.array(feature_rows)
        y = np.array(labels)

        rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        rf.fit(X, y)
        return rf

    @staticmethod
    def _train_fallback_model() -> RandomForestClassifier:
        np.random.seed(42)
        X = np.random.uniform(0.1, 2.0, (200, 7))
        y = np.random.choice([0, 1], size=200)
        rf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
        rf.fit(X, y)
        return rf

    def predict(self, features: CrossoverFeatures) -> PredictionResult:
        vec = np.array([features.to_feature_vector()])
        probs = self.model.predict_proba(vec)[0]
        prob_success = float(probs[1]) if len(probs) > 1 else float(probs[0])
        confidence_pct = round(prob_success * 100.0, 1)

        decision = "ACCEPTED" if prob_success >= ACCEPTANCE_THRESHOLD_CONFIDENCE else "REJECTED"

        return PredictionResult(
            symbol=features.symbol,
            signal=features.signal,
            decision=decision,
            confidence_pct=confidence_pct,
            probability=round(prob_success, 3),
            features=features,
            explanation=""  # Will be populated by AIExplainer
        )
