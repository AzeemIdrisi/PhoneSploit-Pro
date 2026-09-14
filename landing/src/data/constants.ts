import githubStats from "./github-stats.json";

export const navLinks = [
  { href: "#features", label: "Features", num: "01" },
  { href: "#demos", label: "Demos", num: "02" },
  { href: "#install", label: "Install", num: "03" },
  { href: "#compatibility", label: "Compatibility", num: "04" },
  { href: "#faq", label: "FAQ", num: "05" },
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
  version: "v2.3",
};

export const toolStripItems = ["ADB", "SCRCPY", "NMAP", "METASPLOIT"] as const;
