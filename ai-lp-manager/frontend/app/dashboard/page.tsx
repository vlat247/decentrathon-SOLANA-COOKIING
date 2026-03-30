"use client";

import { usePriceStream } from "../../hooks/usePriceStream";
import StatCard from "@/components/StatCard";
import LivePriceChart from "@/components/LivePriceChart";
import VolatilityBar from "@/components/VolatilityBar";

export default function Dashboard() {
  const live = usePriceStream();
  const [volume24h, setVolume24h] = (require("react").useState)(null);

  (require("react").useEffect)(() => {
    async function fetchPools() {
      try {
        const res = await fetch("http://localhost:8000/api/pools");
        if (!res.ok) throw new Error("Failed to fetch pools");
        const pools = await res.json();
        const solPool = pools.find((p: any) => p.id === 'SOL-USDC');
        if (solPool) setVolume24h(solPool.volume_24h);
      } catch (err) {
        console.error("Pool fetch error:", err);
      }
    }
    fetchPools();
  }, []);

  const solPrice = live?.price ?? null;
  const apy = live?.apy ?? null;
  
  const aiSignal = {
    text: live?.signal ? (live.signal === 'INCREASE' ? '▲ INCREASE' : live.signal === 'HOLD' ? '◆ HOLD' : live.signal === 'REDUCE' ? '▼ REDUCE' : '■ EXIT') : '...',
    cls: live?.signal === 'INCREASE' 
      ? 'bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]'
      : live?.signal === 'HOLD'
      ? 'bg-[rgba(167,139,250,0.12)] text-[var(--purple)] border border-[rgba(167,139,250,0.25)]'
      : live?.signal === 'REDUCE'
      ? 'bg-[rgba(251,191,36,0.12)] text-[var(--yellow)] border border-[rgba(251,191,36,0.25)]'
      : live?.signal === 'EXIT'
      ? 'bg-[rgba(248,113,113,0.12)] text-[var(--red)] border border-[rgba(248,113,113,0.25)]'
      : 'bg-[rgba(255,255,255,0.1)] text-[#fff]'
  };

  return (
    <>
      <div className="grid grid-cols-4 gap-2.5">
        <StatCard 
            label="SOL / USDC" 
            value={solPrice !== null && solPrice !== 0.0 ? `$${solPrice.toFixed(2)}` : "Loading..."} 
            valueColorClass="text-[var(--green)]" 
        />
        <StatCard 
            label="Current APY" 
            value={apy !== null && apy !== 0.0 ? `${apy.toFixed(1)}%` : "Loading..."} 
            valueColorClass="text-[var(--purple)]" 
        />
        <StatCard 
          label="24h Volume" 
          value={volume24h !== null && volume24h !== 0.0 ? `$${(volume24h / 1000000).toFixed(2)}M` : "Loading..."} 
        />
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
