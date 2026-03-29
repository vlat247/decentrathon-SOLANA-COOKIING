"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { useWallet, useConnection } from "@solana/wallet-adapter-react";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { LAMPORTS_PER_SOL } from "@solana/web3.js";
import { fetchWallet } from "../api/wallet";

export default function Navbar() {
  const pathname = usePathname();
  const { publicKey, connected } = useWallet();
  const { connection } = useConnection();
  const [walletData, setWalletData] = useState<any>(null);
  const [nativeBalance, setNativeBalance] = useState<number | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (connected && publicKey) {
      // Fetch native balance over RPC so it works even if backend is offline
      connection.getBalance(publicKey)
        .then(lamports => setNativeBalance(lamports / LAMPORTS_PER_SOL))
        .catch(console.error);

      // Background payload for AI integration
      fetchWallet(publicKey.toBase58())
        .then(data => setWalletData(data))
        .catch(console.error);
    } else {
      setWalletData(null);
      setNativeBalance(null);
    }
  }, [connected, publicKey, connection]);

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
      <div className="flex gap-4 items-center">
        {(nativeBalance !== null || walletData) && (
          <span className="font-mono text-[11px] text-[var(--green)]">
            {(nativeBalance ?? walletData?.solBalance ?? 0).toFixed(2)} SOL
          </span>
        )}
        <div className="wallet-btn-container z-50">
          {mounted && <WalletMultiButton />}
        </div>
      </div>
    </nav>
  );
}
