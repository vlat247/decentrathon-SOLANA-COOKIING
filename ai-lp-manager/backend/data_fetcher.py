"""
data_fetcher.py — Real market data fetcher with caching and safe fallbacks
Fetches SOL price from Jupiter, Raydium pool data from DefiLlama/Raydium, 
and price history from CoinGecko/DexScreener.
"""

import asyncio
import time
from datetime import datetime, timezone

import httpx

import config

# ---------------------------------------------------------------------------
# Caching Layer (TTL = 90 seconds)
# ---------------------------------------------------------------------------

CACHE_TTL = 90

class CacheStore:
    def __init__(self):
        self.store = {}
        self.lock = asyncio.Lock()

    async def get(self, key: str):
        async with self.lock:
            if key in self.store:
                item = self.store[key]
                if time.time() - item['timestamp'] < CACHE_TTL:
                    return item['data']
            return None

    async def get_stale(self, key: str):
        """Return cached data ignoring TTL"""
        async with self.lock:
            if key in self.store:
                return self.store[key]['data']
            return None

    async def set(self, key: str, data):
        async with self.lock:
            self.store[key] = {
                'data': data,
                'timestamp': time.time()
            }

global_cache = CacheStore()

# ---------------------------------------------------------------------------
# Robust API Request Wrapper
# ---------------------------------------------------------------------------

async def _fetch_with_retry(url: str, params: dict = None, retries: int = 2) -> httpx.Response:
    timeout = httpx.Timeout(5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(retries + 1):
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp
            except httpx.HTTPError as exc:
                if attempt == retries:
                    print(f"[ERROR] API failed: {exc}")
                    raise
                await asyncio.sleep(1)

# ---------------------------------------------------------------------------
# 1. SOL spot price
# ---------------------------------------------------------------------------

async def fetch_sol_price() -> float:
    """Fetch live SOL price from CoinGecko API."""
    cache_key = "sol_price"
    cached = await global_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        resp = await _fetch_with_retry(url, params={"ids": "solana", "vs_currencies": "usd"})
        price = float(resp.json()["solana"]["usd"])
        print("[DATA] Source: CoinGecko (SOL Price)")
        await global_cache.set(cache_key, price)
        return price
    except Exception as exc:
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            resp = await _fetch_with_retry(url, params={"symbol": "SOLUSDT"})
            price = float(resp.json()["price"])
            print("[DATA] Source: Binance (SOL Price)")
            await global_cache.set(cache_key, price)
            return price
        except Exception as exc2:
            stale = await global_cache.get_stale(cache_key)
            if stale is not None:
                print("[DATA] Source: Cache (Fallback) - SOL Price")
                return stale
            return 150.0


# ---------------------------------------------------------------------------
# 2. Hourly price history (Real Data)
# ---------------------------------------------------------------------------

COINGECKO_MAP = {
    "SOL": "solana",
    "USDC": "usd-coin",
    "RAY": "raydium",
    "MSOL": "msol",
    "BONK": "bonk"
}

DEXSCREENER_MAP = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "MSOL": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
}

async def fetch_price_history(token: str, days: int = 30) -> list:
    """
    Fetch realistic hourly price history for a token using CoinGecko or DexScreener.
    """
    token_upper = token.upper()
    cache_key = f"history_{token_upper}_{days}"
    
    cached = await global_cache.get(cache_key)
    if cached is not None:
        return cached

    if token_upper not in COINGECKO_MAP:
        print(f"[ERROR] API failed: Token '{token_upper}' not in ID map")
        stale = await global_cache.get_stale(cache_key)
        return stale if stale is not None else []

    cg_id = COINGECKO_MAP[token_upper]
    url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days), "interval": "hourly"}
    
    try:
        resp = await _fetch_with_retry(url, params=params)
        data = resp.json()
        
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        
        history = []
        for i, (ts_ms, price) in enumerate(prices):
            ts = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
            vol = volumes[i][1] if i < len(volumes) else 0.0
            history.append({
                "timestamp": ts.isoformat(),
                "price": round(price, 6),
                "volume": round(vol, 2)
            })
            
        print("[DATA] Source: CoinGecko")
        await global_cache.set(cache_key, history)
        return history
        
    except Exception as exc:
        pass # CoinGecko failed, logged by _fetch_with_retry

    try:
        if token_upper in DEXSCREENER_MAP:
            ds_id = DEXSCREENER_MAP[token_upper]
            ds_url = f"https://api.dexscreener.com/latest/dex/tokens/{ds_id}"
            ds_resp = await _fetch_with_retry(ds_url)
            ds_data = ds_resp.json()
            pairs = ds_data.get("pairs", [])
            if pairs:
                current_price = float(pairs[0].get("priceUsd", 0))
                current_vol = float(pairs[0].get("volume", {}).get("h24", 0))
                fallback_history = [{
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "price": round(current_price, 6),
                    "volume": round(current_vol, 2)
                }]
                print("[DATA] Source: DexScreener (fallback)")
                return fallback_history
    except Exception as e:
        pass # DexScreener failed, logged by _fetch_with_retry

    stale = await global_cache.get_stale(cache_key)
    if stale is not None:
        print("[DATA] Source: Cache (Fallback) - History")
        return stale
        
    return []


