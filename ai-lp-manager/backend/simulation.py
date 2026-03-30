"""
simulation.py — Backtesting Engine for AI LP Manager

Compares AI-managed LP strategy vs a passive baseline (set-and-forget)
over a historical price series.

Class: SimulationEngine
  run(pool_id, initial_amount, days, price_history) -> dict
"""

import math
from datetime import datetime, timedelta, timezone

import numpy as np

import config
from ai_engine import get_engine


class SimulationEngine:
    """
    Backtests an AI LP strategy against a passive baseline.

    Both strategies start with `initial_amount` USD split 50/50
    between token_a and USDC at inception.

    Baseline: never rebalances — just absorbs IL and earns fees.
    AI:       calls StrategyEngine.decide() each day and acts on the signal.
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _impermanent_loss(price_ratio: float) -> float:
        """
        Standard constant-product IL formula.

        Returns IL as a negative fraction, e.g. -0.057 = −5.7% loss vs HODL.
        """
        if price_ratio <= 0:
            return -1.0
        k = price_ratio
        return (2.0 * math.sqrt(k)) / (1.0 + k) - 1.0

    @staticmethod
    def _daily_fee(position_value: float) -> float:
        """
        Estimate one day's fee income for `position_value` USD of liquidity.

        fee = pool_volume × fee_tier × (position / pool_liquidity)
        """
        share = position_value / max(config.POOL_LIQUIDITY_ESTIMATE, 1.0)
        return config.POOL_VOLUME_ESTIMATE * config.FEE_TIER * share

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(
        self,
        pool_id: str,
        initial_amount: float,
        days: int,
        price_history: list,
    ) -> dict:
        """
        Run the backtest simulation.

        Parameters
        ----------
        pool_id        : identifier of the pool (e.g. "SOL-USDC")
        initial_amount : position size in USD at inception
        days           : number of days to simulate
        price_history  : list of dicts with at least a "price" key,
                         ordered oldest → newest (hourly or daily granularity)

        Returns
        -------
        dict with "summary" and "timeline" keys.
        """
        engine = get_engine()

        # ── Chunk price_history into daily buckets ──────────────────────
        # If hourly data (24× len), take one point per day (last hour).
        total_points = len(price_history)
        points_per_day = max(1, total_points // max(days, 1))

        daily_history: list[dict] = [
            price_history[min(i * points_per_day, total_points - 1)]
            for i in range(days)
        ]

        # ── Initial state ───────────────────────────────────────────────
        initial_price: float = float(daily_history[0]["price"]) if daily_history else 1.0

        baseline_value: float = initial_amount
        ai_value:       float = initial_amount

        # Track AI-managed position separately so EXIT actually freezes it
        ai_exited      = False
        ai_exit_value  = 0.0

        timeline:       list[dict] = []
        total_il_baseline = 0.0
        total_il_ai       = 0.0

        now = datetime.now(tz=timezone.utc)

        # Pool stub used by the AI engine
        pool_data = {
            "id":         pool_id,
            "apy":        config.POOL_VOLUME_ESTIMATE * config.FEE_TIER * 365
                          / config.POOL_LIQUIDITY_ESTIMATE * 100,
            "volatility": 0.05,
        }

        # ── Day loop ────────────────────────────────────────────────────
        for day_idx in range(days):
            today_price = float(daily_history[day_idx]["price"])
            date_str    = (now + timedelta(days=day_idx - days)).date().isoformat()

            # Impermanent loss relative to inception price
            price_ratio = today_price / max(initial_price, 1e-9)
            il_fraction = self._impermanent_loss(price_ratio)           # e.g. -0.057
            il_pct      = round(il_fraction * 100.0, 4)

            il_loss_baseline = initial_amount * abs(il_fraction)
            il_loss_ai       = ai_value * abs(il_fraction) if not ai_exited else 0.0

            # Fee income for each strategy
            fee_baseline = self._daily_fee(baseline_value)
            fee_ai       = self._daily_fee(ai_value) if not ai_exited else 0.0

            # ── AI decision (based on last ≤21 days of closing prices) ──
            lookback_start     = max(0, day_idx - 20)
            last_21_daily      = daily_history[lookback_start: day_idx + 1]
            # Expand back to price-dict format the engine expects
            recent_price_dicts = [{"price": float(p["price"])} for p in last_21_daily]

            if not ai_exited:
                decision = engine.decide(pool_data, recent_price_dicts)
                action   = decision["action"]

                if action == "EXIT":
                    # Freeze the AI position — no more IL, no more fees
                    ai_exit_value = ai_value
                    ai_exited     = True
                    fee_ai        = 0.0
                    il_loss_ai    = 0.0
                elif action == "REDUCE":
                    ai_value -= ai_value * 0.30      # withdraw 30%
                elif action == "INCREASE":
                    ai_value += ai_value * 0.10      # add 10% (assume available cash)
                # HOLD → no adjustment
            else:
                action = "EXIT"   # already exited

            # ── Apply daily P&L ────────────────────────────────────────
            baseline_value = baseline_value + fee_baseline - il_loss_baseline
            baseline_value = max(baseline_value, 0.0)

            if not ai_exited:
                ai_value = ai_value + fee_ai - il_loss_ai
                ai_value = max(ai_value, 0.0)

            total_il_baseline += il_loss_baseline
            total_il_ai       += il_loss_ai

            # ── Daily snapshot ─────────────────────────────────────────
            timeline.append(
                {
                    "day":            day_idx + 1,
                    "date":           date_str,
                    "price":          round(today_price, 4),
                    "ai_value":       round(ai_value if not ai_exited else ai_exit_value, 4),
                    "baseline_value": round(baseline_value, 4),
                    "action":         action,
                    "il_pct":         il_pct,
                    "fee_income":     round(fee_ai, 4),
                }
            )

        # ── Final AI value (frozen if exited) ──────────────────────────
        final_ai       = ai_exit_value if ai_exited else ai_value
        final_baseline = baseline_value

        ai_return_pct       = (final_ai       - initial_amount) / initial_amount * 100
        baseline_return_pct = (final_baseline - initial_amount) / initial_amount * 100
        difference_pct      = ai_return_pct - baseline_return_pct
        total_il_avoided    = max(0.0, total_il_baseline - total_il_ai)

        summary = {
            "pool_id":            pool_id,
            "initial_amount":     initial_amount,
            "ai_final":           round(final_ai, 4),
            "baseline_final":     round(final_baseline, 4),
            "ai_return_pct":      round(ai_return_pct, 4),
            "baseline_return_pct": round(baseline_return_pct, 4),
            "difference_pct":     round(difference_pct, 4),
            "ai_wins":            difference_pct > 0,
            "total_il_avoided":   round(total_il_avoided, 4),
            "days":               days,
        }

        return {"summary": summary, "timeline": timeline}
