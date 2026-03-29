<<<<<<< HEAD
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

# Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

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

/backend # AI logic, simulation, API

/frontend # React + charts for visualization

/data # sample data or API integration

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

> > > > > > > 8e1b7efd529a72c3dba2913c86f7af3938299ecc
