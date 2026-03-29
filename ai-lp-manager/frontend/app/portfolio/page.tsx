"use client";

import StatCard from "@/components/StatCard";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useWallet, useConnection } from "@solana/wallet-adapter-react";
import { LAMPORTS_PER_SOL } from "@solana/web3.js";
import { getAIDecision } from "../../api/aiDecision";
import { fetchWallet } from "../../api/wallet";

function PositionCard({ pool }: { pool: any }) {
  const [decision, setDecision] = useState<any>(null);

  useEffect(() => {
    getAIDecision(pool.id)
      .then(setDecision)
      .catch((err) => console.log('Failed to fetch AI decision for', pool.id, err));
  }, [pool.id]);

  return (
    <div className="bg-[var(--bg3)] rounded-lg p-3 flex justify-between items-center">
      <div>
        <div className="text-[13px] font-medium">{pool.name}</div>
        <div className="text-[11px] text-[var(--muted)] mt-[3px]">{pool.desc}</div>
      </div>
      <div className="text-right">
        <div className={`text-[13px] font-medium ${pool.pnl >= 0 ? 'text-[var(--green)]' : 'text-[var(--red)]'}`}>
          {pool.pnl >= 0 ? '+' : ''}{pool.pnl}%
        </div>
        <div className="mt-1.5 flex gap-2 justify-end">
          {decision && (
            <span className={`inline-flex items-center gap-[5px] px-[10px] py-1 rounded-[20px] text-[11px] font-semibold tracking-[0.5px] ${
              decision.action === 'INCREASE' ? 'bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]' :
              decision.action === 'HOLD' ? 'bg-[rgba(251,191,36,0.12)] text-[var(--yellow)] border border-[rgba(251,191,36,0.25)]' :
              'bg-[rgba(248,113,113,0.12)] text-[var(--red)] border border-[rgba(248,113,113,0.25)]'
            }`}>
              {decision.action} · {(decision.confidence * 100).toFixed(0)}%
            </span>
          )}
          <span className={`inline-flex items-center gap-[5px] px-[10px] py-1 rounded-[20px] text-[11px] font-semibold tracking-[0.5px] ${pool.health >= 80 ? 'bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]' : pool.health >= 50 ? 'bg-[rgba(251,191,36,0.12)] text-[var(--yellow)] border border-[rgba(251,191,36,0.25)]' : 'bg-[rgba(248,113,113,0.12)] text-[var(--red)] border border-[rgba(248,113,113,0.25)]'}`}>
            Health {pool.health}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Portfolio() {
  const { publicKey, connected } = useWallet();
  const { connection } = useConnection();
  const [walletData, setWalletData] = useState<any>(null);
  const [nativeBalance, setNativeBalance] = useState<number | null>(null);

  useEffect(() => {
    if (connected && publicKey) {
      connection.getBalance(publicKey).then(lamports => setNativeBalance(lamports / LAMPORTS_PER_SOL)).catch(console.error);
      
      fetchWallet(publicKey.toBase58())
        .then(setWalletData)
        .catch((err) => console.log('Wallet fetch failed', err));
    } else {
      setWalletData(null);
      setNativeBalance(null);
    }
  }, [connected, publicKey, connection]);

  return (
    <>
      <div className="grid grid-cols-3 gap-2.5">
        <StatCard 
          label="Wallet" 
          value={<div className="font-mono text-[12px] text-[var(--purple)] mt-1">{publicKey ? `${publicKey.toBase58().slice(0, 4)}...${publicKey.toBase58().slice(-4)}` : '— not connected —'}</div>} 
        />
        <StatCard label="SOL Balance" value={nativeBalance !== null ? `${nativeBalance.toFixed(2)} SOL` : walletData ? `${walletData.solBalance.toFixed(2)} SOL` : '0 SOL'} valueColorClass="text-[var(--green)]" />
        <StatCard label="Total LP Value" value="$24,817" />
      </div>

      <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4 mt-4">
        <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">Active LP Positions</div>
        <div className="flex flex-col gap-2.5">
          <PositionCard pool={{ id: 'SOL-USDC', name: 'SOL / USDC', desc: 'Range: $170 – $210 · Raydium CLMM', pnl: 18.4, health: 87 }} />
          <PositionCard pool={{ id: 'RAY-SOL', name: 'RAY / SOL', desc: 'Range: 0.041 – 0.068 · Raydium CLMM', pnl: 4.1, health: 52 }} />
          <PositionCard pool={{ id: 'BONK-SOL', name: 'BONK / SOL', desc: 'Range: 0.0000082 – 0.000012 · Orca', pnl: -2.3, health: 28 }} />
        </div>
      </div>

      <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4 mt-4">
        <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">AI Recommendations</div>
        <div className="flex flex-col gap-2">
          
          <div className="rounded-lg py-2.5 px-3 flex justify-between items-center bg-[rgba(0,245,160,0.06)] border border-[rgba(0,245,160,0.15)]">
            <div>
              <div className="text-[12px] text-[var(--green)] font-medium">Widen SOL/USDC range</div>
              <div className="text-[11px] text-[var(--muted)] mt-0.5">Volatility spike predicted in ~4h</div>
            </div>
            <Link href="/simulate" className="text-[11px] px-2.5 py-1.5 bg-transparent rounded cursor-pointer font-sans transition-opacity hover:opacity-75 border border-[var(--green)] text-[var(--green)]">
              Simulate ↗
            </Link>
          </div>
          
          <div className="rounded-lg py-2.5 px-3 flex justify-between items-center bg-[rgba(251,191,36,0.06)] border border-[rgba(251,191,36,0.15)]">
            <div>
              <div className="text-[12px] text-[var(--yellow)] font-medium">Rebalance RAY/SOL position</div>
              <div className="text-[11px] text-[var(--muted)] mt-0.5">Out of range 23% of the last 24h</div>
            </div>
            <Link href="/simulate" className="text-[11px] px-2.5 py-1.5 bg-transparent rounded cursor-pointer font-sans transition-opacity hover:opacity-75 border border-[var(--yellow)] text-[var(--yellow)]">
              Simulate ↗
            </Link>
          </div>
          
          <div className="rounded-lg py-2.5 px-3 flex justify-between items-center bg-[rgba(248,113,113,0.06)] border border-[rgba(248,113,113,0.15)]">
            <div>
              <div className="text-[12px] text-[var(--red)] font-medium">Exit BONK/SOL position</div>
              <div className="text-[11px] text-[var(--muted)] mt-0.5">IL exceeds fee income — remove liquidity</div>
            </div>
            <Link href="/simulate" className="text-[11px] px-2.5 py-1.5 bg-transparent rounded cursor-pointer font-sans transition-opacity hover:opacity-75 border border-[var(--red)] text-[var(--red)]">
              Simulate ↗
            </Link>
          </div>
          
        </div>
      </div>
    </>
  );
}
