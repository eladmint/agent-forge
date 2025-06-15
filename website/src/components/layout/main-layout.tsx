import { ReactNode } from "react"
import { Header } from "./header"
import { Footer } from "./footer"

interface MainLayoutProps {
  children: ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-900 text-white">
      <Header />
      <main className="flex-1 bg-slate-900">
        {children}
      </main>
      <Footer />
    </div>
  )
}