import githubStats from "./github-stats.json";

export const navLinks = [
  { href: "#demos", label: "Demos", num: "01" },
  { href: "#workflow", label: "Workflow", num: "02" },
  { href: "#features", label: "Features", num: "03" },
  { href: "#screenshot", label: "Interface", num: "04" },
  { href: "#install", label: "Install", num: "05" },
  { href: "#compatibility", label: "Compatibility", num: "06" },
  { href: "#faq", label: "FAQ", num: "07" },
];

export const socialLinks = [
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro",
    label: "GitHub",
    icon: "github",
  },
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues",
    label: "Issues",
    icon: "github",
  },
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro/discussions",
    label: "Discussions",
    icon: "github",
  },
];

export const repoInfo = {
  owner: "AzeemIdrisi",
  repo: "PhoneSploit-Pro",
  url: "https://github.com/AzeemIdrisi/PhoneSploit-Pro",
  cloneUrl: "git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git",
  stars: githubStats.stars,
  forks: githubStats.forks,
  starsFormatted: githubStats.starsFormatted,
  forksFormatted: githubStats.forksFormatted,
  version: process.env.NEXT_PUBLIC_APP_VERSION ?? "",
};

export const toolStripItems = ["ADB", "SCRCPY", "NMAP", "METASPLOIT"] as const;
