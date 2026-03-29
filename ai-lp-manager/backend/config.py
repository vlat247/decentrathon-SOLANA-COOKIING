# config.py — Central configuration for AI LP Manager

# Pool IDs to track (Raydium pair names)
POOLS = [
    "SOL-USDC",
    "SOL-USDT",
    "RAY-USDC",
    "mSOL-USDC",
    "mSOL-SOL",
]

# Starting prices for mock price history generation
MOCK_START_PRICES = {
    "SOL":  150.0,
    "RAY":  5.0,
    "mSOL": 160.0,
}

# API endpoints
JUPITER_PRICE_URL = "https://price.jup.ag/v4/price"
RAYDIUM_PAIRS_URL = "https://api.raydium.io/v2/main/pairs"

# Solana devnet RPC
SOLANA_RPC_URL  = "https://api.devnet.solana.com"
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

# Contract program ID (placeholder — update after anchor build)
LP_MANAGER_PROGRAM_ID = "CSjDhZXoYAeSa8mtsy7xgSRVqq2Bbeb9jSwf9RP5QVN6"

# CORS — origins allowed to call the API
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# HTTP client timeout (seconds)
HTTP_TIMEOUT = 2.0

# StrategyEngine decision thresholds (0.0 – 1.0 score scale)
SCORE_INCREASE = 0.70   # score >= this → INCREASE position
SCORE_REDUCE   = 0.40   # score <= this → REDUCE position
SCORE_EXIT     = 0.25   # score <= this → EXIT position

# Simulation / backtesting constants
FEE_TIER               = 0.003          # Raydium default pool fee (0.3%)
POOL_VOLUME_ESTIMATE   = 2_000_000.0    # estimated daily pool volume (USD)
POOL_LIQUIDITY_ESTIMATE = 10_000_000.0  # estimated total pool liquidity (USD)
