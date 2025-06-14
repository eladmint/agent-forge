import { MainLayout } from "@/components/layout/main-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Code, ExternalLink, Star, Copy } from "lucide-react"

const examples = [
  {
    title: "Simple Navigation Agent",
    description: "Navigate to URLs and extract basic page information",
    difficulty: "Beginner",
    tags: ["Navigation", "Basic"],
    code: `from agent_forge import BaseAgent

class NavigationAgent(BaseAgent):
    async def run(self, url: str):
        page = await self.browser_client.navigate(url)
        return page.get('page_title')`
  },
  {
    title: "Content Extraction Agent", 
    description: "Extract specific content using CSS selectors",
    difficulty: "Intermediate",
    tags: ["Extraction", "CSS Selectors"],
    code: `from agent_forge import BaseAgent

class ContentAgent(BaseAgent):
    async def run(self, url: str):
        content = await self.browser_client.extract_content(
            url,
            selectors={
                'title': 'h1',
                'description': 'meta[name="description"]'
            }
        )
        return content`
  },
  {
    title: "Form Automation Agent",
    description: "Automate form filling and submission",
    difficulty: "Advanced", 
    tags: ["Forms", "Automation"],
    code: `from agent_forge import BaseAgent

class FormAgent(BaseAgent):
    async def run(self, form_data: dict):
        await self.browser_client.navigate("https://example.com/form")
        
        for field, value in form_data.items():
            await self.browser_client.type(f"input[name='{field}']", value)
        
        await self.browser_client.click("button[type='submit']")
        return "Form submitted successfully"`
  },
  {
    title: "Multi-Page Scraper",
    description: "Scrape data from multiple pages efficiently",
    difficulty: "Advanced",
    tags: ["Multi-page", "Concurrency"],
    code: `from agent_forge import BaseAgent
import asyncio

class MultiPageAgent(BaseAgent):
    async def run(self, urls: list):
        tasks = [self.scrape_page(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
    
    async def scrape_page(self, url: str):
        page = await self.browser_client.navigate(url)
        return {
            'url': url,
            'title': page.get('page_title'),
            'content_length': len(page.get('content', ''))
        }`
  }
]

const difficultyColors = {
  "Beginner": "bg-green-100 text-green-800",
  "Intermediate": "bg-yellow-100 text-yellow-800", 
  "Advanced": "bg-red-100 text-red-800"
}

export default function ExamplesPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold tracking-tight mb-4">
              Code Examples
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Learn by example. Copy, paste, and modify these working Agent Forge examples 
              to jumpstart your AI agent development.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {examples.map((example, index) => (
              <Card key={index} className="flex flex-col h-full">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="flex items-center space-x-2 mb-2">
                        <Code className="h-5 w-5 text-primary" />
                        <span>{example.title}</span>
                      </CardTitle>
                      <CardDescription className="text-base">
                        {example.description}
                      </CardDescription>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyColors[example.difficulty as keyof typeof difficultyColors]}`}>
                      {example.difficulty}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {example.tags.map((tag) => (
                      <span key={tag} className="px-2 py-1 bg-muted rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col">
                  <div className="bg-muted rounded-lg p-4 mb-4 flex-1 relative">
                    <pre className="text-sm overflow-x-auto">
                      <code className="text-foreground whitespace-pre-wrap">
                        {example.code}
                      </code>
                    </pre>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="absolute top-2 right-2"
                      aria-label="Copy code"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Star className="h-4 w-4 mr-2" />
                      Save Example
                    </Button>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      GitHub
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center mt-12">
            <h2 className="text-2xl font-bold mb-4">Want More Examples?</h2>
            <p className="text-muted-foreground mb-6">
              Check out our GitHub repository for additional examples and community contributions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link 
                  href="https://github.com/agent-forge/examples" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2"
                >
                  <ExternalLink className="h-5 w-5" />
                  <span>Browse GitHub Examples</span>
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/docs/getting-started">
                  <span>Get Started Guide</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}