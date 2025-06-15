"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, Github, Zap, Globe, Bot } from "lucide-react"
import { Button } from "@/components/ui/button"
import { CodeBlock } from "@/components/ui/code-block"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 min-h-screen flex items-center">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30"></div>
      <div className="absolute inset-0 bg-gradient-radial"></div>

      {/* Floating Elements */}
      <div className="absolute top-20 left-10 w-4 h-4 rounded-full bg-primary/30 ember-float blur-sm"></div>
      <div className="absolute top-32 right-16 w-6 h-6 rounded-full bg-secondary/30 ember-float blur-sm" style={{ animationDelay: '1s' }}></div>
      <div className="absolute bottom-32 left-20 w-3 h-3 rounded-full bg-accent/30 ember-float blur-sm" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-1/2 right-1/4 w-2 h-2 rounded-full bg-primary/20 ember-float blur-sm" style={{ animationDelay: '3s' }}></div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 px-4 py-2 text-sm font-medium text-primary mb-8"
          >
            <Zap className="mr-2 h-4 w-4" />
            Now with Universal MCP Integration
            <ArrowRight className="ml-2 h-4 w-4" />
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6"
          >
            <span className="gradient-text-ancient-gold">
              Sacred Smithy
            </span>
            <br />
            <span className="text-white font-bold">of Digital Realm</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl lg:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed text-slate-300"
          >
            Production-ready Python framework for AI agents with built-in browser automation and MCP integration.
            Where ancient forge-craft meets modern AI.
          </motion.p>

          {/* Feature Pills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-wrap justify-center gap-4 mb-10"
          >
            <div className="inline-flex items-center rounded-full border bg-card/50 backdrop-blur-sm px-5 py-3 text-sm font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <Bot className="mr-2 h-4 w-4 text-primary" />
              AI-First Architecture
            </div>
            <div className="inline-flex items-center rounded-full border bg-card/50 backdrop-blur-sm px-5 py-3 text-sm font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <Globe className="mr-2 h-4 w-4 text-secondary" />
              Steel Browser Built-In
            </div>
            <div className="inline-flex items-center rounded-full border bg-card/50 backdrop-blur-sm px-5 py-3 text-sm font-medium shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <Zap className="mr-2 h-4 w-4 text-accent" />
              Universal MCP Support
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
          >
            <Button
              size="lg"
              asChild
              className="forge-glow text-lg px-10 py-6 h-auto shadow-2xl hover:shadow-primary/25 transition-all duration-300 hover:scale-105 bg-gradient-to-r from-primary to-primary/80"
            >
              <Link href="/docs/getting-started" className="flex items-center space-x-2">
                <span>Get Started in 5 Minutes</span>
                <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>

            <Button
              variant="outline"
              size="lg"
              asChild
              className="text-lg px-10 py-6 h-auto border-2 glass-effect hover:bg-card/80 transition-all duration-300 hover:scale-105 shadow-lg"
            >
              <Link
                href="https://github.com/agent-forge"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2"
              >
                <Github className="h-5 w-5" />
                <span>View on GitHub</span>
              </Link>
            </Button>
          </motion.div>

          {/* Quick Start Code */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="mt-12 max-w-2xl mx-auto"
          >
            <CodeBlock
              code={`pip install agent-forge

from agent_forge import BaseAgent

class MyAgent(BaseAgent):
    async def run(self, url: str):
        page = await self.browser_client.navigate(url)
        return page.get('page_title')

agent = MyAgent()
result = await agent.run("https://example.com")`}
              title="Quick Start"
              language="python"
            />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
