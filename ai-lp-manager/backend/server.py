"""
server.py — FastAPI Server for AI LP Manager

Endpoints:
  GET  /api/health
  GET  /api/pools
  GET  /api/pools/{pool_id}
  GET  /api/price-history/{token}
  GET  /api/decide/{pool_id}
  POST /api/simulate
  GET  /api/wallet/{pubkey}
  POST /api/simulate-position
  GET  /api/market-data
  WS   /ws/prices
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
import ai_engine
import simulation
import solana_client
from data_fetcher import (
    fetch_all_pools,
    fetch_pool_data,
    fetch_price_history,
    fetch_sol_price,
)


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀  AI LP Manager API starting on devnet…")
    yield
    print("🛑  AI LP Manager API shutting down…")


app = FastAPI(
    title="AI LP Manager",
    version="1.0.0",
    description="AI-powered Liquidity Pool management for Solana / Raydium",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared engine + simulation instances
engine = ai_engine.get_engine()
sim    = simulation.SimulationEngine()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class SimulateRequest(BaseModel):
    pool_id:        str   = Field("SOL-USDC", example="SOL-USDC")
    initial_amount: float = Field(1000.0, gt=0, example=1000.0)
    days:           int   = Field(30, ge=1, le=365)


class SimulatePositionRequest(BaseModel):
    pubkey:      str   = Field(..., example="YourDevnetWalletAddress")
    pool_id:     str   = Field("SOL-USDC", example="SOL-USDC")
    amount_usdc: float = Field(500.0, gt=0, example=500.0)


class ContractPositionRequest(BaseModel):
    pubkey:  str
    pool_id: str


class PrepareTransactionRequest(BaseModel):
    pubkey:  str
    pool_id: str
    action:  str
    score:   int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0", "network": "devnet"}


# ── Pools ────────────────────────────────────────────────────────────────

@app.get("/api/pools", tags=["Pools"])
async def get_all_pools():
    """Fetch market data for all configured pools."""
    pools = await fetch_all_pools()
    return pools


@app.get("/api/pools/{pool_id}", tags=["Pools"])
async def get_pool(pool_id: str):
    """Fetch market data for a single pool."""
    return await fetch_pool_data(pool_id)


# ── Price history ─────────────────────────────────────────────────────────

@app.get("/api/price-history/{token}", tags=["Market"])
async def price_history(token: str, days: int = 30):
    """
    Return hourly mock price history for a token.
    Query param `days` controls the window (default 30).
    """
    history = await fetch_price_history(token=token, days=days)
    return history


# ── AI decision ───────────────────────────────────────────────────────────

@app.get("/api/decide/{pool_id}", tags=["AI"])
async def decide(pool_id: str):
    """
    Run the AI strategy engine for a pool and return the decision.
    Fetches live pool data + 30-day price history, then calls engine.decide().
    """
    token = pool_id.split("-")[0]   # "SOL-USDC" → "SOL"
    pool_data, price_history = await asyncio.gather(
        fetch_pool_data(pool_id),
        fetch_price_history(token=token, days=30),
    )
    return engine.decide(pool_data, price_history)


# ── Simulation ────────────────────────────────────────────────────────────

@app.post("/api/simulate", tags=["Simulation"])
async def simulate(req: SimulateRequest):
    """
    Backtest AI vs baseline strategy over historical price data.
    Body: {pool_id, initial_amount, days}
    """
    token = req.pool_id.split("-")[0]
    price_history = await fetch_price_history(token=token, days=req.days)
    result = sim.run(
        pool_id=req.pool_id,
        initial_amount=req.initial_amount,
        days=req.days,
        price_history=price_history,
    )
    return result


# ── Wallet ────────────────────────────────────────────────────────────────

@app.get("/api/wallet/{pubkey}", tags=["Wallet"])
async def wallet(pubkey: str):
    """
    Fetch on-chain devnet wallet info: SOL balance, SPL token accounts,
    and recent transaction count.
    """
    sol_info, tokens, tx_count = await asyncio.gather(
        solana_client.get_sol_balance(pubkey),
        solana_client.get_token_accounts(pubkey),
        solana_client.get_transaction_count(pubkey),
    )
    return {
        "pubkey":      pubkey,
        "sol_balance": sol_info.get("sol_balance", 0),
        "lamports":    sol_info.get("lamports", 0),
        "tokens":      tokens,
        "tx_count":    tx_count,
        "network":     "devnet",
        "error":       sol_info.get("error"),   # None if no error
    }


@app.post("/api/simulate-position", tags=["Wallet"])
async def simulate_position(req: SimulatePositionRequest):
    """
    Simulate adding liquidity to a pool (no real transaction).
    Calculates SOL/USDC split at current live price.
    """
    return await solana_client.simulate_add_liquidity(
        pubkey=req.pubkey,
        pool_id=req.pool_id,
        amount_usdc=req.amount_usdc,
    )


# ── Market snapshot ───────────────────────────────────────────────────────

@app.get("/api/market-data", tags=["Market"])
async def market_data():
    """
    Fetch SOL spot price and all pool data in parallel.
    Returns a combined snapshot with a server timestamp.
    """
    sol_price, pools = await asyncio.gather(
        fetch_sol_price(),
        fetch_all_pools(),
    )
    return {
        "sol_price": sol_price,
        "pools":     pools,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


# ── Contract Interaction ──────────────────────────────────────────────────

@app.get("/api/contract/position", tags=["Contract"])
async def get_position(owner: str, pool_id: str):
    """
    Fetch LpPosition on-chain data for a specific owner + pool_id.
    """
    return await solana_client.get_lp_position(owner, pool_id)


@app.post("/api/contract/prepare-transaction", tags=["Contract"])
async def prepare_transaction(req: PrepareTransactionRequest):
    """
    Generate transaction instructions for the AI LP Manager contract.
    Body: {pubkey, pool_id, action, score}
    """
    return await solana_client.prepare_lp_transaction(
        pubkey=req.pubkey,
        pool_id=req.pool_id,
        action=req.action,
        score=req.score,
    )


@app.get("/api/contract/info", tags=["Contract"])
async def contract_info():
    """
    Return basic information about the deployed Solana program.
    """
    return {
        "program_id": config.PROGRAM_ID,
        "network": "devnet",
        "explorer_url": f"https://explorer.solana.com/address/{config.PROGRAM_ID}?cluster=devnet",
        "status": "deployed"
    }


# ---------------------------------------------------------------------------
# WebSocket — live price stream
# ---------------------------------------------------------------------------

@app.websocket("/ws/prices")
async def ws_prices(websocket: WebSocket):
    """
    Stream live SOL price + AI decision for SOL-USDC every 10 seconds.

    Payload shape:
      {price, timestamp, action, score, confidence}
    """
    await websocket.accept()
    try:
        while True:
            sol_price, price_history = await asyncio.gather(
                fetch_sol_price(),
                fetch_price_history(token="SOL", days=7),
            )

            pool_data = {
                "id":         "SOL-USDC",
                "apy":        config.POOL_VOLUME_ESTIMATE * config.FEE_TIER * 365
                              / config.POOL_LIQUIDITY_ESTIMATE * 100,
                "volatility": 0.05,
            }
            decision = engine.decide(pool_data, price_history)

            await websocket.send_json(
                {
                    "price":      sol_price,
                    "timestamp":  datetime.now(tz=timezone.utc).isoformat(),
                    "action":     decision["action"],
                    "score":      decision["score"],
                    "confidence": decision["confidence"],
                }
            )
            await asyncio.sleep(10)

    except WebSocketDisconnect:
        print("[WS] Client disconnected from /ws/prices")
    except Exception as e:
        print(f"[WS] Error: {e}")
        await websocket.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
