"""
server.py — FastAPI Server for AI LP Manager

Endpoints:
  GET  /                          – health check
  GET  /api/pools                 – all pools with AI analysis
  GET  /api/pools/{pool_id}       – single pool analysis
  GET  /api/price-history/{token} – hourly price history
  GET  /api/wallet/{address}      – wallet summary + on-chain LP positions
  POST /api/simulate              – simulate a custom LP position
  GET  /api/scenarios/{pool_id}   – IL scenarios across price ratios
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
from data_fetcher import (
    fetch_all_pools,
    fetch_pool_data,
    fetch_price_history,
    fetch_sol_price,
)
from ai_engine import analyse_pool, analyse_all_pools, recommend_range
from simulation import (
    LPPosition,
    simulate_pool_scenarios,
    simulate_position,
    simulate_price_path,
)
from solana_client import get_wallet_summary, get_lp_positions


# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI LP Manager backend starting…")
    yield
    print("🛑 AI LP Manager backend shutting down…")


app = FastAPI(
    title="AI LP Manager API",
    description="AI-powered Liquidity Pool management for Solana / Raydium",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class SimulateRequest(BaseModel):
    pool_id:       str   = Field("SOL-USDC", example="SOL-USDC")
    token_a:       str   = Field("SOL",      example="SOL")
    token_b:       str   = Field("USDC",     example="USDC")
    initial_price: float = Field(150.0,      gt=0)
    current_price: float = Field(165.0,      gt=0)
    liquidity_usd: float = Field(10_000.0,   gt=0)
    fee_tier:      float = Field(0.003,      gt=0, le=1)
    days_active:   int   = Field(30,         ge=1, le=365)
    volume_24h:    float = Field(1_000_000.0, gt=0)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def health():
    return {"status": "ok", "service": "AI LP Manager", "version": "0.1.0"}


@app.get("/api/sol-price", tags=["Market"])
async def sol_price():
    """Live SOL price from Jupiter (mock fallback)."""
    price = await fetch_sol_price()
    return {"token": "SOL", "price_usd": price}


@app.get("/api/pools", tags=["Pools"])
async def get_all_pools(
    liquidity_usd: float = Query(10_000.0, description="Simulated position size in USD"),
    days_active:   int   = Query(30,       description="Days the position has been active"),
):
    """
    Fetch all configured pools and run the full AI analysis pipeline on each.
    """
    pools = await fetch_all_pools()
    analyses = analyse_all_pools(pools, liquidity_usd=liquidity_usd, days_active=days_active)
    return {"count": len(analyses), "pools": analyses}


@app.get("/api/pools/{pool_id}", tags=["Pools"])
async def get_pool(
    pool_id: str,
    liquidity_usd: float = Query(10_000.0),
    days_active:   int   = Query(30),
):
    """Fetch one pool by ID and return its AI analysis."""
    try:
        pool = await fetch_pool_data(pool_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    analysis = analyse_pool(pool, liquidity_usd=liquidity_usd, days_active=days_active)
    return analysis


@app.get("/api/price-history/{token}", tags=["Market"])
async def price_history(
    token: str,
    days:  int = Query(30, ge=1, le=365, description="Number of days of history"),
):
    """
    Return hourly mock price history for a token.
    Supported tokens with realistic starting prices: SOL, RAY, mSOL.
    Any other token gets a random starting price.
    """
    history = await fetch_price_history(token=token, days=days)
    return {
        "token":   token.upper(),
        "days":    days,
        "points":  len(history),
        "history": history,
    }


@app.get("/api/wallet/{address}", tags=["Wallet"])
async def wallet_info(address: str):
    """
    Fetch on-chain wallet data: SOL balance, SPL token balances, LP positions.
    Uses live Solana RPC with mock fallback.
    """
    summary    = await get_wallet_summary(address)
    lp_pos     = await get_lp_positions(address)
    return {
        "wallet":       summary,
        "lp_positions": lp_pos,
    }


@app.post("/api/simulate", tags=["Simulation"])
async def simulate(req: SimulateRequest):
    """
    Simulate an LP position with custom parameters.
    Returns IL, fee income, net PnL, and health assessment.
    """
    position = LPPosition(
        pool_id=req.pool_id,
        token_a=req.token_a,
        token_b=req.token_b,
        initial_price=req.initial_price,
        current_price=req.current_price,
        liquidity_usd=req.liquidity_usd,
        fee_tier=req.fee_tier,
        days_active=req.days_active,
        volume_24h=req.volume_24h,
    )
    result = simulate_position(position)
    return {
        "pool_id":             result.pool_id,
        "initial_value_usd":  result.initial_value_usd,
        "current_value_usd":  result.current_value_usd,
        "hold_value_usd":     result.hold_value_usd,
        "impermanent_loss_pct": result.impermanent_loss_pct,
        "fee_income_usd":     result.fee_income_usd,
        "net_pnl_usd":        result.net_pnl_usd,
        "net_pnl_pct":        result.net_pnl_pct,
    }


@app.get("/api/scenarios/{pool_id}", tags=["Simulation"])
async def scenarios(pool_id: str):
    """
    Return IL + PnL across 9 price-ratio scenarios (0.5x → 2x) for a pool.
    """
    pool = await fetch_pool_data(pool_id)
    results = simulate_pool_scenarios(pool)
    return {"pool_id": pool_id, "scenarios": results}


@app.get("/api/price-path/{token}", tags=["Simulation"])
async def price_path(
    token:     str,
    days:      int   = Query(30,   ge=1, le=365),
    daily_vol: float = Query(0.05, ge=0.001, le=1.0),
    drift:     float = Query(0.0,  ge=-1.0,  le=1.0),
):
    """
    Generate a GBM simulated forward price path for a token.
    Useful for scenario planning in the UI.
    """
    import config as _cfg
    start = _cfg.MOCK_START_PRICES.get(token.upper(), 100.0)
    path  = simulate_price_path(
        start_price=start,
        days=days,
        daily_vol=daily_vol,
        drift=drift,
    )
    return {"token": token.upper(), "days": days, "points": len(path), "path": path}


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