# ---------------------------------------------------------------------------
# 3. Single pool data
# ---------------------------------------------------------------------------

async def _fetch_defillama_pools():
    cache_key = "defillama_pools"
    cached = await global_cache.get(cache_key)
    if cached is not None:
        return cached
        
    try:
        resp = await _fetch_with_retry("https://yields.llama.fi/pools")
        data = resp.json()
        pools = data.get("data", [])
        filtered = [p for p in pools if p.get("chain") == "Solana" and p.get("project") == "raydium"]
        print("[DATA] Source: DefiLlama")
        await global_cache.set(cache_key, filtered)
        return filtered
    except Exception as exc:
        stale = await global_cache.get_stale(cache_key)
        return stale if stale is not None else []


async def _fetch_raydium_pairs():
    cache_key = "raydium_pairs"
    cached = await global_cache.get(cache_key)
    if cached is not None:
        return cached
        
    try:
        resp = await _fetch_with_retry(config.RAYDIUM_PAIRS_URL)
        data = resp.json()
        print("[DATA] Source: Raydium (fallback)")
        await global_cache.set(cache_key, data)
        return data
    except Exception as exc:
        stale = await global_cache.get_stale(cache_key)
        return stale if stale is not None else []


async def fetch_pool_data(pool_id: str) -> dict:
    """
    Fetch data for one Raydium pool by its pair name (e.g. 'SOL-USDC').
    """
    cache_key = f"pool_{pool_id}"
    cached = await global_cache.get(cache_key)
    if cached is not None:
        return cached

    dl_pools = await _fetch_defillama_pools()
    match = next((p for p in dl_pools if p.get("symbol", "").upper() == pool_id.upper()), None)
    
    if match:
        result = {
            "id": pool_id,
            "apy": float(match.get("apy", 0) or 0),
            "price": float(match.get("price", 0) or 1.0),
            "volume_24h": float(match.get("volumeUsd1d", 0) or 0),
            "liquidity": float(match.get("tvlUsd", 0) or 0),
            "volatility": 0.05,
            "source": "DefiLlama"
        }
        await global_cache.set(cache_key, result)
        return result

    ray_pools = await _fetch_raydium_pairs()
    match_ray = next((p for p in ray_pools if p.get("name", "").upper() == pool_id.upper()), None)
    
    if match_ray:
        result = {
            "id": pool_id,
            "apy": float(match_ray.get("apy", 0) or 0),
            "price": float(match_ray.get("price", 0) or 1.0),
            "volume_24h": float(match_ray.get("volume", {}).get("h24", 0) if isinstance(match_ray.get("volume"), dict) else match_ray.get("volume24h", 0)),
            "liquidity": float(match_ray.get("liquidity", 0) or 0),
            "volatility": 0.05,
            "source": "Raydium"
        }
        await global_cache.set(cache_key, result)
        return result

    stale = await global_cache.get_stale(cache_key)
    if stale is not None:
        print(f"[DATA] Source: Cache (Fallback) - Pool {pool_id}")
        return stale

    print(f"[ERROR] API failed: Pool {pool_id} data unavailable entirely")
    return {
        "id": pool_id,
        "apy": 0.0,
        "price": 0.0,
        "volume_24h": 0.0,
        "liquidity": 0.0,
        "volatility": 0.05,
        "source": "fallback"
    }


# ---------------------------------------------------------------------------
# 4. All configured pools
# ---------------------------------------------------------------------------

async def fetch_all_pools() -> list:
    """
    Fetch data for all configured pools.
    """
    return list(await asyncio.gather(*[fetch_pool_data(p) for p in config.POOLS]))
