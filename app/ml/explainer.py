"""
AI Natural Language Explanation Generator.
Provides readable trade rationale explaining why an SMMA crossover signal is ACCEPTED or REJECTED.
"""
from app.ml.feature_extractor import CrossoverFeatures
from app.ml.model import PredictionResult

class AIExplainer:
    """
    Generates human-readable trade rationale from feature contributions and model prediction.
    """

    @staticmethod
    def explain(result: PredictionResult) -> str:
        f = result.features
        decision = result.decision
        signal = f.signal
        conf = result.confidence_pct

        drivers = []
        cautions = []

        # 1. LTQ Surge Ratio
        if f.ltq_surge_ratio >= 1.5:
            drivers.append(f"Strong institutional LTQ volume surge ({f.ltq_surge_ratio}x 2m/5m ratio)")
        elif f.ltq_surge_ratio >= 1.1:
            drivers.append(f"Moderate LTQ volume uptick ({f.ltq_surge_ratio}x 2m/5m ratio)")
        else:
            cautions.append(f"Weak LTQ volume momentum ({f.ltq_surge_ratio}x 2m/5m ratio)")

        # 2. Bid/Ask Quantity Depth Ratio
        if signal == "BUY":
            if f.bid_ask_qty_ratio >= 1.2:
                drivers.append(f"Strong Bid depth support ({f.bid_ask_qty_ratio}x Bid/Ask ratio)")
            elif f.bid_ask_qty_ratio <= 0.8:
                cautions.append(f"Heavy Ask sell wall creating overhead resistance ({f.bid_ask_qty_ratio}x Bid/Ask ratio)")
        else: # SELL
            if f.bid_ask_qty_ratio <= 0.8:
                drivers.append(f"Dominant Ask sell pressure ({f.bid_ask_qty_ratio}x Bid/Ask ratio)")
            elif f.bid_ask_qty_ratio >= 1.2:
                cautions.append(f"Strong Bid buy wall opposing downward momentum ({f.bid_ask_qty_ratio}x Bid/Ask ratio)")

        # 3. ETQ Acceleration
        if f.etq_acceleration >= 1.25:
            drivers.append(f"Accelerating trade execution rate ({f.etq_acceleration}x vs 20m pace)")
        elif f.etq_acceleration <= 0.75:
            cautions.append(f"Decelerating execution activity ({f.etq_acceleration}x vs 20m pace)")

        # 4. SMMA Spread Trend Slope
        if f.smma_spread_pct >= 0.15:
            drivers.append(f"Wide SMMA separation gap ({f.smma_spread_pct:.2f}% trend divergence)")

        # Assemble summary explanation string
        if decision == "ACCEPTED":
            main_driver = drivers[0] if drivers else "Favorable technical momentum"
            second_driver = f" and {drivers[1].lower()}" if len(drivers) > 1 else ""
            explanation = f"ACCEPTED ({conf}% Confidence): {main_driver}{second_driver}. SMMA(20) crossover backed by strong quantitative flow."
        else:
            main_caution = cautions[0] if cautions else "Insufficient volume momentum"
            second_caution = f" and {cautions[1].lower()}" if len(cautions) > 1 else ""
            explanation = f"REJECTED ({conf}% Confidence): {main_caution}{second_caution}. High risk of false crossover failure."

        return explanation
