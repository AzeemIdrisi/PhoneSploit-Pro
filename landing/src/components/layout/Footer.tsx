import { Container } from "@/components/ui/Container";
import { Star, GitFork } from "lucide-react";
import { navLinks, repoInfo } from "@/data/constants";
import { getBasePath } from "@/lib/utils";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const basePath = getBasePath();

  return (
    <footer className="border-t border-white/10 bg-surface-950">
      <Container className="py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          <div>
            <a
              href={`${basePath}/`}
              className="font-mono text-lg font-bold tracking-widest text-white mb-4 inline-block"
              aria-label="PhoneSploit Pro Home"
            >
              PHONESPLOIT <span className="text-neon-red">PRO</span>
            </a>
            <p className="text-muted-foreground max-w-md text-sm font-mono leading-relaxed">
              The Swiss Army knife for Android. One menu for ADB control, scrcpy
              mirroring, data extraction, and Metasploit — pick a number and
              run.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-4 text-xs font-mono uppercase tracking-widest text-muted-foreground">
              <div className="flex items-center gap-2">
                <Star className="h-3.5 w-3.5 text-neon-red" />
                <span>{repoInfo.starsFormatted} Stars</span>
              </div>
              <div className="flex items-center gap-2">
                <GitFork className="h-3.5 w-3.5" />
                <span>{repoInfo.forksFormatted} Forks</span>
              </div>
              <span className="text-neon-cyan">GPL-3.0</span>
            </div>
          </div>

          <div>
            <h4 className="text-[10px] font-mono uppercase tracking-[0.25em] text-muted mb-4">
              Product
            </h4>
            <ul className="space-y-2">
              {navLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm font-mono text-muted-foreground hover:text-neon-cyan transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-[10px] font-mono uppercase tracking-[0.25em] text-muted mb-4">
              Resources
            </h4>
            <ul className="space-y-2 text-sm font-mono">
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-white transition-colors flex items-center gap-2"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  Issues
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/discussions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  Discussions
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/blob/main/docs/SECURITY.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  Security Policy
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/AzeemIdrisi/PhoneSploit-Pro/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  Contributing
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-[10px] font-mono uppercase tracking-[0.25em] text-muted mb-4">
              Developer
            </h4>
            <ul className="space-y-2 text-sm font-mono">
              <li>
                <a
                  href="https://github.com/AzeemIdrisi"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-neon-cyan transition-colors"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="https://azeemidrisi.github.io"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-neon-cyan transition-colors"
                >
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-white/10">
          <p className="text-muted text-xs font-mono text-center md:text-left">
            © {currentYear} Azeem Idrisi · GPL-3.0 · Educational use only
          </p>
        </div>
      </Container>
    </footer>
  );
}
