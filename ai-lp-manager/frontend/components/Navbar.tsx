"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { useWallet, useConnection } from "@solana/wallet-adapter-react";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { LAMPORTS_PER_SOL } from "@solana/web3.js";
import { fetchWallet } from "../api/wallet";
import { fetchContractInfo } from "../api/contract";

export default function Navbar() {
  const pathname = usePathname();
  const { publicKey, connected } = useWallet();
  const { connection } = useConnection();
  const [walletData, setWalletData] = useState<any>(null);
  const [nativeBalance, setNativeBalance] = useState<number | null>(null);
  const [contractInfo, setContractInfo] = useState<any>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetchContractInfo().then(setContractInfo).catch(console.error);
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
      <div className="flex items-center gap-6">
        <div className="font-mono text-[14px] text-[var(--green)] tracking-[2px]">◈ LP_MIND</div>
        <div className="hidden lg:flex items-center gap-2 font-mono text-[10px] tracking-[1px] mt-[2px]">
          <div className="bg-[rgba(0,245,160,0.08)] text-[var(--green)] border border-[rgba(0,245,160,0.2)] px-2.5 py-[5px] rounded-md">
            <span className="mr-1.5 inline-block w-[6px] h-[6px] bg-[var(--green)] rounded-full animate-pulse shadow-[0_0_8px_var(--green)]"></span>
            Live on {contractInfo?.network || 'Devnet'}
          </div>
          <a 
            href={`https://explorer.solana.com/address/${contractInfo?.programId || 'CSjDhZXoYAeSa8mtsy7xgSRVqq2Bbeb9jSwf9RP5QVN6'}?cluster=${contractInfo?.network || 'devnet'}`} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="bg-[rgba(167,139,250,0.08)] text-[var(--purple)] border border-[rgba(167,139,250,0.2)] px-2.5 py-[5px] rounded-md hover:bg-[rgba(167,139,250,0.15)] transition-colors inline-flex items-center gap-1.5 cursor-pointer"
          >
            Program: {contractInfo?.programId ? `${contractInfo.programId.slice(0,6)}...${contractInfo.programId.slice(-4)}` : 'CSjDhZ...QVN6'} ↗
          </a>
        </div>
      </div>
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
