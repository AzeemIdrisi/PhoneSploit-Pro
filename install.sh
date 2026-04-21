#!/usr/bin/env bash
# PhoneSploit Pro — dependency installer for Unix-like systems (Linux, macOS, Termux).
# See README.md for manual steps and supported distributions.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

YES=0
COMPONENTS_RAW=""
SKIP_PIP=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

  --yes, -y              Non-interactive: assume yes for prompts (except sudo/password).
  --components LIST      Comma-separated: adb,metasploit,scrcpy,nmap,pip
                         If omitted (interactive), you will be asked what to install.
  --skip-pip             Do not run pip install -r requirements.txt
  -h, --help             Show this help

Examples:
  ./install.sh
  ./install.sh --yes --components adb,nmap,scrcpy,pip
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y) YES=1 ;;
    --components) COMPONENTS_RAW="${2:-}"; shift ;;
    --skip-pip) SKIP_PIP=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
  shift
done

say() { printf '%s\n' "$*"; }
warn() { printf '[install] %s\n' "$*" >&2; }
die() { warn "$*"; exit 1; }

prompt_yes() {
  local msg="$1"
  if [[ "$YES" -eq 1 ]]; then
    return 0
  fi
  read -r -p "$msg [y/N] " x || true
  case "$(echo "$x" | tr '[:upper:]' '[:lower:]')" in
    y|yes) return 0 ;;
    *) return 1 ;;
  esac
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

detect_os() {
  if [[ -n "${TERMUX_VERSION:-}" ]] || [[ -d /data/data/com.termux/files/usr ]]; then
    echo "termux"
    return
  fi
  case "$(uname -s 2>/dev/null)" in
    Darwin) echo "macos"; return ;;
  esac
  if [[ -f /etc/os-release ]]; then
    # shellcheck source=/dev/null
    . /etc/os-release
    case "${ID:-}" in
      ubuntu|debian|linuxmint|kali|parrot|pop|zorin|elementary) echo "debian"; return ;;
      fedora|rhel|centos|rocky|almalinux) echo "fedora"; return ;;
      arch|manjaro|endeavouros|garuda) echo "arch"; return ;;
      opensuse*|opensuse-leap|opensuse-tumbleweed|sles) echo "opensuse"; return ;;
      alpine) echo "alpine"; return ;;
    esac
    local il="${ID_LIKE:-}"
    if echo "$il" | grep -qE '(^|[[:space:]])debian([[:space:]]|$)'; then echo "debian"; return; fi
    if echo "$il" | grep -qE '(rhel|fedora)'; then echo "fedora"; return; fi
    if echo "$il" | grep -q arch; then echo "arch"; return; fi
  fi
  echo "unknown"
}

OS_KIND="$(detect_os)"
PRETTY_OS="${OS_KIND}"
if [[ -f /etc/os-release ]]; then
  # shellcheck source=/dev/null
  . /etc/os-release
  PRETTY_OS="${PRETTY_NAME:-$OS_KIND}"
fi
if [[ "$(uname -s 2>/dev/null)" = "Darwin" ]]; then
  PRETTY_OS="macOS $(sw_vers -productVersion 2>/dev/null || echo '')"
fi

say ""
say "PhoneSploit Pro — dependency installer"
say "Detected environment: ${PRETTY_OS}"
say ""

ensure_python() {
  if ! have_cmd python3; then
    die "python3 not found. Install Python 3.10+ (see README), then re-run this script."
  fi
  python3 - <<'PY' || die "Python 3.10 or newer is required."
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PY
}

ensure_brew() {
  if have_cmd brew; then
    return 0
  fi
  warn "Homebrew is not installed (needed on macOS for several tools)."
  if [[ "$YES" -eq 1 ]]; then
    die "Install Homebrew from https://brew.sh and re-run."
  fi
  if ! prompt_yes "Install Homebrew now (official install script)?"; then
    die "Homebrew is required on macOS for this installer. Install manually and re-run."
  fi
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # shellcheck disable=SC1091
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -f /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
}

install_adb() {
  case "$OS_KIND" in
    debian)
      sudo apt-get update
      # Package name is "adb" (Ubuntu universe / Debian main); virtual: android-tools-adb
      sudo apt-get install -y adb
      ;;
    fedora)
      sudo dnf install -y android-tools
      ;;
    arch)
      sudo pacman -S --needed --noconfirm android-tools
      ;;
    opensuse)
      if ! sudo zypper --non-interactive install android-tools; then
        die "ADB: zypper could not install android-tools. On openSUSE you may need the hardware repo first — see https://software.opensuse.org/package/android-tools"
      fi
      ;;
    alpine)
      sudo apk add --no-cache android-tools
      ;;
    macos)
      ensure_brew
      brew install android-platform-tools
      ;;
    termux)
      pkg update -y
      pkg install -y android-tools
      ;;
    *)
      die "ADB: unsupported OS for automatic install. See README → Installing external tools → ADB."
      ;;
  esac
}

install_nmap() {
  case "$OS_KIND" in
    debian)
      sudo apt-get update
      sudo apt-get install -y nmap
      ;;
    fedora)
      sudo dnf install -y nmap
      ;;
    arch)
      sudo pacman -S --needed --noconfirm nmap
      ;;
    opensuse)
      sudo zypper --non-interactive install nmap
      ;;
    alpine)
      sudo apk add --no-cache nmap
      ;;
    macos)
      ensure_brew
      brew install nmap
      ;;
    termux)
      pkg update -y
      pkg install -y nmap
      ;;
    *)
      die "Nmap: unsupported OS for automatic install. See README → Nmap."
      ;;
  esac
}

