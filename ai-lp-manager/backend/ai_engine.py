"""
ai_engine.py — Core AI Decision Engine for AI LP Manager

Class: StrategyEngine
  - calculate_volatility(prices) -> float
  - calculate_trend(prices)      -> float
  - calculate_score(apy, vol, trend) -> float  [0.0 – 1.0]
  - decide(pool_data, price_history) -> dict

Module-level factory:
  get_engine() -> StrategyEngine
"""

from datetime import datetime, timezone

import numpy as np

import config


class StrategyEngine:
    """Rule-based AI engine that scores LP pools and decides on an action."""

    # ------------------------------------------------------------------
    # 1. Volatility
    # ------------------------------------------------------------------

    def calculate_volatility(self, prices: list[float]) -> float:
        """
        Coefficient of variation: std(prices) / mean(prices).

        Higher value = more volatile.
        Returns 0.0 if the list is too short or the mean is zero.
        """
        if len(prices) < 2:
            return 0.0
        arr = np.array(prices, dtype=float)
        mean = arr.mean()
        if mean == 0.0:
            return 0.0
        return round(float(arr.std() / mean), 4)

    # ------------------------------------------------------------------
    # 2. Trend
    # ------------------------------------------------------------------

    def calculate_trend(self, prices: list[float]) -> float:
        """
        Momentum: (mean of last 3 points) / (mean of first 3 points) - 1.

        Positive → uptrend, negative → downtrend.
        Returns 0.0 if fewer than 6 data points are supplied.
        """
        if len(prices) < 6:
            return 0.0
        arr = np.array(prices, dtype=float)
        old_avg    = arr[:3].mean()
        recent_avg = arr[-3:].mean()
        if old_avg == 0.0:
            return 0.0
        return round(float((recent_avg - old_avg) / old_avg), 4)

    # ------------------------------------------------------------------
    # 3. Composite score
    # ------------------------------------------------------------------

    def calculate_score(
        self, apy: float, volatility: float, trend: float
    ) -> float:
        """
        Weighted composite score in [0.0, 1.0].

        Weights:
          APY        50% — higher APY = better
          Volatility 30% — lower vol  = better
          Trend      20% — uptrend    = better

        Normalisation:
          apy_score   = min(apy / 100, 1.0)
          vol_score   = max(0, 1 - volatility / 0.2)
          trend_score = clamp((trend + 0.1) / 0.2, 0, 1)
        """
        apy_score   = min(apy / 100.0, 1.0)
        vol_score   = max(0.0, 1.0 - volatility / 0.2)
        trend_raw   = (trend + 0.1) / 0.2
        trend_score = max(0.0, min(1.0, trend_raw))

        score = apy_score * 0.5 + vol_score * 0.3 + trend_score * 0.2
        return round(float(score), 4)

    # ------------------------------------------------------------------
    # 4. Decision
    # ------------------------------------------------------------------

    def decide(self, pool_data: dict, price_history: list) -> dict:
        """
        Full decision pipeline for one pool.

        Parameters
        ----------
        pool_data     : dict from fetch_pool_data() / fetch_all_pools()
        price_history : list of dicts with a "price" key (from fetch_price_history())

        Returns a decision dict with action, score, confidence, and reasoning.
        """
        # Extract price series
        prices: list[float] = [
            float(p["price"]) for p in price_history if "price" in p
        ]

        apy        = float(pool_data.get("apy", 0.0))
        pool_id    = pool_data.get("id", "unknown")

        volatility = self.calculate_volatility(prices)
        trend      = self.calculate_trend(prices)
        score      = self.calculate_score(apy, volatility, trend)

        # --- Action determination ---
        if score >= config.SCORE_INCREASE:
            action = "INCREASE"
        elif score <= config.SCORE_EXIT:
            action = "EXIT"
        elif score <= config.SCORE_REDUCE:
            action = "REDUCE"
        else:
            action = "HOLD"

        # --- Human-readable reasoning ---
        apy_desc = "high" if apy >= 40 else "moderate" if apy >= 15 else "low"
        vol_desc = "low" if volatility < 0.04 else "moderate" if volatility < 0.09 else "high"
        trend_desc = (
            "uptrend"   if trend >  0.02 else
            "downtrend" if trend < -0.02 else
            "sideways"
        )

        reason_parts = [
            f"{apy_desc.capitalize()} APY ({apy:.1f}%) ",
            f"with {vol_desc} volatility ({volatility:.4f}) ",
            f"and {trend_desc} momentum ({trend:+.4f}) ",
            f"yields a score of {score:.2f} → {action}.",
        ]

        if action == "INCREASE":
            reason_parts.append(
                " Strong fundamentals — consider adding liquidity."
            )
        elif action == "EXIT":
            reason_parts.append(
                " Poor risk/reward — exit to preserve capital."
            )
        elif action == "REDUCE":
            reason_parts.append(
                " Weakening metrics — reduce exposure to limit downside."
            )
        else:
            reason_parts.append(" Metrics stable — maintain current position.")

        reason = "".join(reason_parts)

        # --- Confidence: distance from neutral (0.5), scaled to [0, 1] ---
        confidence = round(abs(score - 0.5) * 2.0, 4)

        return {
            "action":     action,
            "score":      score,
            "confidence": confidence,
            "apy":        apy,
            "volatility": volatility,
            "trend":      trend,
            "reason":     reason,
            "timestamp":  datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(),
        }


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

def get_engine() -> StrategyEngine:
    """Return a new StrategyEngine instance."""
    return StrategyEngine()
