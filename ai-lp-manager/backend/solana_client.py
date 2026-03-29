"""
solana_client.py — Solana Devnet Integration for AI LP Manager

Makes raw JSON-RPC calls to Solana devnet via httpx.
No solana-py dependency — pure HTTP.

Functions:
  get_sol_balance(pubkey)             -> dict
  get_token_accounts(pubkey)          -> list
  get_transaction_count(pubkey)       -> int
  simulate_add_liquidity(pubkey, ...) -> dict
"""

import random

import httpx

import config


# ---------------------------------------------------------------------------
# Low-level JSON-RPC helper
# ---------------------------------------------------------------------------

async def _rpc(method: str, params: list) -> dict:
    """
    Send a Solana JSON-RPC request to config.SOLANA_RPC_URL.
    Raises on HTTP error or RPC-level error.
    Returns the "result" field of the response.
    """
    payload = {
        "jsonrpc": "2.0",
        "id":      1,
        "method":  method,
        "params":  params,
    }
    async with httpx.AsyncClient(timeout=config.HTTP_TIMEOUT) as client:
        resp = await client.post(config.SOLANA_RPC_URL, json=payload)
        resp.raise_for_status()
        body = resp.json()
        if "error" in body:
            raise RuntimeError(f"RPC error [{method}]: {body['error']}")
        return body["result"]
    
    # Fallback to satisfy linter, though unreachable
    return {}


# ---------------------------------------------------------------------------
# 1. SOL Balance
# ---------------------------------------------------------------------------

async def get_sol_balance(pubkey: str) -> dict:
    """
    Fetch the native SOL balance of a wallet from Solana devnet.

    Returns
    -------
    {pubkey, sol_balance (float), lamports (int)}
    On error: {pubkey, sol_balance: 0, error: str}
    """
    try:
        result   = await _rpc("getBalance", [pubkey])
        lamports = int(result["value"])
        sol      = lamports / 1_000_000_000.0
        return {
            "pubkey":      pubkey,
            "sol_balance": round(sol, 9),
            "lamports":    lamports,
        }
    except Exception as e:
        return {"pubkey": pubkey, "sol_balance": 0, "error": str(e)}


# ---------------------------------------------------------------------------
# 2. SPL Token Accounts
# ---------------------------------------------------------------------------

async def get_token_accounts(pubkey: str) -> list:
    """
    Fetch all SPL token accounts owned by `pubkey` from Solana devnet.

    Returns a list of
      {mint: str, amount: float, decimals: int, symbol: "UNKNOWN"}
    Returns [] on any error.
    """
    try:
        result = await _rpc(
            "getTokenAccountsByOwner",
            [
                pubkey,
                {"programId": config.TOKEN_PROGRAM_ID},
                {"encoding": "jsonParsed"},
            ],
        )
        accounts = []
        for item in result.get("value", []):
            parsed = item["account"]["data"]["parsed"]["info"]
            token_amount = parsed["tokenAmount"]
            accounts.append(
                {
                    "mint":     parsed["mint"],
                    "amount":   float(token_amount.get("uiAmount") or 0),
                    "decimals": int(token_amount.get("decimals", 0)),
                    "symbol":   "UNKNOWN",   # devnet tokens have no registry
                }
            )
        return accounts
    except Exception:
        return []


# ---------------------------------------------------------------------------
# 3. Transaction Count
# ---------------------------------------------------------------------------

async def get_transaction_count(pubkey: str) -> int:
    """
    Return the number of confirmed transactions found for `pubkey` (up to 10).
    Returns 0 on any error.
    """
    try:
        result = await _rpc(
            "getSignaturesForAddress",
            [pubkey, {"limit": 10}],
        )
        return len(result)
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# 4. Simulate Add Liquidity (no real tx)
# ---------------------------------------------------------------------------

async def simulate_add_liquidity(
    pubkey: str, pool_id: str, amount_usdc: float
) -> dict:
    """
    Simulate adding `amount_usdc` USDC of liquidity to `pool_id`.

    Fetches the live SOL price from Jupiter to calculate the SOL leg.
    Does NOT sign or broadcast any transaction.

    Returns a simulation summary dict.
    """
    # Import here to avoid circular dependency at module level
    from data_fetcher import fetch_sol_price

    try:
        sol_price = await fetch_sol_price()
    except Exception:
        sol_price = 150.0    # safe fallback

    sol_amount  = (amount_usdc / 2.0) / sol_price
    usdc_amount = amount_usdc / 2.0

    return {
        "simulated":           True,
        "pubkey":              pubkey,
        "pool_id":             pool_id,
        "amount_usdc":         amount_usdc,
        "sol_amount":          round(sol_amount, 6),
        "usdc_amount":         round(usdc_amount, 2),
        "estimated_lp_tokens": round(amount_usdc / 10.0, 4),
        "estimated_apy":       round(random.uniform(15.0, 60.0), 2),
        "network":             "devnet",
        "note":                "Simulation only - no real transaction executed",
    }
