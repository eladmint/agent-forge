import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Agent Forge - Sacred Smithy of Digital Realm",
  description: "Production-ready Python framework for AI agents with built-in browser automation and MCP integration. Where ancient forge-craft meets modern AI.",
  keywords: [
    "AI agents",
    "Python framework",
    "browser automation",
    "Steel Browser",
    "MCP integration",
    "web scraping",
    "artificial intelligence",
    "agent framework",
    "production ready"
  ],
  authors: [{ name: "Agent Forge Team" }],
  creator: "Agent Forge",
  publisher: "Agent Forge",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://agent-forge.dev",
    title: "Agent Forge - Sacred Smithy of Digital Realm",
    description: "Production-ready Python framework for AI agents with built-in browser automation and MCP integration.",
    siteName: "Agent Forge",
  },
  twitter: {
    card: "summary_large_image",
    title: "Agent Forge - Sacred Smithy of Digital Realm",
    description: "Production-ready Python framework for AI agents with built-in browser automation and MCP integration.",
    creator: "@agentforge",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  manifest: '/manifest.json',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark"> {/* Added 'dark' class here */}
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}