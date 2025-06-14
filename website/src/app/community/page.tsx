import { MainLayout } from "@/components/layout/main-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { 
  Github, 
  MessageCircle, 
  BookOpen, 
  Users, 
  Star,
  ExternalLink,
  Zap,
  Heart,
  Trophy,
  Calendar,
  Code,
  Bug,
  Lightbulb,
  ArrowRight
} from "lucide-react"

const communityChannels = [
  {
    title: "GitHub Repository",
    icon: Github,
    description: "Contribute to the codebase, report issues, and track development",
    link: "https://github.com/nuru-ai/agent-forge",
    color: "text-gray-900",
    bgColor: "bg-gray-50",
    stats: {
      stars: "2.1k",
      forks: "340", 
      issues: "42 open"
    },
    actions: [
      { label: "View Source", icon: Code },
      { label: "Report Bug", icon: Bug },
      { label: "Request Feature", icon: Lightbulb }
    ]
  },
  {
    title: "Discord Community",
    icon: MessageCircle,
    description: "Join discussions, get help, and connect with other developers",
    link: "https://discord.gg/agent-forge",
    color: "text-indigo-600",
    bgColor: "bg-indigo-50",
    stats: {
      members: "5.2k",
      online: "420",
      channels: "15"
    },
    actions: [
      { label: "General Chat", icon: MessageCircle },
      { label: "Help & Support", icon: Heart },
      { label: "Showcase", icon: Trophy }
    ]
  },
  {
    title: "Documentation Hub",
    icon: BookOpen,
    description: "Comprehensive guides, tutorials, and API reference",
    link: "/docs",
    color: "text-ancient-gold",
    bgColor: "bg-ancient-gold/5",
    stats: {
      guides: "50+",
      examples: "120+",
      updated: "Daily"
    },
    actions: [
      { label: "Getting Started", icon: Zap },
      { label: "API Reference", icon: BookOpen },
      { label: "Examples", icon: Code }
    ]
  }
]

const contributors = [
  {
    name: "Alex Chen",
    role: "Core Maintainer",
    contributions: "Architecture, Core Framework",
    avatar: "AC",
    color: "bg-ancient-gold"
  },
  {
    name: "Sarah Kim",
    role: "Browser Integration Lead", 
    contributions: "Steel Browser, Automation",
    avatar: "SK",
    color: "bg-nuru-purple"
  },
  {
    name: "Mike Rodriguez",
    role: "DevOps & Deployment",
    contributions: "Infrastructure, CI/CD",
    avatar: "MR",
    color: "bg-ancient-bronze"
  },
  {
    name: "Emma Thompson",
    role: "Documentation",
    contributions: "Guides, Tutorials, Examples",
    avatar: "ET",
    color: "bg-emerald-500"
  },
  {
    name: "David Park",
    role: "Community Manager",
    contributions: "Discord, Support, Events",
    avatar: "DP",
    color: "bg-blue-500"
  },
  {
    name: "Lisa Wang",
    role: "AI Integration",
    contributions: "LLM Connectors, Reasoning",
    avatar: "LW",
    color: "bg-pink-500"
  }
]

const events = [
  {
    title: "Agent Forge Monthly Meetup",
    date: "Every 2nd Thursday",
    time: "7:00 PM EST",
    type: "Virtual Meetup",
    description: "Monthly community calls to discuss updates, showcase projects, and Q&A"
  },
  {
    title: "Hackathon: Build with Agent Forge",
    date: "July 15-17, 2025",
    time: "48 hours",
    type: "Virtual Hackathon",
    description: "Build innovative AI agents using Agent Forge. Prizes and mentorship included!"
  },
  {
    title: "Workshop: Advanced Automation",
    date: "August 5, 2025",
    time: "2:00 PM EST",
    type: "Workshop",
    description: "Deep dive into complex automation patterns and enterprise deployment strategies"
  }
]

const contributionAreas = [
  {
    title: "Core Framework",
    description: "Improve the base agent architecture and core functionality",
    difficulty: "Advanced",
    color: "border-ancient-gold",
    skills: ["Python", "Architecture", "Testing"]
  },
  {
    title: "Browser Integration", 
    description: "Enhance Steel Browser connectivity and web automation features",
    difficulty: "Intermediate",
    color: "border-nuru-purple",
    skills: ["JavaScript", "Browser APIs", "Automation"]
  },
  {
    title: "Documentation",
    description: "Write guides, tutorials, and improve existing documentation",
    difficulty: "Beginner",
    color: "border-emerald-500",
    skills: ["Writing", "Markdown", "Examples"]
  },
  {
    title: "AI Connectors",
    description: "Build integrations with new LLM providers and AI services",
    difficulty: "Intermediate",
    color: "border-blue-500",
    skills: ["Python", "APIs", "AI/ML"]
  }
]

