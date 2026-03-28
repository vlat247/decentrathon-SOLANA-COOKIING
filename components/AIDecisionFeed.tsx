"use client";

import { useState } from "react";

const initialDecisions = [
  {time:'14:32:01',action:'INCREASE',reason:'Vol dropped, fees rising',cls:'bg-[var(--green)]'},
  {time:'14:28:44',action:'HOLD',reason:'Price in mid-range',cls:'bg-[var(--yellow)]'},
  {time:'14:21:10',action:'HOLD',reason:'Monitoring volatility',cls:'bg-[var(--yellow)]'},
  {time:'14:15:33',action:'EXIT',reason:'IL threshold exceeded',cls:'bg-[var(--red)]'},
  {time:'14:09:07',action:'INCREASE',reason:'APY spike detected',cls:'bg-[var(--green)]'},
  {time:'14:01:22',action:'HOLD',reason:'Rebalancing in progress',cls:'bg-[var(--yellow)]'},
  {time:'13:55:48',action:'INCREASE',reason:'Low gas, good entry',cls:'bg-[var(--green)]'},
  {time:'13:47:30',action:'EXIT',reason:'Price leaving range',cls:'bg-[var(--red)]'},
  {time:'13:41:05',action:'HOLD',reason:'Awaiting momentum',cls:'bg-[var(--yellow)]'},
  {time:'13:33:18',action:'INCREASE',reason:'Fee APY 62% — go',cls:'bg-[var(--green)]'},
];

export default function AIDecisionFeed() {
  const [decisions] = useState(initialDecisions);

  return (
    <div className="flex flex-col">
      {decisions.map((d, i) => (
        <div key={i} className="py-2.5 border-b border-lp-border last:border-none flex flex-col gap-1">
          <div className="font-mono text-[9px] text-[var(--muted)]">{d.time}</div>
          <div className="text-[12px] text-[var(--text)] leading-[1.4] flex items-center">
            <span className={`w-2 h-2 rounded-full inline-block mr-1 shrink-0 ${d.cls}`}></span>
            {d.action}
          </div>
          <div className="text-[11px] text-[var(--muted)] italic">{d.reason}</div>
        </div>
      ))}
    </div>
  );
}
