import type { Metadata } from "next";
import { Space_Mono, DM_Sans } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import AIDecisionFeed from "@/components/AIDecisionFeed";

const spaceMono = Space_Mono({
  variable: "--font-space-mono",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

export const metadata: Metadata = {
  title: "LP Mind — AI Liquidity Manager",
  description: "AI Liquidity Manager",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${spaceMono.variable} ${dmSans.variable} dark antialiased h-full`}
    >
      <body className="h-full bg-[var(--bg)] text-[var(--text)] font-sans text-[14px] overflow-hidden m-0 p-0">
        <div className="grid grid-rows-[56px_1fr] h-screen bg-[var(--bg)]">
          <Navbar />
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] overflow-hidden">
            <div className="bg-[var(--bg)] p-5 flex flex-col gap-4 overflow-y-auto">
              {children}
            </div>
            <aside className="bg-[var(--bg)] border-l border-lp-border p-4 flex flex-col gap-2 overflow-y-auto hidden lg:flex">
              <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-2">
                AI DECISION FEED
              </div>
              <AIDecisionFeed />
            </aside>
          </div>
        </div>
      </body>
    </html>
  );
}
