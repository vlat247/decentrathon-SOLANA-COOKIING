"use client";
import { useEffect, useState } from "react";

export default function VolatilityBar() {
  const [v, setV] = useState(34);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setV(28 + Math.round(Math.random() * 24));
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4">
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">Pool Volatility Score</div>
          <div className="h-2 bg-[var(--bg3)] rounded overflow-hidden">
            <div 
              className="h-full rounded transition-all duration-1000 bg-gradient-to-r from-[var(--green)] to-[var(--yellow)]" 
              style={{ width: `${v}%` }}
            ></div>
          </div>
        </div>
        <div className="flex flex-col items-center justify-end h-full pt-[22px]">
            <span className="font-mono text-[13px] text-[var(--yellow)] min-w-[28px]">{v}</span>
        </div>
      </div>
      <div className="text-[11px] text-[var(--muted)] mt-2">Low volatility → AI maintaining current LP range</div>
    </div>
  );
}
