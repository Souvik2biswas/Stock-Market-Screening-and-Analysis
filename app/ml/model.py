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
        Generates realistic synthetic dataset of SMMA crossover features and outcomes,
        training a robust Random Forest Classifier.
        """
        np.random.seed(42)
        n_samples = 1500

        # Feature generation:
        # ltq_surge_ratio: 0.5 to 3.5
        ltq_surge = np.random.uniform(0.5, 3.5, n_samples)
        # bid_ask_qty_ratio: 0.3 to 3.0
        bid_ask_ratio = np.random.uniform(0.3, 3.0, n_samples)
        # etq_acceleration: 0.4 to 2.5
        etq_acc = np.random.uniform(0.4, 2.5, n_samples)
        # smma_spread_pct: 0.01 to 1.5%
        smma_spread = np.random.uniform(0.01, 1.5, n_samples)
        # price_vs_avg20_pct: -2.0 to +2.0%
        price_vs_avg = np.random.uniform(-2.0, 2.0, n_samples)
        # spread_pct: 0.01 to 0.5%
        spread_pct = np.random.uniform(0.01, 0.5, n_samples)
        # signal_type_num: 0 (SELL) or 1 (BUY)
        sig_type = np.random.choice([0, 1], size=n_samples)

        # Ground Truth Logic: Profitable trade if high LTQ surge + favorable Bid/Ask depth support
        # For BUY: high LTQ surge + high bid_ask_ratio (strong buyers) -> Profitable
        # For SELL: high LTQ surge + low bid_ask_ratio (strong sellers) -> Profitable
        depth_impact = np.where(sig_type == 1, bid_ask_ratio - 1.0, 1.0 - bid_ask_ratio)
        score = (
            0.35 * (ltq_surge - 1.0) +
            0.30 * depth_impact +
            0.20 * (etq_acc - 1.0) +
            0.15 * (smma_spread - 0.2) -
            0.10 * (spread_pct * 10)
        )
        
        prob = 1.0 / (1.0 + np.exp(-score))
        labels = (prob > 0.50).astype(int)

        X = np.column_stack([
            ltq_surge, bid_ask_ratio, etq_acc, smma_spread, price_vs_avg, spread_pct, sig_type
        ])

        rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        rf.fit(X, labels)
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
