"use client";

import { usePriceStream } from "../../hooks/usePriceStream";
import StatCard from "@/components/StatCard";
import LivePriceChart from "@/components/LivePriceChart";
import VolatilityBar from "@/components/VolatilityBar";

export default function Dashboard() {
  const live = usePriceStream();

  const solPrice = live?.price ?? 185.42;
  const apy = live?.apy ?? 47.3;
  
  const aiSignal = {
    text: live?.signal ? (live.signal === 'INCREASE' ? '▲ INCREASE' : live.signal === 'HOLD' ? '◆ HOLD' : '▼ EXIT') : '...',
    cls: live?.signal === 'INCREASE' 
      ? 'bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]'
      : live?.signal === 'HOLD'
      ? 'bg-[rgba(251,191,36,0.12)] text-[var(--yellow)] border border-[rgba(251,191,36,0.25)]'
      : live?.signal === 'EXIT'
      ? 'bg-[rgba(248,113,113,0.12)] text-[var(--red)] border border-[rgba(248,113,113,0.25)]'
      : 'bg-[rgba(255,255,255,0.1)] text-[#fff]'
  };

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

      <LivePriceChart livePrice={solPrice} liveSignal={live?.signal} />

      <VolatilityBar />
    </>
  );
}
