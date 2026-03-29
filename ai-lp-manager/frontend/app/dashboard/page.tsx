"use client";

import { useEffect, useState } from "react";
import StatCard from "@/components/StatCard";
import LivePriceChart from "@/components/LivePriceChart";
import VolatilityBar from "@/components/VolatilityBar";

export default function Dashboard() {
  const [solPrice, setSolPrice] = useState(185.42);
  const [apy, setApy] = useState(47.3);
  const [aiSignal, setAiSignal] = useState({ text: '▲ INCREASE', cls: 'bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]' });

  useEffect(() => {
    const i1 = setInterval(() => {
      setSolPrice(prev => prev + (Math.random() - 0.48) * 0.8);
      setApy(47 + (Math.random() * 2 - 1));
    }, 2000);

    const signals = [
      { text: '▲ INCREASE', cls: 'bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]' },
      { text: '◆ HOLD', cls: 'bg-[rgba(251,191,36,0.12)] text-[var(--yellow)] border border-[rgba(251,191,36,0.25)]' },
      { text: '▼ EXIT', cls: 'bg-[rgba(248,113,113,0.12)] text-[var(--red)] border border-[rgba(248,113,113,0.25)]' },
    ];
    let sigIdx = 0;
    const i2 = setInterval(() => {
      if (Math.random() < 0.3) {
        sigIdx = (sigIdx + 1) % signals.length;
        setAiSignal(signals[sigIdx]);
      }
    }, 5000);
    return () => { clearInterval(i1); clearInterval(i2); };
  }, []);

  return (
    <>
      <div className="grid grid-cols-4 gap-2.5">
        <StatCard label="SOL / USDC" value={`$${solPrice.toFixed(2)}`} valueColorClass="text-[var(--green)]" />
        <StatCard label="Current APY" value={`${apy.toFixed(1)}%`} valueColorClass="text-[var(--purple)]" />
        <StatCard label="24h Volume" value="$2.41M" />
        <StatCard 
          label="AI Signal" 
          value={<span className={`inline-flex items-center gap-[5px] px-[10px] py-1 rounded-[20px] text-[11px] font-semibold tracking-[0.5px] ${aiSignal.cls}`}>{aiSignal.text}</span>} 
        />
      </div>

      <LivePriceChart />

      <VolatilityBar />
    </>
  );
}
