import { Inter, JetBrains_Mono } from "next/font/google";
import { getSiteUrl } from "@/lib/utils";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: "PhoneSploit Pro — The Android Swiss Army Knife",
  description:
    "An all-in-one hacking tool to remotely take over Android devices using ADB, scrcpy, Nmap, and Metasploit-Framework.",
  openGraph: {
    title: "PhoneSploit Pro — The Android Swiss Army Knife",
    description: "The Swiss Army knife for Android. Own the device.",
    images: ["/og-image.png"],
    type: "website",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} scroll-smooth`}
    >
      <body className="bg-surface-900 text-white antialiased">{children}</body>
    </html>
  );
}