install_scrcpy() {
  case "$OS_KIND" in
    debian)
      sudo apt-get update
      if ! sudo apt-get install -y scrcpy; then
        warn "apt could not install scrcpy. On some distros (e.g. Kali) use the scrcpy GitHub docs or build from source."
        return 1
      fi
      ;;
    fedora)
      sudo dnf install -y scrcpy
      ;;
    arch)
      sudo pacman -S --needed --noconfirm scrcpy
      ;;
    opensuse)
      sudo zypper --non-interactive install scrcpy || {
        warn "zypper scrcpy failed; try building from https://github.com/Genymobile/scrcpy"
        return 1
      }
      ;;
    alpine)
      warn "scrcpy on Alpine may need edge/community; see scrcpy GitHub."
      sudo apk add --no-cache scrcpy 2>/dev/null || return 1
      ;;
    macos)
      ensure_brew
      brew install scrcpy
      ;;
    termux)
      pkg update -y
      pkg install -y scrcpy || {
        warn "Termux: scrcpy may be unavailable; see README."
        return 1
      }
      ;;
    *)
      die "scrcpy: unsupported OS for automatic install. See README → scrcpy."
      ;;
  esac
}

install_metasploit() {
  case "$OS_KIND" in
    macos)
      ensure_brew
      # Upstream distributes Metasploit as a Homebrew Cask (not a core formula).
      if brew list --cask metasploit &>/dev/null; then
        warn "Metasploit already installed via Homebrew Cask."
        return 0
      fi
      brew install --cask metasploit
      ;;
    debian|fedora|arch|opensuse|alpine)
      local tmp
      tmp="$(mktemp -d)"
      trap 'rm -rf "$tmp"' EXIT
      curl -fsSL "https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb" \
        -o "$tmp/msfinstall"
      chmod 755 "$tmp/msfinstall"
      warn "Running Rapid7 msfinstall (may prompt for sudo / package manager)…"
      (cd "$tmp" && sudo ./msfinstall)
      ;;
    termux)
      die "Metasploit on Termux is not supported by this script. Use a full Linux desktop or see Metasploit docs."
      ;;
    *)
      die "Metasploit: unsupported OS for automatic install. See README → Metasploit-Framework."
      ;;
  esac
}

install_pip_reqs() {
  if [[ ! -f "$SCRIPT_DIR/requirements.txt" ]]; then
    warn "requirements.txt not found; skipping pip."
    return 0
  fi
  # Try user install first; many distros use PEP 668 and need --break-system-packages for pip outside a venv.
  if python3 -m pip install --user -r "$SCRIPT_DIR/requirements.txt"; then
    return 0
  fi
  warn "Retrying pip with --break-system-packages (PEP 668 / externally-managed Python)…"
  python3 -m pip install --user --break-system-packages -r "$SCRIPT_DIR/requirements.txt"
}

# --- Parse desired components (bash 3 compatible; no associative arrays) ---
want_adb=0
want_metasploit=0
want_scrcpy=0
want_nmap=0
want_pip=0

set_component() {
  case "$1" in
    adb) want_adb=1 ;;
    metasploit) want_metasploit=1 ;;
    scrcpy) want_scrcpy=1 ;;
    nmap) want_nmap=1 ;;
    pip) want_pip=1 ;;
    *) warn "Unknown component ignored: $1" ;;
  esac
}

if [[ -n "$COMPONENTS_RAW" ]]; then
  _old_ifs="$IFS"
  IFS=','
  for p in $COMPONENTS_RAW; do
    p="$(echo "$p" | tr -d '[:space:]')"
    [[ -z "$p" ]] && continue
    set_component "$p"
  done
  IFS="$_old_ifs"
else
  if [[ "$YES" -eq 1 ]]; then
    die "With --yes you must pass --components (e.g. adb,nmap,pip)."
  fi
  say "Choose what to install (you can say n to skip each):"
  prompt_yes "Install ADB (Android platform tools)?" && want_adb=1
  prompt_yes "Install Metasploit-Framework (large download)?" && want_metasploit=1
  prompt_yes "Install scrcpy?" && want_scrcpy=1
  prompt_yes "Install Nmap?" && want_nmap=1
  prompt_yes "Run pip install -r requirements.txt?" && want_pip=1
fi

if [[ "$OS_KIND" = "unknown" ]]; then
  die "Could not detect a supported package manager. Install dependencies manually (README → Installing external tools)."
fi

ensure_python

if [[ "$want_adb$want_metasploit$want_scrcpy$want_nmap$want_pip" = "00000" ]]; then
  say "Nothing selected. Exiting."
  exit 0
fi

if [[ "$want_adb" -eq 1 ]]; then
  warn "Installing ADB…"
  install_adb
fi
if [[ "$want_nmap" -eq 1 ]]; then
  warn "Installing Nmap…"
  install_nmap
fi
if [[ "$want_scrcpy" -eq 1 ]]; then
  warn "Installing scrcpy…"
  install_scrcpy || warn "scrcpy install reported an error; see messages above."
fi
if [[ "$want_metasploit" -eq 1 ]]; then
  warn "Installing Metasploit-Framework…"
  install_metasploit
fi
if [[ "$want_pip" -eq 1 ]] && [[ "$SKIP_PIP" -eq 0 ]]; then
  warn "Installing Python dependencies (pip)…"
  install_pip_reqs
fi

say ""
say "Done. If commands are still not found, open a new terminal or log out and back in (PATH updates)."
say "Then run: python3 phonesploitpro.py"
say ""
