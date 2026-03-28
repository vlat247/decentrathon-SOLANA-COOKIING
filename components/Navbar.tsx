"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const [walletConnected, setWalletConnected] = useState(false);

  return (
    <nav className="flex items-center justify-between px-6 border-b border-lp-border bg-[var(--bg)] z-10 pt-[3px]">
      <div className="font-mono text-[14px] text-[var(--green)] tracking-[2px]">◈ LP_MIND</div>
      <div className="flex gap-6 h-full items-end pb-[2px]">
        {[
          { path: "/dashboard", label: "Dashboard" },
          { path: "/simulate", label: "Simulate" },
          { path: "/portfolio", label: "Portfolio" },
        ].map((link) => {
          const isActive = pathname.startsWith(link.path) || (pathname === '/' && link.path === '/dashboard');
          return (
            <Link 
              key={link.path} 
              href={link.path}
              className={`text-[12px] cursor-pointer tracking-[1px] uppercase py-1.5 border-b-2 transition-all duration-200 font-sans ${isActive ? 'text-[var(--text)] border-[var(--green)]' : 'text-[var(--muted)] border-transparent hover:text-[var(--text)] hover:border-[var(--green)]'}`}
            >
              {link.label}
            </Link>
          );
        })}
      </div>
      <button 
        onClick={() => setWalletConnected(!walletConnected)}
        className={`font-mono text-[11px] px-3.5 py-1.5 bg-transparent border border-[var(--purple)] text-[var(--purple)] rounded-md cursor-pointer tracking-[1px] transition-all duration-200 ${walletConnected ? '!bg-[var(--purple)] !text-white' : 'hover:bg-[var(--purple)] hover:text-white'}`}
      >
        {walletConnected ? '4xKj...9mPQ' : 'Connect Phantom'}
      </button>
    </nav>
  );
}
