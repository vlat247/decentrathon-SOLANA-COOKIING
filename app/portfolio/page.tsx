import StatCard from "@/components/StatCard";
import Link from "next/link";

export default function Portfolio() {
  return (
    <>
      <div className="grid grid-cols-3 gap-2.5">
        <StatCard 
          label="Wallet" 
          value={<div className="font-mono text-[12px] text-[var(--purple)] mt-1">— not connected —</div>} 
        />
        <StatCard label="SOL Balance" value="0 SOL" valueColorClass="text-[var(--green)]" />
        <StatCard label="Total LP Value" value="$24,817" />
      </div>

      <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4 mt-4">
        <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">Active LP Positions</div>
        <div className="flex flex-col gap-2.5">
          <div className="bg-[var(--bg3)] rounded-lg p-3 flex justify-between items-center">
            <div>
              <div className="text-[13px] font-medium">SOL / USDC</div>
              <div className="text-[11px] text-[var(--muted)] mt-[3px]">Range: $170 – $210 · Raydium CLMM</div>
            </div>
            <div className="text-right">
              <div className="text-[13px] text-[var(--green)] font-medium">+18.4%</div>
              <div className="mt-1.5"><span className="inline-flex items-center gap-[5px] px-[10px] py-1 rounded-[20px] text-[11px] font-semibold tracking-[0.5px] bg-[rgba(0,245,160,0.12)] text-[var(--green)] border border-[rgba(0,245,160,0.25)]">Health 87</span></div>
            </div>
          </div>
          
          <div className="bg-[var(--bg3)] rounded-lg p-3 flex justify-between items-center">
            <div>
              <div className="text-[13px] font-medium">RAY / SOL</div>
              <div className="text-[11px] text-[var(--muted)] mt-[3px]">Range: 0.041 – 0.068 · Raydium CLMM</div>
            </div>
            <div className="text-right">
              <div className="text-[13px] text-[var(--yellow)] font-medium">+4.1%</div>
              <div className="mt-1.5"><span className="inline-flex items-center gap-[5px] px-[10px] py-1 rounded-[20px] text-[11px] font-semibold tracking-[0.5px] bg-[rgba(251,191,36,0.12)] text-[var(--yellow)] border border-[rgba(251,191,36,0.25)]">Health 52</span></div>
            </div>
          </div>
          
          <div className="bg-[var(--bg3)] rounded-lg p-3 flex justify-between items-center">
            <div>
              <div className="text-[13px] font-medium">BONK / SOL</div>
              <div className="text-[11px] text-[var(--muted)] mt-[3px]">Range: 0.0000082 – 0.000012 · Orca</div>
            </div>
            <div className="text-right">
              <div className="text-[13px] text-[var(--red)] font-medium">−2.3%</div>
              <div className="mt-1.5"><span className="inline-flex items-center gap-[5px] px-[10px] py-1 rounded-[20px] text-[11px] font-semibold tracking-[0.5px] bg-[rgba(248,113,113,0.12)] text-[var(--red)] border border-[rgba(248,113,113,0.25)]">Health 28</span></div>
            </div>
          </div>
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
