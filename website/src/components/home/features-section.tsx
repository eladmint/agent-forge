"use client"

import { motion } from "framer-motion"
import { Bot, Globe, Zap, Shield, Code, Plug } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const features = [
  {
    icon: Bot,
    title: "AI-First Architecture",
    description: "Built from the ground up for modern AI agent patterns with seamless LLM integration and intelligent error handling.",
    color: "text-ancient-gold"
  },
  {
    icon: Globe,
    title: "Browser Automation Built-In",
    description: "Steel Browser integration provides production-ready web scraping with no complex setup required.",
    color: "text-nuru-purple"
  },
  {
    icon: Zap,
    title: "Universal MCP Support",
    description: "Works with Claude Desktop, ChatGPT, Gemini, and all major AI platforms through MCP integration.",
    color: "text-ancient-bronze"
  },
  {
    icon: Shield,
    title: "Production Ready",
    description: "Enterprise-grade error handling, logging, and monitoring built-in for reliable production deployments.",
    color: "text-emerald-500"
  },
  {
    icon: Code,
    title: "Developer Experience",
    description: "Modern async/await patterns, comprehensive documentation, and intuitive APIs that just make sense.",
    color: "text-blue-500"
  },
  {
    icon: Plug,
    title: "Extensible Framework",
    description: "Modular architecture allows easy customization and extension for your specific use cases.",
    color: "text-purple-500"
  }
]

export function FeaturesSection() {
  return (
    <section className="py-20 lg:py-32 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-3xl lg:text-4xl font-bold tracking-tight mb-4"
          >
            Why Choose Agent Forge?
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
            className="text-xl text-muted-foreground"
          >
            Everything you need to build, deploy, and scale AI agents in production.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow duration-300 border-l-4 border-l-primary/20 hover:border-l-primary/60">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg bg-background border ${feature.color}`}>
                      <feature.icon className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}