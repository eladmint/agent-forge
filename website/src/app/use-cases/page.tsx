import { MainLayout } from "@/components/layout/main-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CodeBlock } from "@/components/ui/code-block"
import Link from "next/link"
import { 
  Globe, 
  Database, 
  Building2, 
  TestTube, 
  Zap, 
  Shield, 
  ArrowRight,
  CheckCircle,
  TrendingUp,
  Users,
  Clock
} from "lucide-react"

const useCases = [
  {
    title: "Web Automation & Scraping",
    icon: Globe,
    description: "Automate complex web interactions and extract data from any website",
    color: "text-ancient-gold",
    bgColor: "bg-ancient-gold/5",
    features: [
      "E-commerce price monitoring",
      "Content aggregation systems",
      "Competitive intelligence gathering",
      "Social media automation",
      "News and article processing"
    ],
    metrics: {
      accuracy: "99.5%",
      speed: "10x faster",
      reliability: "24/7 uptime"
    },
    codeExample: `class PriceMonitorAgent(BaseAgent):
    async def run(self, products: List[str]):
        results = []
        for url in products:
            page = await self.browser_client.navigate(url)
            price = await self.extract_price(page)
            results.append({'url': url, 'price': price})
        return results`
  },
  {
    title: "Data Extraction & Processing",
    icon: Database,
    description: "Extract, transform, and process structured data from any source",
    color: "text-nuru-purple", 
    bgColor: "bg-nuru-purple/5",
    features: [
      "Financial data collection",
      "Real estate listings aggregation",
      "Research data gathering",
      "Document processing automation",
      "API data synchronization"
    ],
    metrics: {
      throughput: "1M+ records/hour",
      accuracy: "99.9%",
      formats: "50+ data formats"
    },
    codeExample: `class DataExtractionAgent(BaseAgent):
    async def run(self, sources: List[Source]):
        extracted_data = []
        for source in sources:
            data = await self.extract_structured_data(source)
            processed = await self.transform_data(data)
            extracted_data.append(processed)
        return extracted_data`
  },
  {
    title: "Enterprise Integration",
    icon: Building2,
    description: "Connect and automate business processes across your organization",
    color: "text-ancient-bronze",
    bgColor: "bg-ancient-bronze/5", 
    features: [
      "CRM data synchronization",
      "Automated report generation",
      "Legacy system integration",
      "Workflow orchestration",
      "Business process automation"
    ],
    metrics: {
      efficiency: "80% reduction in manual work",
      integration: "100+ systems supported",
      roi: "300% average ROI"
    },
    codeExample: `class EnterpriseIntegrationAgent(BaseAgent):
    async def run(self, workflow: Workflow):
        results = []
        for step in workflow.steps:
            result = await self.execute_step(step)
            await self.update_systems(result)
            results.append(result)
        return self.generate_report(results)`
  },
  {
    title: "Testing & Quality Assurance", 
    icon: TestTube,
    description: "Automated testing and quality assurance for web applications",
    color: "text-emerald-500",
    bgColor: "bg-emerald-50",
    features: [
      "User journey testing",
      "Cross-browser validation",
      "Performance monitoring",
      "Accessibility checks",
      "Regression testing"
    ],
    metrics: {
      coverage: "95% test coverage",
      speed: "50% faster testing",
      bugs: "90% fewer production bugs"
    },
    codeExample: `class QAAutomationAgent(BaseAgent):
    async def run(self, test_suite: TestSuite):
        results = []
        for test in test_suite.tests:
            result = await self.run_test(test)
            await self.validate_result(result)
            results.append(result)
        return self.generate_qa_report(results)`
  }
]

const benefits = [
  {
    icon: TrendingUp,
    title: "Increase Productivity",
    description: "Automate repetitive tasks and focus on high-value work"
  },
  {
    icon: Shield,
    title: "Reduce Errors",
    description: "Eliminate human error with consistent, reliable automation"
  },
  {
    icon: Clock,
    title: "Save Time",
    description: "Complete hours of work in minutes with intelligent agents"
  },
  {
    icon: Users,
    title: "Scale Operations",
    description: "Handle increasing workloads without adding headcount"
  }
]

export default function UseCasesPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-6">
              What Can You Build with <br />
              <span className="text-primary">Agent Forge?</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              From simple web scraping to complex enterprise automation, Agent Forge provides 
              the foundation for production-ready AI agents across every industry and use case.
            </p>
          </div>

          {/* Benefits Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            {benefits.map((benefit, index) => (
              <Card key={index} className="text-center border-2 hover:border-primary/20 transition-colors">
                <CardHeader className="pb-4">
                  <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                    <benefit.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{benefit.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {benefit.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Use Cases */}
          <div className="space-y-16">
            {useCases.map((useCase, index) => (
              <div key={index} className={`${index % 2 === 0 ? '' : 'lg:flex-row-reverse'} lg:flex lg:items-center lg:gap-12`}>
                
                {/* Content */}
                <div className="lg:w-1/2 mb-8 lg:mb-0">
                  <Card className={`border-l-4 border-l-primary hover:shadow-lg transition-shadow ${useCase.bgColor}`}>
                    <CardHeader>
                      <div className="flex items-center space-x-4 mb-4">
                        <div className={`p-3 rounded-lg ${useCase.bgColor} border`}>
                          <useCase.icon className={`h-8 w-8 ${useCase.color}`} />
                        </div>
                        <div>
                          <CardTitle className="text-2xl">{useCase.title}</CardTitle>
                          <CardDescription className="text-base mt-2">
                            {useCase.description}
                          </CardDescription>
                        </div>
                      </div>
                      
                      {/* Metrics */}
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        {Object.entries(useCase.metrics).map(([key, value]) => (
                          <div key={key} className="text-center">
                            <div className="font-bold text-lg text-primary">{value}</div>
                            <div className="text-sm text-muted-foreground capitalize">{key}</div>
                          </div>
                        ))}
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      {/* Features */}
                      <div className="space-y-2 mb-6">
                        {useCase.features.map((feature, idx) => (
                          <div key={idx} className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" />
                            <span className="text-sm">{feature}</span>
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex gap-3">
                        <Button size="sm" asChild>
                          <Link href="/examples">
                            View Examples
                          </Link>
                        </Button>
                        <Button variant="outline" size="sm" asChild>
                          <Link href="/docs/getting-started">
                            Get Started
                          </Link>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Code Example */}
                <div className="lg:w-1/2">
                  <CodeBlock
                    code={useCase.codeExample}
                    title="Example Implementation"
                    language="python"
                    className="border-2"
                  />
                </div>
              </div>
            ))}
          </div>

          {/* CTA Section */}
          <div className="text-center mt-20 p-12 rounded-2xl bg-gradient-to-r from-primary/5 via-secondary/5 to-accent/5 border">
            <h2 className="text-3xl font-bold mb-4">Ready to Build Your Use Case?</h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Start with our comprehensive getting started guide or explore real-world examples 
              to see how Agent Forge can transform your specific workflow.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="forge-glow">
                <Link href="/docs/getting-started" className="flex items-center space-x-2">
                  <span>Start Building</span>
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/examples" className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>Browse Examples</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}