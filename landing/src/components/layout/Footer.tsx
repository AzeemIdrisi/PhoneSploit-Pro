import { Container } from "@/components/ui/Container";
import { Star, GitFork } from "lucide-react";
import { GitHubIcon } from "@/components/ui/BrandIcons";
import { repoInfo } from "@/data/constants";
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
              An all-in-one hacking tool to remotely take over Android devices
              using ADB, scrcpy, Nmap, and Metasploit-Framework.
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
                  <GitHubIcon className="h-4 w-4" />
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
                  <GitHubIcon className="h-4 w-4" />
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
                  <GitHubIcon className="h-4 w-4" />
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
                  <GitHubIcon className="h-4 w-4" />
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
                  <GitHubIcon className="h-4 w-4" />
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
              Copyright © {currentYear} Azeem Idrisi. Licensed under GPL-3.0.
            </p>
          </div>
        </div>
      </Container>
    </footer>
  );
}