export default function CommunityPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-6">
              Join the <span className="text-primary">Agent Forge</span> Community
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Connect with developers, contributors, and AI enthusiasts building the future 
              of intelligent automation. From beginners to experts, everyone is welcome.
            </p>
          </div>

          {/* Community Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <Card className="text-center border-2 hover:border-primary/20 transition-colors">
              <CardHeader>
                <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-3xl font-bold">8.5k+</CardTitle>
                <CardDescription>Active Developers</CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center border-2 hover:border-primary/20 transition-colors">
              <CardHeader>
                <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Star className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-3xl font-bold">2.1k+</CardTitle>
                <CardDescription>GitHub Stars</CardDescription>
              </CardHeader>
            </Card>
            <Card className="text-center border-2 hover:border-primary/20 transition-colors">
              <CardHeader>
                <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Code className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-3xl font-bold">450+</CardTitle>
                <CardDescription>Projects Built</CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* Community Channels */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-12">Connect With Us</h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {communityChannels.map((channel, index) => (
                <Card key={index} className={`border-2 hover:border-primary/20 transition-all hover:shadow-lg ${channel.bgColor}`}>
                  <CardHeader>
                    <div className="flex items-center space-x-4 mb-4">
                      <div className={`p-3 rounded-lg ${channel.bgColor} border`}>
                        <channel.icon className={`h-8 w-8 ${channel.color}`} />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{channel.title}</CardTitle>
                        <CardDescription className="mt-2">
                          {channel.description}
                        </CardDescription>
                      </div>
                    </div>
                    
                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-2 mb-6">
                      {Object.entries(channel.stats).map(([key, value]) => (
                        <div key={key} className="text-center">
                          <div className="font-bold text-primary">{value}</div>
                          <div className="text-xs text-muted-foreground capitalize">{key}</div>
                        </div>
                      ))}
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-2 mb-6">
                      {channel.actions.map((action, idx) => (
                        <div key={idx} className="flex items-center space-x-2 text-sm">
                          <action.icon className="h-4 w-4 text-primary" />
                          <span>{action.label}</span>
                        </div>
                      ))}
                    </div>
                    
                    <Button asChild className="w-full">
                      <Link href={channel.link} className="flex items-center space-x-2">
                        <span>Join Now</span>
                        <ExternalLink className="h-4 w-4" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Contributors */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-12">Core Contributors</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contributors.map((contributor, index) => (
                <Card key={index} className="border-2 hover:border-primary/20 transition-colors">
                  <CardHeader className="text-center">
                    <div className={`mx-auto w-16 h-16 rounded-full ${contributor.color} flex items-center justify-center mb-4`}>
                      <span className="text-white font-bold text-lg">{contributor.avatar}</span>
                    </div>
                    <CardTitle className="text-lg">{contributor.name}</CardTitle>
                    <CardDescription className="font-medium text-primary">
                      {contributor.role}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="text-sm text-muted-foreground">{contributor.contributions}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Upcoming Events */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-12">Upcoming Events</h2>
            <div className="space-y-6">
              {events.map((event, index) => (
                <Card key={index} className="border-l-4 border-l-primary hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                      <div>
                        <CardTitle className="text-xl mb-2">{event.title}</CardTitle>
                        <CardDescription className="text-base mb-2">
                          {event.description}
                        </CardDescription>
                      </div>
                      <div className="flex flex-col items-start md:items-end space-y-1">
                        <div className="flex items-center space-x-2 text-sm">
                          <Calendar className="h-4 w-4 text-primary" />
                          <span className="font-medium">{event.date}</span>
                        </div>
                        <div className="text-sm text-muted-foreground">{event.time}</div>
                        <span className="inline-block px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                          {event.type}
                        </span>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>

          {/* Contribution Areas */}
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-center mb-12">Ways to Contribute</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {contributionAreas.map((area, index) => (
                <Card key={index} className={`border-2 ${area.color} hover:shadow-lg transition-shadow`}>
                  <CardHeader>
                    <div className="flex items-center justify-between mb-4">
                      <CardTitle className="text-xl">{area.title}</CardTitle>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        area.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                        area.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {area.difficulty}
                      </span>
                    </div>
                    <CardDescription className="text-base">
                      {area.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {area.skills.map((skill, idx) => (
                        <span key={idx} className="px-2 py-1 bg-muted text-muted-foreground text-sm rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center p-12 rounded-2xl bg-gradient-to-r from-primary/5 via-secondary/5 to-accent/5 border">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Involved?</h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Whether you&apos;re looking to contribute code, documentation, or just connect with 
              like-minded developers, there&apos;s a place for you in our community.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="forge-glow">
                <Link href="https://discord.gg/agent-forge" className="flex items-center space-x-2">
                  <span>Join Discord</span>
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="https://github.com/nuru-ai/agent-forge" className="flex items-center space-x-2">
                  <Github className="h-5 w-5" />
                  <span>View on GitHub</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}