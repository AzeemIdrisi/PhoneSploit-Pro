import { Inter, JetBrains_Mono } from 'next/font/google'
import { getSiteUrl } from '@/lib/utils'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})
const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: 'PhoneSploit Pro — Android ADB & Metasploit Toolkit',
  description: 'All-in-one hacking tool to remotely exploit Android devices using ADB and Metasploit-Framework. Automated Meterpreter sessions, device control, data extraction, and more.',
  openGraph: {
    title: 'PhoneSploit Pro',
    description: 'Android ADB & Metasploit automation toolkit',
    images: ['/og-image.png'],
    type: 'website',
  },
  twitter: { card: 'summary_large_image' },
  robots: { index: true, follow: true },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} scroll-smooth`}>
      <body className="bg-surface-900 text-white antialiased">{children}</body>
    </html>
  )
}