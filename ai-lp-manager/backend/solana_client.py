"""
solana_client.py — Solana Blockchain Client for AI LP Manager

Provides async helpers to:
  - Fetch a wallet's SOL balance
  - Fetch SPL token balances for known mints
  - Fetch on-chain LP token account info (mocked Raydium account parsing)
  - Fetch recent transactions for an address

All methods fall back to realistic mock data on any error so the rest of
the application never crashes due to RPC issues.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

import config

# ---------------------------------------------------------------------------
# Known SPL token mints (mainnet)
# ---------------------------------------------------------------------------

KNOWN_MINTS: dict[str, str] = {
    "So11111111111111111111111111111111111111112":  "SOL",   # Wrapped SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R": "RAY",
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So":  "mSOL",
}

# Default Solana RPC endpoint (public — no API key required)
RPC_URL = "https://api.mainnet-beta.solana.com"


# ---------------------------------------------------------------------------
# Low-level JSON-RPC helper
# ---------------------------------------------------------------------------

async def _rpc(method: str, params: list) -> dict:
    """
    Send a single Solana JSON-RPC request.
    Raises httpx.HTTPError or KeyError on failure.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as client:
        resp = await client.post(RPC_URL, json=payload)
        resp.raise_for_status()
        body = resp.json()
        if "error" in body:
            raise RuntimeError(f"RPC error: {body['error']}")
        return body["result"]


# ---------------------------------------------------------------------------
# 1. SOL balance
# ---------------------------------------------------------------------------

async def get_sol_balance(wallet_address: str) -> float:
    """
    Return the SOL balance of a wallet (in SOL, not lamports).
    Falls back to mock on any error.
    """
    try:
        result = await _rpc(
            "getBalance",
            [wallet_address, {"commitment": "confirmed"}],
        )
        lamports = result["value"]
        sol = lamports / 1_000_000_000.0
        print(f"[LIVE] Wallet {wallet_address[:8]}… SOL balance: {sol:.4f}")
        return sol
    except Exception as exc:
        sol = random.uniform(0.5, 50.0)
        print(f"[MOCK] SOL balance: {sol:.4f}  (reason: {exc})")
        return sol


# ---------------------------------------------------------------------------
# 2. SPL token balances
# ---------------------------------------------------------------------------

async def get_token_balances(wallet_address: str) -> list[dict]:
    """
    Return a list of SPL token balances for the wallet.
    Each entry: {mint, symbol, amount, decimals, ui_amount}
    Falls back to mock on error.
    """
    try:
        result = await _rpc(
            "getTokenAccountsByOwner",
            [
                wallet_address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed", "commitment": "confirmed"},
            ],
        )
        balances = []
        for account in result.get("value", []):
            info = (
                account["account"]["data"]["parsed"]["info"]
            )
            mint = info["mint"]
            token_amount = info["tokenAmount"]
            balances.append(
                {
                    "mint":      mint,
                    "symbol":    KNOWN_MINTS.get(mint, "UNKNOWN"),
                    "amount":    int(token_amount["amount"]),
                    "decimals":  token_amount["decimals"],
                    "ui_amount": float(token_amount["uiAmount"] or 0),
                }
            )
        print(f"[LIVE] Fetched {len(balances)} token accounts for {wallet_address[:8]}…")
        return balances
    except Exception as exc:
        mock_balances = [
            {"mint": m, "symbol": s, "amount": 0, "decimals": 6,
             "ui_amount": round(random.uniform(10, 5000), 2)}
            for m, s in list(KNOWN_MINTS.items())[:4]
        ]
        print(f"[MOCK] Token balances ({len(mock_balances)} tokens)  (reason: {exc})")
        return mock_balances


# ---------------------------------------------------------------------------
# 3. Full wallet summary
# ---------------------------------------------------------------------------

async def get_wallet_summary(wallet_address: str) -> dict:
    """
    Fetch SOL balance + SPL token balances and bundle into one dict.
    Always returns something — mocks on error.
    """
    sol_balance    = await get_sol_balance(wallet_address)
    token_balances = await get_token_balances(wallet_address)

    return {
        "wallet":    wallet_address,
        "sol":       round(sol_balance, 6),
        "tokens":    token_balances,
        "total_tokens": len(token_balances),
    }


# ---------------------------------------------------------------------------
# 4. Recent transactions (mock — on-chain tx parsing is complex)
# ---------------------------------------------------------------------------

async def get_recent_transactions(
    wallet_address: str,
    limit: int = 10,
) -> list[dict]:
    """
    Return the most recent `limit` transaction signatures for a wallet.
    Returns mock data if RPC call fails.
    """
    try:
        result = await _rpc(
            "getSignaturesForAddress",
            [wallet_address, {"limit": limit, "commitment": "confirmed"}],
        )
        txs = []
        for tx in result:
            txs.append(
                {
                    "signature": tx["signature"],
                    "slot":      tx.get("slot"),
                    "block_time": tx.get("blockTime"),
                    "err":       tx.get("err"),
                    "memo":      tx.get("memo"),
                }
            )
        print(f"[LIVE] Fetched {len(txs)} transactions for {wallet_address[:8]}…")
        return txs
    except Exception as exc:
        now = datetime.now(tz=timezone.utc)
        mock_txs = [
            {
                "signature": f"mock_tx_{i}_{''.join(random.choices('abcdef0123456789', k=32))}",
                "slot":      random.randint(200_000_000, 250_000_000),
                "block_time": int((now - timedelta(hours=i * 6)).timestamp()),
                "err":       None,
                "memo":      random.choice(["LP Add", "LP Remove", "Swap", "Stake"]),
            }
            for i in range(limit)
        ]
        print(f"[MOCK] Transactions ({len(mock_txs)})  (reason: {exc})")
        return mock_txs


# ---------------------------------------------------------------------------
# 5. LP position on-chain stub
# ---------------------------------------------------------------------------

async def get_lp_positions(wallet_address: str) -> list[dict]:
    """
    Stub for fetching on-chain Raydium LP token accounts.
    Parsing AMM-specific account layouts requires decoding binary data;
    this returns realistic mock positions for now.
    """
    pools = ["SOL-USDC", "SOL-USDT", "RAY-USDC", "mSOL-SOL"]
    positions = []
    for pool in random.sample(pools, k=random.randint(1, 3)):
        positions.append(
            {
                "pool":           pool,
                "lp_token_amount": round(random.uniform(0.1, 100.0), 6),
                "share_pct":      round(random.uniform(0.0001, 0.5), 6),
                "value_usd":      round(random.uniform(500, 50_000), 2),
                "source":         "mock",
            }
        )
    print(f"[MOCK] LP positions for {wallet_address[:8]}…: {len(positions)} found")
    return positions
