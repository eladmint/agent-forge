"use client"

import { motion } from "framer-motion"
import { ArrowRight, Copy, Play } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const codeExample = `from agent_forge import BaseAgent

class ContentExtractionAgent(BaseAgent):
    async def run(self, url: str) -> dict:
        # Navigate to webpage with built-in browser automation
        page = await self.browser_client.navigate(url)
        
        # Extract specific content using CSS selectors
        content = await self.browser_client.extract_content(
            url, 
            selectors={
                'title': 'h1',
                'description': 'meta[name="description"]',
                'links': 'a[href]'
            }
        )
        
        # AI-powered content analysis (optional)
        analysis = await self.analyze_content(content)
        
        return {
            'title': content.get('title'),
            'description': content.get('description'), 
            'link_count': len(content.get('links', [])),
            'ai_summary': analysis.get('summary'),
            'extracted_at': datetime.now().isoformat()
        }

# Usage is simple and intuitive
agent = ContentExtractionAgent()
result = await agent.run("https://example.com")
print(f"Found: {result['title']}")  # Built-in error handling`

export function FrameworkOverview() {
  return (
    <section className="py-20 lg:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="mb-6"
            >
              <span className="inline-flex items-center rounded-full border border-secondary/20 bg-secondary/5 px-4 py-2 text-sm font-medium text-secondary mb-4">
                See It In Action
              </span>
              <h2 className="text-3xl lg:text-4xl font-bold tracking-tight mb-4">
                From Concept to Production
                <br />
                <span className="text-primary">In Minutes, Not Days</span>
              </h2>
              <p className="text-xl text-muted-foreground leading-relaxed">
                Agent Forge provides everything you need out of the box. No complex configuration, 
                no wrestling with browser automation, no reinventing the wheel. Just clean, 
                production-ready code that works.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              className="space-y-4 mb-8"
            >
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="font-semibold text-foreground">Built-in Browser Automation</h3>
                  <p className="text-muted-foreground">Steel Browser integration handles all the complexity</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-secondary mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="font-semibold text-foreground">Intelligent Error Handling</h3>
                  <p className="text-muted-foreground">Automatic retries, graceful degradation, comprehensive logging</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-accent mt-2 flex-shrink-0"></div>
                <div>
                  <h3 className="font-semibold text-foreground">Modern Async Patterns</h3>
                  <p className="text-muted-foreground">Clean async/await code that&apos;s easy to read and maintain</p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <Button size="lg" asChild className="forge-glow">
                <Link href="/docs/getting-started" className="flex items-center space-x-2">
                  <span>Start Building</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/examples" className="flex items-center space-x-2">
                  <Play className="h-4 w-4" />
                  <span>View More Examples</span>
                </Link>
              </Button>
            </motion.div>
          </div>

          {/* Code Example */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
          >
            <Card className="bg-background border-2 shadow-xl">
              <CardHeader className="bg-muted/50 border-b">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg font-mono">content_agent.py</CardTitle>
                  <Button variant="ghost" size="sm" className="text-xs">
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <pre className="text-sm p-6 leading-relaxed">
                    <code className="text-foreground font-mono whitespace-pre">
                      {codeExample}
                    </code>
                  </pre>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  )
}