import Hero from '@/components/hero/Hero'
import Showcase from '@/components/showcase/Showcase'
import Features from '@/components/features/Features'
import Screenshots from '@/components/screenshots/Screenshots'
import Install from '@/components/install/Install'
import Compatibility from '@/components/compatibility/Compatibility'
import CTABanner from '@/components/cta/CTABanner'
import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'

export default function Home() {
  return (
    <div className="relative min-h-screen">
      <Header />
      <main className="pt-16">
        <Hero />
        <Showcase />
        <Features />
        <Screenshots />
        <Install />
        <Compatibility />
        <CTABanner />
      </main>
      <Footer />
    </div>
  )
}