"""
data_fetcher.py — Real market data fetcher with mock fallback
Fetches SOL price, Raydium pool data, and price history for the AI LP Manager.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone

import httpx

import config


# ---------------------------------------------------------------------------
# 1. SOL spot price
# ---------------------------------------------------------------------------

async def fetch_sol_price() -> float:
    """Fetch live SOL price from Jupiter Aggregator. Falls back to mock."""
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as client:
            resp = await client.get(
                config.JUPITER_PRICE_URL,
                params={"ids": "SOL"},
            )
            resp.raise_for_status()
            price = float(resp.json()["data"]["SOL"]["price"])
            print(f"[LIVE] SOL price: ${price:.4f}")
            return price
    except Exception as exc:
        price = random.uniform(140, 180)
        print(f"[MOCK] SOL price: ${price:.4f}  (reason: {exc})")
        return price


# ---------------------------------------------------------------------------
# 2. Single pool data
# ---------------------------------------------------------------------------

async def fetch_pool_data(pool_id: str) -> dict:
    """
    Fetch data for one Raydium pool by its pair name (e.g. 'SOL-USDC').
    Returns mock data on any error or if the pool is not found.
    """
    try:
        async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as client:
            resp = await client.get(config.RAYDIUM_PAIRS_URL)
            resp.raise_for_status()
            pairs = resp.json()  # list of pair dicts

        # Find the matching pair by name field
        match = next(
            (p for p in pairs if p.get("name", "").upper() == pool_id.upper()),
            None,
        )

        if match is None:
            raise ValueError(f"Pool '{pool_id}' not found in Raydium pairs list")

        result = {
            "id":         pool_id,
            "apy":        float(match.get("apy", 0)),
            "price":      float(match.get("price", 0)),
            "volume_24h": float(match.get("volume", {}).get("h24", 0)
                                if isinstance(match.get("volume"), dict)
                                else match.get("volume24h", 0)),
            "liquidity":  float(match.get("liquidity", 0)),
            "volatility": random.uniform(0.03, 0.12),   # not in Raydium API
            "source":     "live",
        }
        print(f"[LIVE] Pool {pool_id}: APY={result['apy']:.2f}%")
        return result

    except Exception as exc:
        mock_price = config.MOCK_START_PRICES.get(
            pool_id.split("-")[0].upper(), random.uniform(10, 200)
        )
        mock = {
            "id":         pool_id,
            "apy":        random.uniform(15, 80),
            "price":      mock_price * (1 + random.uniform(-0.05, 0.05)),
            "volume_24h": random.uniform(500_000, 5_000_000),
            "liquidity":  random.uniform(1_000_000, 20_000_000),
            "volatility": random.uniform(0.03, 0.12),
            "source":     "mock",
        }
        print(f"[MOCK] Pool {pool_id}  (reason: {exc})")
        return mock


# ---------------------------------------------------------------------------
# 3. All configured pools
# ---------------------------------------------------------------------------

async def fetch_all_pools() -> list:
    """Fetch data for every pool defined in config.POOLS — all in parallel."""
    return list(await asyncio.gather(*[fetch_pool_data(p) for p in config.POOLS]))


# ---------------------------------------------------------------------------
# 4. Hourly price history (mock — realistic GBM walk)
# ---------------------------------------------------------------------------

async def fetch_price_history(token: str, days: int = 30) -> list:
    """
    Generate realistic mock hourly price history for a token.

    Uses a Gaussian random walk with 3% daily (≈ 0.87% hourly) volatility,
    anchored to known starting prices for SOL, RAY, and mSOL.

    Returns a list of dicts with keys: timestamp, price, volume.
    Length = days * 24.
    """
    token_upper = token.upper()

    # Base starting price — try to match known tokens, otherwise random
    start_price: float = config.MOCK_START_PRICES.get(
        token_upper, random.uniform(10, 200)
    )

    # Daily vol → hourly vol (σ_h ≈ σ_d / √24)
    hourly_vol = (start_price * 0.03) / (24 ** 0.5)

    now = datetime.now(tz=timezone.utc)
    total_hours = days * 24
    history: list[dict] = []
    price = start_price

    for hour_offset in range(total_hours - 1, -1, -1):
        ts = now - timedelta(hours=hour_offset)
        price = max(price + random.gauss(0, hourly_vol), 0.01)  # never go negative
        volume = random.uniform(500_000, 5_000_000)

        history.append(
            {
                "timestamp": ts.isoformat(),
                "price":     round(price, 6),
                "volume":    round(volume, 2),
            }
        )

    return history
