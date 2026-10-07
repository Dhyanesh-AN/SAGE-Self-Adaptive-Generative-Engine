// app/layout.tsx
import type { Metadata } from "next";
import { Syncopate, Space_Grotesk } from "next/font/google";
import "./globals.css";

// The wide, aggressive heading font
const syncopate = Syncopate({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: '--font-syncopate'
});

// The sleek, technical body font
const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: '--font-space-grotesk'
});

export const metadata: Metadata = {
  title: "SAGE | Agentic RAG",
  description: "Self-correcting Agentic Retrieval-Augmented Generation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${syncopate.variable} ${spaceGrotesk.variable} font-mono bg-background text-white selection:bg-neon selection:text-black`}>
        {children}
      </body>
    </html>
  );
}