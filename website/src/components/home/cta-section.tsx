"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { ArrowRight, Github, MessageCircle, BookOpen } from "lucide-react"
import { Button } from "@/components/ui/button"

export function CTASection() {
  return (
    <section className="py-20 lg:py-32 bg-gradient-to-r from-primary/5 via-secondary/5 to-accent/5">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-3xl lg:text-4xl font-bold tracking-tight mb-4"
          >
            Ready to Build Your First Agent?
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
            className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto"
          >
            Join the growing community of developers building production-ready AI agents with Agent Forge. 
            Get started in minutes, scale to millions of requests.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8"
          >
            <div className="flex flex-col items-center p-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-1">Complete Documentation</h3>
              <p className="text-sm text-muted-foreground text-center">From basics to advanced patterns</p>
            </div>
            
            <div className="flex flex-col items-center p-4">
              <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center mb-3">
                <MessageCircle className="h-6 w-6 text-secondary" />
              </div>
              <h3 className="font-semibold mb-1">Active Community</h3>
              <p className="text-sm text-muted-foreground text-center">Get help when you need it</p>
            </div>
            
            <div className="flex flex-col items-center p-4">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mb-3">
                <Github className="h-6 w-6 text-accent" />
              </div>
              <h3 className="font-semibold mb-1">Open Source</h3>
              <p className="text-sm text-muted-foreground text-center">Built by developers, for developers</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            viewport={{ once: true }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Button 
              size="lg" 
              asChild 
              className="forge-glow text-lg px-8 py-6 h-auto"
            >
              <Link href="/docs/getting-started" className="flex items-center space-x-2">
                <span>Get Started Now</span>
                <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
            
            <Button 
              variant="outline" 
              size="lg" 
              asChild
              className="text-lg px-8 py-6 h-auto"
            >
              <Link href="/examples" className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5" />
                <span>Browse Examples</span>
              </Link>
            </Button>
            
            <Button 
              variant="ghost" 
              size="lg" 
              asChild
              className="text-lg px-8 py-6 h-auto"
            >
              <Link 
                href="https://discord.gg/agent-forge" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center space-x-2"
              >
                <MessageCircle className="h-5 w-5" />
                <span>Join Community</span>
              </Link>
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            viewport={{ once: true }}
            className="mt-12 text-sm text-muted-foreground"
          >
            <p>
              Trusted by developers worldwide • Open source • Production ready • 
              <Link href="/docs/enterprise" className="text-primary hover:underline ml-1">
                Enterprise support available
              </Link>
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  )
}