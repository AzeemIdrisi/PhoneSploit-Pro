import { Container } from "@/components/ui/Container";
import { MessageSquare, ExternalLink, Star, GitFork } from "lucide-react";
import { GitHubIcon, GitLabIcon, XIcon } from "@/components/ui/BrandIcons";
import { socialLinks, repoInfo } from "@/data/constants";
import { getBasePath } from "@/lib/utils";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const basePath = getBasePath();

  return (
    <footer className="border-t border-surface-700 bg-surface-900/50">
      <Container className="py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          <div className="lg:col-span-2">
            <a
              href={`${basePath}/`}
              className="flex items-center gap-2 text-2xl font-bold text-white mb-4"
              aria-label="PhoneSploit Pro Home"
            >
              <span className="text-primary-400">PhoneSploit</span>
              <span className="text-white">Pro</span>
            </a>
            <p className="text-primary-300 max-w-md text-balance">
              All-in-one hacking tool to remotely exploit Android devices using
              ADB and Metasploit-Framework. Automated Meterpreter sessions,
              device control, data extraction, and more.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-primary-400">
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-accent-500" />
                <span>{repoInfo.starsFormatted} Stars</span>
              </div>
              <div className="flex items-center gap-2">
                <GitFork className="h-4 w-4" />
                <span>{repoInfo.forksFormatted} Forks</span>
              </div>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              {socialLinks.map((link) => {
                const Icon = getIcon(link.icon);
                return (
                  <a
                    key={link.label}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-primary-300 bg-surface-800/50 border border-surface-700 hover:bg-primary-900/30 hover:text-white hover:border-primary-700 transition-all"
                  >
                    <Icon className="h-4 w-4" />
                    {link.label}
                  </a>
                );
              })}
            </div>
          </div>

          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Resources</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-300 hover:text-white transition-colors flex items-center gap-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  GitHub Repository
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-300 hover:text-white transition-colors flex items-center gap-2"
                >
                  <GitLabIcon className="h-4 w-4" />
                  Report Issues
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/discussions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-300 hover:text-white transition-colors flex items-center gap-2"
                >
                  <MessageSquare className="h-4 w-4" />
                  Discussions
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/blob/main/docs/SECURITY.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-300 hover:text-white transition-colors flex items-center gap-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  Security Policy
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-300 hover:text-white transition-colors flex items-center gap-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  Contributing
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-lg font-semibold text-white mb-4">
              Requirements
            </h4>
            <ul className="space-y-2 text-primary-300 text-sm">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
                Python 3.10+
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
                ADB (Android Debug Bridge)
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
                Metasploit-Framework
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
                scrcpy
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-accent-500" />
                Nmap
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-surface-700">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-primary-500 text-sm text-center md:text-left">
              Copyright © {currentYear} Azeem Idrisi. Licensed under MIT
              License.
            </p>
          </div>
        </div>
      </Container>
    </footer>
  );
}

function getIcon(name: string) {
  const icons: Record<string, React.ComponentType<{ className?: string }>> = {
    github: GitHubIcon,
    twitter: XIcon,
    "message-square": MessageSquare,
    gitlab: GitLabIcon,
  };
  return icons[name] || GitHubIcon;
}
