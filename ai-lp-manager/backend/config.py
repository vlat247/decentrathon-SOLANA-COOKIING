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

# HTTP client timeout (seconds)
HTTP_TIMEOUT = 5.0

# StrategyEngine decision thresholds (0.0 – 1.0 score scale)
SCORE_INCREASE = 0.70   # score >= this → INCREASE position
SCORE_REDUCE   = 0.40   # score <= this → REDUCE position
SCORE_EXIT     = 0.25   # score <= this → EXIT position
