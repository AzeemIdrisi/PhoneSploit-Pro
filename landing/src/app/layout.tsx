import { GeistMono } from "geist/font/mono";
import { getBasePath, getSiteUrl } from "@/lib/utils";
import "./fonts/HarmonyOS_Sans/Black/Black.css";
import "./globals.css";

const ogImagePath = `${getBasePath()}/screenshots/Screenshot-1.png`;

export const metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: "PhoneSploit Pro — The Android Swiss Army Knife",
  description:
    "All-in-one Android security testing from one menu. ADB, scrcpy, Nmap, and Metasploit-Framework — connect, control, extract, and exploit.",
  openGraph: {
    title: "PhoneSploit Pro — The Android Swiss Army Knife",
    description: "The Swiss Army knife for Android. Own the device.",
    images: [ogImagePath],
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
      className={`${GeistMono.variable} scroll-smooth`}
    >
      <body className="bg-background text-foreground antialiased">
        <div className="page-grid" aria-hidden="true" />
        <div className="noise-bg" aria-hidden="true" />
        <div className="scanline-effect" aria-hidden="true" />
        <div className="scanline-sweep" aria-hidden="true" />
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
