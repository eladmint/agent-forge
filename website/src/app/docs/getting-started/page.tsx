import { MainLayout } from "@/components/layout/main-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { CheckCircle, Copy, ArrowRight } from "lucide-react"

export default function GettingStartedPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold tracking-tight mb-4">
              Getting Started with Agent Forge
            </h1>
            <p className="text-xl text-muted-foreground">
              Build your first AI agent in under 10 minutes. This guide will walk you through 
              installation, setup, and creating your first working agent.
            </p>
          </div>

          <div className="space-y-8">
            {/* Prerequisites */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  <span>Prerequisites</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-muted-foreground">
                  <li>• Python 3.8 or higher</li>
                  <li>• Basic knowledge of async/await patterns</li>
                  <li>• pip or poetry for package management</li>
                </ul>
              </CardContent>
            </Card>

            {/* Step 1: Installation */}
            <Card>
              <CardHeader>
                <CardTitle>Step 1: Installation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-muted-foreground">
                  Install Agent Forge using pip:
                </p>
                <div className="bg-muted rounded-lg p-4 font-mono text-sm relative">
                  <code>pip install agent-forge</code>
                  <Button variant="ghost" size="icon" className="absolute top-2 right-2">
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Step 2: First Agent */}
            <Card>
              <CardHeader>
                <CardTitle>Step 2: Create Your First Agent</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-muted-foreground">
                  Create a simple agent that extracts page titles:
                </p>
                <div className="bg-muted rounded-lg p-4 font-mono text-sm relative overflow-x-auto">
                  <pre><code>{`from agent_forge import BaseAgent

class TitleExtractorAgent(BaseAgent):
    async def run(self, url: str) -> str:
        # Navigate to the URL
        page = await self.browser_client.navigate(url)
        
        # Extract the page title
        title = page.get('page_title', 'No title found')
        
        return f"Page title: {title}"

# Use your agent
async def main():
    agent = TitleExtractorAgent()
    result = await agent.run("https://example.com")
    print(result)

# Run it
import asyncio
asyncio.run(main())`}</code></pre>
                  <Button variant="ghost" size="icon" className="absolute top-2 right-2">
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Step 3: Run Your Agent */}
            <Card>
              <CardHeader>
                <CardTitle>Step 3: Run Your Agent</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-muted-foreground">
                  Save the code above as <code className="bg-muted px-2 py-1 rounded">my_agent.py</code> and run it:
                </p>
                <div className="bg-muted rounded-lg p-4 font-mono text-sm relative">
                  <code>python my_agent.py</code>
                  <Button variant="ghost" size="icon" className="absolute top-2 right-2">
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <p className="mt-4 text-muted-foreground">
                  You should see output like: <code className="bg-muted px-2 py-1 rounded">Page title: Example Domain</code>
                </p>
              </CardContent>
            </Card>

            {/* Next Steps */}
            <Card>
              <CardHeader>
                <CardTitle>🎉 Congratulations!</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-6 text-muted-foreground">
                  You&apos;ve successfully created and run your first Agent Forge agent. Here&apos;s what to explore next:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button variant="outline" asChild>
                    <Link href="/docs/concepts" className="flex items-center justify-between">
                      <span>Learn Core Concepts</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link href="/examples" className="flex items-center justify-between">
                      <span>Browse Examples</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link href="/docs/steel-browser" className="flex items-center justify-between">
                      <span>Steel Browser Guide</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link href="/docs/api" className="flex items-center justify-between">
                      <span>API Reference</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}