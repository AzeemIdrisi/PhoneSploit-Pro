import Hero from "@/components/hero/Hero";
import Showcase from "@/components/showcase/Showcase";
import OperatorFlow from "@/components/operator/OperatorFlow";
import Features from "@/components/features/Features";
import Screenshots from "@/components/screenshots/Screenshots";
import Install from "@/components/install/Install";
import Compatibility from "@/components/compatibility/Compatibility";
import FAQ from "@/components/faq/FAQ";
import CTABanner from "@/components/cta/CTABanner";
import Footer from "@/components/layout/Footer";
import Header from "@/components/layout/Header";

export default function Home() {
  return (
    <div className="relative min-h-screen">
      <Header />
      <main className="pt-24 sm:pt-28">
        <Hero />
        <Showcase />
        <OperatorFlow />
        <Features />
        <Screenshots />
        <Install />
        <Compatibility />
        <FAQ />
        <CTABanner />
      </main>
      <Footer />
    </div>
  );
}
