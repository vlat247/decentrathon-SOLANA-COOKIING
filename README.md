# decentrathon-SOLANA-COOKIING
Autonomous AI agent for Solana liquidity pools. Monitors prices, APY, and volatility, makes decisions (hold, increase, reduce, exit), simulates outcomes, and visualizes AI vs manual strategies. Demo-ready for hackathons.

AI Liquidity Manager (Solana Hackathon Project)
Autonomous AI agent for optimizing liquidity pool positions on Solana
This project demonstrates a proof-of-concept AI system that:
Monitors DeFi pools (Raydium / Orca)
Analyzes market data: token prices, APY, volatility, liquidity
Makes decisions autonomously: hold, increase, reduce, or exit liquidity positions
Simulates outcomes: compares “AI-managed strategy” vs. “manual hold strategy”
Visualizes results: interactive frontend showing price charts, AI decisions, and profitability comparison
🚀 Features
Data Layer: fetches or mocks market data (price, APY, liquidity)
Decision Engine: heuristic “AI” rules and scoring function
Simulation Engine: evaluates performance and impermanent loss
Frontend Visualization: charts showing AI actions and strategy outcomes
Backend API: connects frontend to AI and simulation engine
Optional Solana Integration: mock on-chain execution of trades
📂 Structure
/backend        # AI logic, simulation, API
/frontend       # React + charts for visualization
/data           # sample data or API integration
💡 Usage
Run the backend:
cd backend
python server.py
Start frontend:
cd frontend
npm install
npm start
Open browser → see charts, AI decisions, and performance comparison
⚖️ Why this project matters
Demonstrates AI interacting with on-chain DeFi
Shows improved LP profitability vs passive holding
Provides a hackathon-ready, visually compelling demo
