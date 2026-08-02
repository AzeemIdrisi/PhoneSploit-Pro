import githubStats from "./github-stats.json";

export const navLinks = [
  { href: "#features", label: "Features" },
  { href: "#screenshots", label: "Screenshots" },
  { href: "#install", label: "Install" },
  { href: "#compatibility", label: "Compatibility" },
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
    icon: "gitlab",
  },
  {
    href: "https://github.com/AzeemIdrisi/PhoneSploit-Pro/discussions",
    label: "Discussions",
    icon: "message-square",
  },
];

export const repoInfo = {
  owner: "AzeemIdrisi",
  repo: "PhoneSploit-Pro",
  url: "https://github.com/AzeemIdrisi/PhoneSploit-Pro",
  stars: githubStats.stars,
  forks: githubStats.forks,
  starsFormatted: githubStats.starsFormatted,
  forksFormatted: githubStats.forksFormatted,
  version: "v2.1.1",
};
