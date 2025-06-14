import { MainLayout } from "@/components/layout/main-layout"
import Link from "next/link"
import { BookOpen, ArrowRight, Zap, Globe, Bot } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const quickStartLinks = [
  {
    title: "Installation",
    description: "Get Agent Forge installed and ready to use",
    href: "/docs/installation",
    icon: Bot
  },
  {
    title: "Quick Start",
    description: "Build your first agent in 5 minutes",
    href: "/docs/quick-start", 
    icon: Zap
  },
  {
    title: "Core Concepts",
    description: "Understand the framework architecture",
    href: "/docs/concepts",
    icon: BookOpen
  },
  {
    title: "Steel Browser Integration",
    description: "Learn about built-in web automation",
    href: "/docs/steel-browser",
    icon: Globe
  }
]

export default function DocsPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold tracking-tight mb-4">
              Agent Forge Documentation
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to build, deploy, and scale AI agents in production.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {quickStartLinks.map((link) => (
              <Card key={link.title} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <link.icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle>{link.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">
                    {link.description}
                  </CardDescription>
                  <Button variant="ghost" asChild className="p-0 h-auto">
                    <Link href={link.href} className="flex items-center space-x-2 text-primary">
                      <span>Learn more</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Ready to get started?</h2>
            <p className="text-muted-foreground mb-6">
              Follow our getting started guide to build your first agent.
            </p>
            <Button size="lg" asChild className="forge-glow">
              <Link href="/docs/getting-started">
                Get Started Now
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}