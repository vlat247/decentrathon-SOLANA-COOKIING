import asyncio
import json
import httpx
import websockets
import time

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/prices"

results = []

def add_result(endpoint, status_code, issues, passed):
    results.append({
        "Endpoint": endpoint,
        "Status": status_code,
        "Issues Found": ", ".join(issues) if issues else "None",
        "Pass/Fail": "PASS" if passed else "FAIL"
    })

async def test_wallet_connect():
    endpoint = "GET /api/wallet/connect?publicKey={publicKey}"
    issues = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/wallet/connect?publicKey=4xKj...9mPQ")
        status = resp.status_code
        if status != 200:
            issues.append(f"Expected 200, got {status}")
        else:
            data = resp.json()
            if "publicKey" not in data: issues.append("Missing publicKey")
            if "sol_balance" not in data: issues.append("Missing sol_balance")
            elif data["sol_balance"] is None: issues.append("sol_balance is null")
            if "spl_tokens" not in data: issues.append("Missing spl_tokens")
    except Exception as e:
        status = "Error"
        issues.append(str(e))
    
    add_result(endpoint, status, issues, len(issues)==0)

async def test_simulate():
    endpoint = "POST /api/simulate"
    issues = []
    try:
        payload = {
            "initial_amount": 10000,
            "time_period": 30,
            "pool": "SOL/USDC",
            "strategy": "balanced"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{BASE_URL}/api/simulate", json=payload)
        status = resp.status_code
        if status != 200:
            issues.append(f"Expected 200, got {status}")
            try:
                data = resp.json()
                issues.append(f"Response: {data}")
            except:
                pass
        else:
            data = resp.json()
            if "pool" not in data: issues.append("Missing pool")
            if "days" not in data: issues.append("Missing days")
            if "base" not in data: issues.append("Missing base")
            if "ai" not in data: issues.append("Missing ai")
            if "winner_delta_usd" not in data: issues.append("Missing winner_delta_usd")
            if "winner_delta_pct" not in data: issues.append("Missing winner_delta_pct")
            
            if "chart_data" not in data:
                issues.append("Missing chart_data")
            elif len(data["chart_data"]) != 30:
                issues.append(f"chart_data length {len(data['chart_data'])} != time_period {30}")
    except Exception as e:
        status = "Error"
        issues.append(str(e))
    
    add_result(endpoint, status, issues, len(issues)==0)

async def test_websocket():
    endpoint = "WebSocket ws://localhost:8000/ws/prices"
    issues = []
    status = "101"
    try:
        async with websockets.connect(WS_URL, close_timeout=1) as websocket:
            t0 = time.time()
            msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            t1 = time.time()
            
            data = json.loads(msg)
            if "pair" not in data: issues.append("Missing pair")
            if "price" not in data: issues.append("Missing price")
            if "apy" not in data: issues.append("Missing apy")
            if "volume_24h" not in data: issues.append("Missing volume_24h")
            if "volatility_score" not in data: 
                issues.append("Missing volatility_score")
            elif not (0 <= data["volatility_score"] <= 100):
                issues.append("volatility_score outside 0-100")
            if "ai_signal" not in data:
                issues.append("Missing ai_signal")
            elif data["ai_signal"] not in ["INCREASE", "HOLD", "EXIT"]:
                issues.append(f"Invalid ai_signal: {data['ai_signal']}")
            if "timestamp" not in data: issues.append("Missing timestamp")
            
            if (t1 - t0) > 5.0:
                issues.append("Message arrived > 5 seconds apart")
                
    except asyncio.TimeoutError:
        status = "Error"
        issues.append("WebSocket timeout or messages > 5s apart")
    except Exception as e:
        status = "Error"
        issues.append(f"WebSocket connection failed: {e}")
        
    add_result(endpoint, status, issues, len(issues)==0)

async def test_portfolio():
    endpoint = "GET /api/portfolio?publicKey={publicKey}"
    issues = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/portfolio?publicKey=4xKj...9mPQ")
        status = resp.status_code
        if status != 200:
            issues.append(f"Expected 200, got {status}")
        else:
            data = resp.json()
            if "total_lp_value_usd" not in data: issues.append("Missing total_lp_value_usd")
            if "positions" not in data: issues.append("Missing positions")
            else:
                for p in data["positions"]:
                    if "health_score" in p and not (0 <= p["health_score"] <= 100):
                        issues.append("health_score outside 0-100")
                    if "ai_recommendation" in p and p["ai_recommendation"] not in ["INCREASE", "HOLD", "EXIT"]:
                        issues.append(f"Invalid ai_recommendation: {p['ai_recommendation']}")
            if "recommendations" not in data: issues.append("Missing recommendations")
    except Exception as e:
        status = "Error"
        issues.append(str(e))
    add_result(endpoint, status, issues, len(issues)==0)

async def test_ai_decisions():
    endpoint = "GET /api/ai-decisions?limit=10"
    issues = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/ai-decisions?limit=10")
        status = resp.status_code
        if status != 200:
            issues.append(f"Expected 200, got {status}")
        else:
            data = resp.json()
            if "decisions" not in data: issues.append("Missing decisions")
            else:
                for d in data["decisions"]:
                    if "action" in d and d["action"] not in ["INCREASE", "HOLD", "EXIT"]:
                        issues.append(f"Invalid action: {d['action']}")
    except Exception as e:
        status = "Error"
        issues.append(str(e))
    add_result(endpoint, status, issues, len(issues)==0)

async def main():
    await test_wallet_connect()
    await test_simulate()
    await test_websocket()
    await test_portfolio()
    await test_ai_decisions()
    
    print("| Endpoint | Status | Issues Found | Pass/Fail |")
    print("|---|---|---|---|")
    for r in results:
        print(f"| {r['Endpoint']} | {r['Status']} | {r['Issues Found']} | {r['Pass/Fail']} |")

if __name__ == "__main__":
    asyncio.run(main())
