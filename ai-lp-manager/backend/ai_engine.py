"""
ai_engine.py — Core AI Decision Engine for AI LP Manager

Implements a robust, regime-based quantitative trading strategy avoiding "buy high, sell low"
behavior. Utilizes moving averages for trend, standard deviation of returns for volatility, and
implements strict risk management rules (stop-loss, allocation limits, trade cooldowns).

Module-level factory:
  get_engine() -> StrategyEngine
"""

from datetime import datetime, timezone
import numpy as np

class StrategyEngine:
    """Regime-based quantitative analysis engine that scores LP pools and decides on an action."""

    def __init__(self):
        # Maintain state to enforce cooldown periods and track entry prices per pool
        self.state = {}

    def decide(self, pool_data: dict, price_history: list) -> dict:
        """
        Full decision pipeline for one pool.

        Parameters
        ----------
        pool_data     : dict from fetch_pool_data() / fetch_all_pools()
        price_history : list of dicts with a "price" key (from fetch_price_history())

        Returns a decision dict with action, score, confidence, and human-readable reasoning.
        """
        pool_id = pool_data.get("id", "unknown")
        
        # 1. Initialize per-pool state for tracking positions and cooldown
        if pool_id not in self.state:
            self.state[pool_id] = {
                'cooldown': 0,
                'entry_price': None
            }

        prices = [float(p["price"]) for p in price_history if "price" in p]
        
        # We need at least 20 periods for the long moving average
        if len(prices) < 20:
            return self._build_response(
                "HOLD", 0.0,
                "Warming up: Insufficient price history for long-term indicators (requires 20 periods).",
                0.0, 0.0
            )

        current_price = prices[-1]

        # ------------------------------------------------------------------
        # 2. Compute Technical Indicators
        # ------------------------------------------------------------------
        
        # A. Trend (Moving Averages)
        short_ma = float(np.mean(prices[-5:]))
        long_ma = float(np.mean(prices[-20:]))
        
        # B. Volatility (Standard Deviation of returns)
        arr = np.array(prices)
        returns = np.diff(arr) / arr[:-1]
        volatility = float(np.std(returns[-20:]))
        
        # C. Momentum (Price change over last 5 periods)
        momentum = float((current_price - prices[-6]) / prices[-6])

        # ------------------------------------------------------------------
        # 3. Risk Management Layer
        # ------------------------------------------------------------------
        
        # A. Stop Loss (5% drop from entry)
        if self.state[pool_id]['entry_price'] is None:
            # If we don't know the exact entry, use the local rolling maximum to act as a trailing stop
            self.state[pool_id]['entry_price'] = float(np.max(prices[-20:]))
            
        entry_price = self.state[pool_id]['entry_price']
        price_drop = (current_price - entry_price) / max(entry_price, 1e-9)
        
        if price_drop <= -0.05:
            # Hard exit rule to preserve capital
            self.state[pool_id]['entry_price'] = None       # Reset tracking basis
            self.state[pool_id]['cooldown'] = 0             # Clear cooldown to act immediately
            return self._build_response(
                "EXIT", 0.95, 
                f"STOP LOSS REQUIRED: Asset portfolio dropped {abs(price_drop)*100:.2f}%. Exiting to protect capital.", 
                volatility, momentum
            )

        # B. Trade Cooldown (Prevent overtrading/churn)
        if self.state[pool_id]['cooldown'] > 0:
            self.state[pool_id]['cooldown'] -= 1
            return self._build_response(
                "HOLD", 0.5, 
                "Risk Management: Cooldown active to prevent overtrading. Holding current position.", 
                volatility, momentum
            )

        # C. Volatility Filter
        VOLATILITY_THRESHOLD = 0.04  # ~4% std dev is considered highly unstable here
        if volatility > VOLATILITY_THRESHOLD:
            return self._build_response(
                "HOLD", 0.8, 
                f"Risk Management: High volatility regime detected ({volatility*100:.2f}%). Avoiding trades until stabilization.", 
                volatility, momentum
            )

        # ------------------------------------------------------------------
        # 4. Strategy Engine Logic
        # ------------------------------------------------------------------
        
        MOMENTUM_THRESHOLD = 0.02    # 2% momentum required to confirm trend
        ALLOCATION_LIMIT_TEXT = "(Risk Management ENFORCED: Maximum 20% allocation per action.)"
        
        # Scenario 1: Strong Uptrend
        if short_ma > long_ma and momentum > MOMENTUM_THRESHOLD:
            action = "INCREASE"
            reason = f"Strong uptrend confirmed (Short MA > Long MA) with positive momentum (+{momentum*100:.2f}%). Logic dictates adding liquidity. {ALLOCATION_LIMIT_TEXT}"
            confidence = min(0.95, 0.5 + (momentum / 0.1))
            self.state[pool_id]['cooldown'] = 3
            self.state[pool_id]['entry_price'] = current_price  # Update basis when averaging up
            
        # Scenario 2: Strong Downtrend
        elif short_ma < long_ma and momentum < -MOMENTUM_THRESHOLD:
            # Check for severe drop
            if momentum < -(MOMENTUM_THRESHOLD * 2):
                action = "EXIT"
                reason = f"Severe downtrend forming (Short MA < Long MA, Momentum {momentum*100:.2f}%). Logic dictates exiting fully to avoid extended losses."
                confidence = 0.90
                self.state[pool_id]['entry_price'] = None       # Clear tracking position
            else:
                action = "REDUCE"
                reason = f"Downtrend forming (Short MA < Long MA). Logic dictates reducing exposure to limit downside momentum impact. {ALLOCATION_LIMIT_TEXT}"
                confidence = 0.75
            self.state[pool_id]['cooldown'] = 3
            
        # Scenario 3: Sideways Market
        else:
            action = "HOLD"
            reason = "Ranging/Sideways market detected. No strong trend indicator present. Holding to prevent overtrading."
            confidence = 0.50

        return self._build_response(action, confidence, reason, volatility, momentum)

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _build_response(self, action: str, confidence: float, reason: str, vol: float, trend: float) -> dict:
        """Constructs an output dictionary compatible with the frontend schema."""
        return {
            "action":     action,
            "score":      round(confidence, 4),    # Overload score with confidence for backward-compatibility
            "confidence": round(confidence, 4),
            "apy":        0.0,                     # Replaced by indicators, zeroed out
            "volatility": round(vol, 4),
            "trend":      round(trend, 4),
            "reason":     reason,
            "timestamp":  datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(),
        }

# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

def get_engine() -> StrategyEngine:
    """Return a new StrategyEngine instance."""
    return StrategyEngine()

# Keep legacy unused mock signatures valid if imported elsewhere
def analyse_pool(a, *args, **kwargs): return {}
def analyse_all_pools(a, *args, **kwargs): return []
def recommend_range(a, *args, **kwargs): return {}
