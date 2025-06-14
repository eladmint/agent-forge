import { MainLayout } from "@/components/layout/main-layout"
import { HeroSection } from "@/components/home/hero-section"
import { FeaturesSection } from "@/components/home/features-section"
import { FrameworkOverview } from "@/components/home/framework-overview"
import { CTASection } from "@/components/home/cta-section"

export default function Home() {
  return (
    <MainLayout>
      <HeroSection />
      <FeaturesSection />
      <FrameworkOverview />
      <CTASection />
    </MainLayout>
  )
}
