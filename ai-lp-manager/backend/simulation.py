"""
simulation.py — LP Position Simulator for AI LP Manager

Provides:
  - Impermanent loss calculation (Uniswap v2 / constant-product model)
  - Fee income estimation
  - Net PnL over a given horizon
  - Multi-step Monte Carlo / GBM price-path simulation
"""

import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LPPosition:
    """Represents an open LP position."""
    pool_id: str
    token_a: str
    token_b: str
    initial_price: float          # Price of token_a in token_b at entry
    current_price: float          # Latest market price
    liquidity_usd: float          # Total liquidity deposited (USD)
    fee_tier: float = 0.003       # e.g. 0.003 = 0.3%
    days_active: int = 1
    volume_24h: float = 1_000_000.0
    apy: float = 30.0             # Annualised fee APY (%)


@dataclass
class SimulationResult:
    """Result bundle returned by simulate_position()."""
    pool_id: str
    initial_value_usd: float
    current_value_usd: float
    impermanent_loss_pct: float      # negative = loss
    fee_income_usd: float
    net_pnl_usd: float
    net_pnl_pct: float
    hold_value_usd: float            # value if user had just HODL'd
    price_path: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 1. Impermanent Loss
# ---------------------------------------------------------------------------

def calc_impermanent_loss(price_ratio: float) -> float:
    """
    Compute impermanent loss for a constant-product (v2) LP.

    price_ratio = current_price / initial_price

    Returns IL as a fraction (negative number means loss).
    Formula: IL = 2*sqrt(k) / (1 + k) - 1  where k = price_ratio
    """
    if price_ratio <= 0:
        return -1.0
    k = price_ratio
    il = (2.0 * math.sqrt(k)) / (1.0 + k) - 1.0
    return il  # e.g. -0.057 = -5.7% loss relative to HODL


def lp_value_after_il(initial_value: float, price_ratio: float) -> float:
    """USD value of LP position after price moves by price_ratio."""
    il = calc_impermanent_loss(price_ratio)
    return initial_value * (1.0 + il)


# ---------------------------------------------------------------------------
# 2. Fee Income
# ---------------------------------------------------------------------------

def calc_fee_income(
    liquidity_usd: float,
    volume_24h: float,
    fee_tier: float,
    days: int,
) -> float:
    """
    Estimate fee income earned over `days`.

    fees_per_day = (liquidity_share_of_pool) × volume_24h × fee_tier
    We approximate share = 1 (single position owns all liquidity — conservative).
    For a realistic estimate, callers should pass volume/liquidity ratio themselves.
    """
    daily_fee_rate = (volume_24h * fee_tier) / max(liquidity_usd, 1.0)
    daily_fee_rate = min(daily_fee_rate, 1.0)   # cap at 100%/day for sanity
    return liquidity_usd * daily_fee_rate * days


# ---------------------------------------------------------------------------
# 3. Full position simulation (single snapshot)
# ---------------------------------------------------------------------------

def simulate_position(position: LPPosition) -> SimulationResult:
    """
    Simulate the current state of an LP position.

    Returns a SimulationResult with IL, fees, and net PnL.
    """
    price_ratio = position.current_price / max(position.initial_price, 1e-9)

    # LP value (with IL baked in)
    current_lp_value = lp_value_after_il(position.liquidity_usd, price_ratio)

    # What the user would have if they just held 50/50 spot
    hold_value = position.liquidity_usd * (
        0.5 + 0.5 * price_ratio   # 50% in token_b (stable), 50% in token_a
    )

    il_pct = calc_impermanent_loss(price_ratio) * 100.0  # as percentage

    fee_income = calc_fee_income(
        position.liquidity_usd,
        position.volume_24h,
        position.fee_tier,
        position.days_active,
    )

    net_pnl_usd = (current_lp_value + fee_income) - position.liquidity_usd
    net_pnl_pct = (net_pnl_usd / max(position.liquidity_usd, 1.0)) * 100.0

    return SimulationResult(
        pool_id=position.pool_id,
        initial_value_usd=position.liquidity_usd,
        current_value_usd=round(current_lp_value, 4),
        impermanent_loss_pct=round(il_pct, 4),
        fee_income_usd=round(fee_income, 4),
        net_pnl_usd=round(net_pnl_usd, 4),
        net_pnl_pct=round(net_pnl_pct, 4),
        hold_value_usd=round(hold_value, 4),
    )


# ---------------------------------------------------------------------------
# 4. Price-path simulation (GBM / Monte Carlo)
# ---------------------------------------------------------------------------

def simulate_price_path(
    start_price: float,
    days: int = 30,
    daily_vol: float = 0.05,
    drift: float = 0.0,
    steps_per_day: int = 24,
    seed: Optional[int] = None,
) -> list[dict]:
    """
    Simulate a Geometric Brownian Motion price path.

    Parameters
    ----------
    start_price   : starting asset price
    days          : number of days to simulate
    daily_vol     : daily volatility (e.g. 0.05 = 5%)
    drift         : daily drift / expected return (e.g. 0.001)
    steps_per_day : hourly by default
    seed          : optional RNG seed for reproducibility

    Returns a list of {timestamp, price, pct_change} dicts.
    """
    if seed is not None:
        random.seed(seed)

    dt = 1.0 / steps_per_day          # fraction of a day per step
    hourly_vol = daily_vol * math.sqrt(dt)
    hourly_drift = drift * dt

    now = datetime.now(tz=timezone.utc)
    total_steps = days * steps_per_day
    path: list[dict] = []
    price = start_price

    for step in range(total_steps):
        ts = now + timedelta(hours=step)
        shock = random.gauss(0.0, 1.0)
        # GBM: ln(S_t) = ln(S_{t-1}) + (μ - σ²/2)dt + σ√dt·Z
        log_return = (hourly_drift - 0.5 * hourly_vol ** 2) + hourly_vol * shock
        price = price * math.exp(log_return)
        price = max(price, 0.001)

        pct_change = ((price - start_price) / start_price) * 100.0

        path.append(
            {
                "timestamp": ts.isoformat(),
                "price": round(price, 6),
                "pct_change": round(pct_change, 4),
            }
        )

    return path


# ---------------------------------------------------------------------------
# 5. Batch simulation helper
# ---------------------------------------------------------------------------

def simulate_pool_scenarios(
    pool: dict,
    scenarios: Optional[list[float]] = None,
) -> list[dict]:
    """
    Run IL + fee simulations across a range of price ratio scenarios.

    pool      : dict from fetch_pool_data() / fetch_all_pools()
    scenarios : list of price ratios to test (default: 0.5x → 2x)

    Returns list of scenario result dicts.
    """
    if scenarios is None:
        scenarios = [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]

    results = []
    base_price = pool.get("price", 100.0)
    liquidity = pool.get("liquidity", 1_000_000.0)
    volume_24h = pool.get("volume_24h", 1_000_000.0)

    for ratio in scenarios:
        pos = LPPosition(
            pool_id=pool.get("id", "unknown"),
            token_a="SOL",
            token_b="USDC",
            initial_price=base_price,
            current_price=base_price * ratio,
            liquidity_usd=liquidity,
            days_active=30,
            volume_24h=volume_24h,
        )
        sim = simulate_position(pos)
        results.append(
            {
                "price_ratio": ratio,
                "final_price": round(base_price * ratio, 4),
                "il_pct": sim.impermanent_loss_pct,
                "fee_income_usd": sim.fee_income_usd,
                "net_pnl_pct": sim.net_pnl_pct,
                "net_pnl_usd": sim.net_pnl_usd,
            }
        )
    return results
