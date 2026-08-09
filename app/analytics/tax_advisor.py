"""
Indian Equity Income Tax Advisory & Capital Gains Tax Calculator.
Calculates STCG (Sec 111A), LTCG (Sec 112A), STT, and tax optimization recommendations.
"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TaxCalculationResult:
    total_realized_profit: float
    stcg_realized_gains: float      # Short-term gains (<12 months)
    ltcg_realized_gains: float      # Long-term gains (>=12 months)
    stcg_tax_payable: float         # 20% on STCG
    ltcg_tax_payable: float         # 12.5% on LTCG above ₹1.25L
    stt_tax_estimated: float        # Securities Transaction Tax
    net_profit_after_tax: float
    tax_saving_recommendations: List[str]

class IndianTaxAdvisor:
    """
    Indian Stock Market Tax Engine (Income Tax Act 1961 - Sections 111A, 112A, STT).
    """

    STCG_RATE = 0.20                # Section 111A (20% for STCG)
    LTCG_RATE = 0.125               # Section 112A (12.5% for LTCG)
    LTCG_EXEMPTION_LIMIT = 125000.0  # ₹1.25 Lakh exemption limit under Section 112A
    STT_RATE_EQUITY = 0.001         # 0.1% STT on Delivery turnover

    @classmethod
    def calculate_taxes(cls, closed_trades: List[dict]) -> TaxCalculationResult:
        if not closed_trades:
            return TaxCalculationResult(
                total_realized_profit=0.0,
                stcg_realized_gains=0.0,
                ltcg_realized_gains=0.0,
                stcg_tax_payable=0.0,
                ltcg_tax_payable=0.0,
                stt_tax_estimated=0.0,
                net_profit_after_tax=0.0,
                tax_saving_recommendations=["No closed trades available for tax calculation."]
            )

        total_profit = 0.0
        stcg_gains = 0.0
        ltcg_gains = 0.0
        total_turnover = 0.0

        for t in closed_trades:
            pnl = t.get("pnl", 0.0)
            entry_ltp = t.get("entry_ltp", 0.0)
            exit_ltp = t.get("exit_ltp", entry_ltp)
            holding_days = t.get("holding_days", 1)  # Default short-term for intra/swing trading

            total_profit += pnl
            turnover = entry_ltp + exit_ltp
            total_turnover += turnover

            if holding_days >= 365:
                ltcg_gains += pnl
            else:
                stcg_gains += pnl

        # Calculate STCG Tax
        stcg_tax = max(0.0, stcg_gains * cls.STCG_RATE) if stcg_gains > 0 else 0.0

        # Calculate LTCG Tax (First ₹1,25,000 exempt under Sec 112A)
        taxable_ltcg = max(0.0, ltcg_gains - cls.LTCG_EXEMPTION_LIMIT)
        ltcg_tax = taxable_ltcg * cls.LTCG_RATE if taxable_ltcg > 0 else 0.0

        # Estimate STT
        stt = total_turnover * cls.STT_RATE_EQUITY

        total_tax = stcg_tax + ltcg_tax + stt
        net_after_tax = total_profit - total_tax

        # Generate Tax Optimization Recommendations
        recs = []
        if stcg_gains > 50000:
            recs.append("💡 Tax-Loss Harvesting: Consider offsetting STCG gains against unrealized losing positions before March 31.")
        if ltcg_gains > 0 and ltcg_gains < cls.LTCG_EXEMPTION_LIMIT:
            recs.append(f"✅ LTCG Exemption: Your long-term gains (₹{ltcg_gains:,.2f}) are within the tax-free ₹1,25,000 limit (Sec 112A).")
        if stcg_tax > 0:
            recs.append(f"📌 Section 111A STCG Tax Payable: ₹{stcg_tax:,.2f} (Calculated at 20% on short-term gains).")

        if not recs:
            recs.append("Your realized trading gains are currently fully compliant with standard Indian equity tax norms.")

        return TaxCalculationResult(
            total_realized_profit=round(total_profit, 2),
            stcg_realized_gains=round(stcg_gains, 2),
            ltcg_realized_gains=round(ltcg_gains, 2),
            stcg_tax_payable=round(stcg_tax, 2),
            ltcg_tax_payable=round(ltcg_tax, 2),
            stt_tax_estimated=round(stt, 2),
            net_profit_after_tax=round(net_after_tax, 2),
            tax_saving_recommendations=recs
        )
