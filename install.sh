#!/usr/bin/env bash
# PhoneSploit Pro — dependency installer for Unix-like systems (Linux, macOS, Termux).
# See README.md for manual steps and supported distributions.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION_FILE="$SCRIPT_DIR/VERSION"
if [[ ! -f "$VERSION_FILE" ]]; then
  echo "Error: VERSION file not found at $VERSION_FILE" >&2
  exit 1
fi
INSTALLER_VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"
if [[ -z "$INSTALLER_VERSION" ]]; then
  echo "Error: VERSION file is empty" >&2
  exit 1
fi

YES=1
COMPONENTS_RAW=""
SKIP_PIP=0
INTERACTIVE=0

# --- UI state ---
STEP_CURRENT=0
STEP_TOTAL=0
FAILED_COUNT=0
declare -a SUMMARY_OK=()
declare -a SUMMARY_SKIP=()
declare -a SUMMARY_FAIL=()

# --- Colors (TTY + NO_COLOR) ---
if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
  C_RESET=$'\033[0m'
  C_BOLD=$'\033[1m'
  C_DIM=$'\033[2m'
  C_RED=$'\033[31m'
  C_GREEN=$'\033[32m'
  C_YELLOW=$'\033[33m'
  C_CYAN=$'\033[36m'
  C_MAGENTA=$'\033[35m'
  C_WHITE=$'\033[97m'
else
  C_RESET="" C_BOLD="" C_DIM="" C_RED="" C_GREEN="" C_YELLOW="" C_CYAN="" C_MAGENTA="" C_WHITE=""
fi

# Box drawing: UTF-8 locale vs ASCII
_use_utf8=0
if [[ "${LANG:-}${LC_ALL:-}" == *[Uu][Tt][Ff]-8* ]]; then
  _use_utf8=1
fi
if [[ "$_use_utf8" -eq 1 ]]; then
  BOX_TL="╔" BOX_TR="╗" BOX_BL="╚" BOX_BR="╝" BOX_H="═" BOX_V="║"
  ICON_OK="✓" ICON_FAIL="✗" ICON_SKIP="○" ICON_PENDING="◦" ICON_RUN="▶"
else
  BOX_TL="+" BOX_TR="+" BOX_BL="+" BOX_BR="+" BOX_H="=" BOX_V="|"
  ICON_OK="OK" ICON_FAIL="X" ICON_SKIP="-" ICON_PENDING="." ICON_RUN=">"
fi

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

  --yes, -y              Non-interactive: assume yes for prompts (except sudo/password). Default on.
  --interactive          Ask yes/no per component instead of installing everything.
  --components LIST      Comma-separated: adb,metasploit,scrcpy,nmap,hardax,pip
                         If omitted: adb, metasploit, scrcpy, nmap, and pip
                         (HARDAX is installed via pip / requirements.txt).
                         Use hardax alone to reinstall HARDAX without other tools.
  --skip-pip             Do not run pip install -r requirements.txt
  -h, --help             Show this help

Examples:
  ./install.sh
  ./install.sh --components adb,nmap,pip
  ./install.sh --interactive
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y) YES=1 ;;
    --interactive) INTERACTIVE=1; YES=0 ;;
    --components)
      if [[ $# -lt 2 ]] || [[ "${2:-}" == -* ]] || [[ -z "${2:-}" ]]; then
        echo "Error: --components requires a comma-separated list (e.g. adb,nmap,pip)." >&2
        usage
        exit 1
      fi
      COMPONENTS_RAW="$2"
      shift
      ;;
    --skip-pip) SKIP_PIP=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
  shift
done

if [[ "$SKIP_PIP" -eq 1 ]]; then
  export PSP_SKIP_PIP=1
fi

ui_line() { printf '%s\n' "$*"; }
ui_die() {
  printf '%s%s[ERROR]%s %s\n' "$C_BOLD" "$C_RED" "$C_RESET" "$*" >&2
  exit 1
}

BANNER_INNER_WIDTH=50

banner_pad() {
  local plain="$1"
  local n="${#plain}"
  local pad=$((BANNER_INNER_WIDTH - n))
  if [[ "$pad" -lt 0 ]]; then
    pad=0
  fi
  printf '%*s' "$pad" ''
}

print_banner() {
  local title="PhoneSploit Pro Auto Installer"
  local sub="All-in-one dependency setup"
  local row1="  ${title}"
  local row2="  ${sub}  ${INSTALLER_VERSION}"
  ui_line ""
  ui_line "${C_CYAN}${BOX_TL}$(printf '%*s' "$BANNER_INNER_WIDTH" '' | tr ' ' "${BOX_H}")${BOX_TR}${C_RESET}"
  ui_line "${C_CYAN}${BOX_V}${C_RESET}  ${C_BOLD}${C_MAGENTA}${title}${C_RESET}$(banner_pad "$row1")${C_CYAN}${BOX_V}${C_RESET}"
  ui_line "${C_CYAN}${BOX_V}${C_RESET}  ${C_DIM}${sub}${C_RESET}  ${C_YELLOW}${INSTALLER_VERSION}${C_RESET}$(banner_pad "$row2")${C_CYAN}${BOX_V}${C_RESET}"
  ui_line "${C_CYAN}${BOX_BL}$(printf '%*s' "$BANNER_INNER_WIDTH" '' | tr ' ' "${BOX_H}")${BOX_BR}${C_RESET}"
  ui_line ""
}

print_env_block() {
  local pretty="$1" priv python_ver mode
  if [[ "$(id -u 2>/dev/null)" -eq 0 ]]; then
    priv="root"
  else
    priv="user (may use sudo)"
  fi
  python_ver="$(python3 --version 2>/dev/null || echo 'not found')"
  if [[ "$INTERACTIVE" -eq 1 ]]; then
    mode="Interactive"
  elif [[ -n "$COMPONENTS_RAW" ]]; then
    mode="Custom components"
  else
    mode="Full install (non-interactive)"
  fi
  ui_line "${C_BOLD}Environment${C_RESET}"
  ui_line "  ${C_DIM}OS:${C_RESET}       ${pretty}"
  ui_line "  ${C_DIM}Python:${C_RESET}   ${python_ver}"
  ui_line "  ${C_DIM}Privilege:${C_RESET} ${priv}"
  ui_line "  ${C_DIM}Mode:${C_RESET}     ${mode}"
  ui_line ""
}

print_plan() {
  ui_line "${C_BOLD}Installation plan${C_RESET}"
  local label status color
  for entry in "$@"; do
    label="${entry%%|*}"
    status="${entry#*|}"
    case "$status" in
      pending) color="$C_CYAN"; status="${ICON_PENDING} pending" ;;
      skip) color="$C_DIM"; status="${ICON_SKIP} already installed" ;;
      run) color="$C_GREEN"; status="${ICON_RUN} will install" ;;
      *) color="$C_RESET"; status="$status" ;;
    esac
    ui_line "  ${color}${status}${C_RESET}  ${label}"
  done
  ui_line ""
}

step_begin() {
  local label="$1"
  STEP_CURRENT=$((STEP_CURRENT + 1))
  ui_line ""
  ui_line "${C_BOLD}${C_CYAN}[${STEP_CURRENT}/${STEP_TOTAL}]${C_RESET} ${C_BOLD}${ICON_RUN} ${label}${C_RESET}"
  ui_line "${C_DIM}────────────────────────────────────────${C_RESET}"
}

step_ok() {
  local label="$1"
  SUMMARY_OK+=("$label")
  ui_line "${C_GREEN}${ICON_OK}${C_RESET} ${C_BOLD}Done:${C_RESET} ${label}"
}

step_skip_record() {
  local label="$1"
  SUMMARY_SKIP+=("$label")
}

step_fail() {
  local label="$1" rc="$2" hint="${3:-}"
  SUMMARY_FAIL+=("$label")
  FAILED_COUNT=$((FAILED_COUNT + 1))
  ui_line "${C_RED}${ICON_FAIL}${C_RESET} ${C_BOLD}Failed:${C_RESET} ${label} ${C_DIM}(exit ${rc})${C_RESET}" >&2
  if [[ -n "$hint" ]]; then
    ui_line "  ${C_YELLOW}→${C_RESET} ${hint}" >&2
  fi
}

run_step() {
  local label="$1"
  shift
  step_begin "$label"
  set +e
  "$@"
  local rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    step_ok "$label"
  else
    step_fail "$label" "$rc" "${STEP_HINT:-See messages above or README → Installing external tools.}"
    STEP_HINT=""
  fi
}

print_summary() {
  ui_line ""
  ui_line "${C_BOLD}Summary${C_RESET}"
  if [[ ${#SUMMARY_OK[@]} -gt 0 ]]; then
    ui_line "  ${C_GREEN}${ICON_OK} Installed (${#SUMMARY_OK[@]}):${C_RESET} ${SUMMARY_OK[*]}"
  fi
  if [[ ${#SUMMARY_SKIP[@]} -gt 0 ]]; then
    ui_line "  ${C_DIM}${ICON_SKIP} Skipped (${#SUMMARY_SKIP[@]}):${C_RESET} ${SUMMARY_SKIP[*]}"
  fi
  if [[ ${#SUMMARY_FAIL[@]} -gt 0 ]]; then
    ui_line "  ${C_RED}${ICON_FAIL} Failed (${#SUMMARY_FAIL[@]}):${C_RESET} ${SUMMARY_FAIL[*]}"
  fi
  ui_line ""
  if [[ "$FAILED_COUNT" -gt 0 ]]; then
    ui_line "${C_RED}${C_BOLD}Installation completed with errors.${C_RESET} Fix the failed steps and re-run."
    ui_line ""
    exit 1
  fi
  ui_line "${C_GREEN}${C_BOLD}Installation completed successfully.${C_RESET}"
  ui_line ""
  ui_line "If commands are still not found, open a new terminal (PATH updates)."
  ui_line "Activate the virtual environment and run:"
  ui_line "  ${C_CYAN}source .venv/bin/activate${C_RESET}"
  ui_line "  ${C_CYAN}python3 phonesploitpro.py${C_RESET}"
  ui_line ""
}

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

IS_ROOT=0
[[ "$(id -u 2>/dev/null)" -eq 0 ]] && IS_ROOT=1

run_as_root() {
  if [[ "$IS_ROOT" -eq 1 ]]; then
    "$@"
    return $?
  elif have_cmd sudo; then
    sudo "$@"
    return $?
  else
    STEP_HINT="Re-run as root or install sudo."
    ui_line "${C_RED}This step requires root privileges.${C_RESET}" >&2
    return 1
  fi
}

APT_UPDATED=0
apt_update_once() {
  if [[ "$APT_UPDATED" -eq 1 ]]; then
    return 0
  fi
  export DEBIAN_FRONTEND=noninteractive
  run_as_root apt-get update || return 1
  APT_UPDATED=1
}

have_adb() { have_cmd adb; }
have_nmap() { have_cmd nmap; }
have_scrcpy() { have_cmd scrcpy; }
have_metasploit() { have_cmd msfconsole && have_cmd msfvenom; }
have_hardax() {
  have_cmd hardax && return 0
  local venv="$SCRIPT_DIR/.venv"
  [[ -x "$venv/bin/hardax" ]] && return 0
  return 1
}

have_pip_reqs() {
  local venv="$SCRIPT_DIR/.venv"
  local pip="$venv/bin/pip"
  [[ -d "$venv" && -x "$pip" ]] || return 1
  [[ -f "$SCRIPT_DIR/requirements.txt" ]] || return 0
  local req pkg
  while IFS= read -r req || [[ -n "$req" ]]; do
    req="${req%%#*}"
    req="$(echo "$req" | tr -d '[:space:]')"
    [[ -z "$req" ]] && continue
    pkg="${req%%[<>=!~]*}"
    if ! "$pip" show "$pkg" &>/dev/null; then
      return 1
    fi
  done < "$SCRIPT_DIR/requirements.txt"
  return 0
}

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

ensure_python() {
  if ! have_cmd python3; then
    ui_die "python3 not found. Install Python 3.10+ (see README), then re-run this script."
  fi
  python3 - <<'PY' || ui_die "Python 3.10 or newer is required."
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PY
}

ensure_venv_module() {
  if python3 -c "import venv" 2>/dev/null; then
    return 0
  fi
  ui_line "${C_YELLOW}Python venv module missing; installing OS package…${C_RESET}"
  case "$OS_KIND" in
    debian)
      apt_update_once || return 1
      run_as_root apt-get install -y python3-venv python3-pip || return 1
      ;;
    fedora)
      run_as_root dnf install -y python3 || return 1
      ;;
    arch)
      run_as_root pacman -S --needed --noconfirm python || return 1
      ;;
    opensuse)
      run_as_root zypper --non-interactive install python3 || return 1
      ;;
    alpine)
      run_as_root apk add --no-cache py3-pip py3-virtualenv || return 1
      ;;
    macos|termux)
      ;;
    *)
      STEP_HINT="Install python3-venv manually, then re-run."
      ui_line "${C_RED}Cannot install python3-venv automatically on this OS.${C_RESET}" >&2
      return 1
      ;;
  esac
  if ! python3 -c "import venv" 2>/dev/null; then
    STEP_HINT="Install python3-venv manually, then re-run."
    ui_line "${C_RED}python3-venv still unavailable after package install.${C_RESET}" >&2
    return 1
  fi
}

create_venv_if_needed() {
  local venv="$SCRIPT_DIR/.venv"
  if [[ -d "$venv" ]]; then
    return 0
  fi
  ensure_venv_module || return 1
  ui_line "Creating virtual environment at .venv…"
  python3 -m venv "$venv" || return 1
}

shellenv_brew() {
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -f /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
}

ensure_brew() {
  if have_cmd brew; then
    return 0
  fi
  if [[ -f /opt/homebrew/bin/brew ]]; then
    shellenv_brew
    have_cmd brew && return 0
  fi
  if [[ -f /usr/local/bin/brew ]]; then
    shellenv_brew
    have_cmd brew && return 0
  fi
  ui_line "${C_YELLOW}Homebrew is not installed (needed on macOS for several tools).${C_RESET}"
  if [[ "$YES" -eq 0 ]]; then
    if ! prompt_yes "Install Homebrew now (official install script)?"; then
      STEP_HINT="Install Homebrew manually and re-run."
      return 1
    fi
  fi
  local brew_install="/tmp/psp-brew-install.sh"
  if ! curl -fsSL "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh" -o "$brew_install"; then
    STEP_HINT="Check your network connection and try again."
    ui_line "${C_RED}Failed to download Homebrew install script.${C_RESET}" >&2
    return 1
  fi
  if [[ "$YES" -eq 1 ]]; then
    NONINTERACTIVE=1 /bin/bash "$brew_install" || { rm -f "$brew_install"; return 1; }
  else
    /bin/bash "$brew_install" || { rm -f "$brew_install"; return 1; }
  fi
  rm -f "$brew_install"
  shellenv_brew
  if ! have_cmd brew; then
    STEP_HINT="Open a new terminal or add Homebrew to PATH, then re-run."
    ui_line "${C_RED}Homebrew install finished but brew was not found on PATH.${C_RESET}" >&2
    return 1
  fi
}

install_adb() {
  case "$OS_KIND" in
    debian)
      apt_update_once || return 1
      run_as_root apt-get install -y adb || return 1
      ;;
    fedora)
      run_as_root dnf install -y android-tools || return 1
      ;;
    arch)
      run_as_root pacman -S --needed --noconfirm android-tools || return 1
      ;;
    opensuse)
      run_as_root zypper --non-interactive install android-tools || {
        STEP_HINT="On openSUSE you may need the hardware repo — see software.opensuse.org/package/android-tools"
        return 1
      }
      ;;
    alpine)
      run_as_root apk add --no-cache android-tools || return 1
      ;;
    macos)
      ensure_brew || return 1
      brew install android-platform-tools || return 1
      ;;
    termux)
      pkg update -y || return 1
      pkg install -y android-tools || return 1
      ;;
    *)
      STEP_HINT="See README → Installing external tools → ADB."
      ui_line "${C_RED}ADB: unsupported OS for automatic install.${C_RESET}" >&2
      return 1
      ;;
  esac
}

install_nmap() {
  case "$OS_KIND" in
    debian)
      apt_update_once || return 1
      run_as_root apt-get install -y nmap || return 1
      ;;
    fedora)
      run_as_root dnf install -y nmap || return 1
      ;;
    arch)
      run_as_root pacman -S --needed --noconfirm nmap || return 1
      ;;
    opensuse)
      run_as_root zypper --non-interactive install nmap || return 1
      ;;
    alpine)
      run_as_root apk add --no-cache nmap || return 1
      ;;
    macos)
      ensure_brew || return 1
      brew install nmap || return 1
      ;;
    termux)
      pkg update -y || return 1
      pkg install -y nmap || return 1
      ;;
    *)
      STEP_HINT="See README → Nmap."
      ui_line "${C_RED}Nmap: unsupported OS for automatic install.${C_RESET}" >&2
      return 1
      ;;
  esac
}

install_scrcpy() {
  case "$OS_KIND" in
    debian)
      apt_update_once || return 1
      if ! run_as_root apt-get install -y scrcpy; then
        STEP_HINT="On some distros (e.g. Kali) build scrcpy from https://github.com/Genymobile/scrcpy"
        return 1
      fi
      ;;
    fedora)
      run_as_root dnf install -y scrcpy || return 1
      ;;
    arch)
      run_as_root pacman -S --needed --noconfirm scrcpy || return 1
      ;;
    opensuse)
      run_as_root zypper --non-interactive install scrcpy || {
        STEP_HINT="Try building from https://github.com/Genymobile/scrcpy"
        return 1
      }
      ;;
    alpine)
      run_as_root apk add --no-cache scrcpy 2>/dev/null || {
        STEP_HINT="scrcpy on Alpine may need edge/community; see scrcpy GitHub."
        return 1
      }
      ;;
    macos)
      ensure_brew || return 1
      brew install scrcpy || return 1
      ;;
    termux)
      pkg update -y || return 1
      pkg install -y scrcpy || {
        STEP_HINT="Termux: scrcpy may be unavailable; see README."
        return 1
      }
      ;;
    *)
      STEP_HINT="See README → scrcpy."
      ui_line "${C_RED}scrcpy: unsupported OS for automatic install.${C_RESET}" >&2
      return 1
      ;;
  esac
}

install_metasploit() {
  case "$OS_KIND" in
    macos)
      ensure_brew || return 1
      brew install --cask metasploit || return 1
      ;;
    debian|fedora|arch|opensuse|alpine)
      (
        set -e
        tmp="$(mktemp -d)"
        cleanup() { rm -rf "$tmp"; }
        trap cleanup EXIT
        curl -fsSL "https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb" \
          -o "$tmp/msfinstall"
        chmod 755 "$tmp/msfinstall"
        ui_line "Running Rapid7 msfinstall (may prompt for sudo / package manager)…"
        cd "$tmp"
        if [[ "$IS_ROOT" -eq 1 ]]; then
          ./msfinstall
        elif have_cmd sudo; then
          sudo ./msfinstall
        else
          ui_line "${C_RED}Metasploit install requires root (sudo).${C_RESET}" >&2
          exit 1
        fi
      )
      ;;
    termux)
      STEP_HINT="Use a full Linux desktop or see Metasploit docs."
      return 1
      ;;
    *)
      STEP_HINT="See README → Metasploit-Framework."
      ui_line "${C_RED}Metasploit: unsupported OS for automatic install.${C_RESET}" >&2
      return 1
      ;;
  esac
}

install_pip_reqs() {
  if [[ ! -f "$SCRIPT_DIR/requirements.txt" ]]; then
    ui_line "${C_YELLOW}requirements.txt not found; skipping pip.${C_RESET}"
    return 0
  fi
  create_venv_if_needed || return 1
  local venv="$SCRIPT_DIR/.venv"
  ui_line "Installing Python dependencies into .venv…"
  "$venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" || return 1
}

install_hardax() {
  create_venv_if_needed || return 1
  local venv="$SCRIPT_DIR/.venv"
  ui_line "Installing HARDAX (Android security auditor) into .venv…"
  "$venv/bin/pip" install 'hardax>=6.2.0' || return 1
}

# --- Components ---
want_adb=0
want_metasploit=0
want_scrcpy=0
want_nmap=0
want_hardax=0
want_pip=0

VALID_COMPONENTS="adb metasploit scrcpy nmap hardax pip"

set_component() {
  local p
  p="$(echo "$1" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  [[ -z "$p" ]] && return 0
  case "$p" in
    adb) want_adb=1; return 0 ;;
    metasploit) want_metasploit=1; return 0 ;;
    scrcpy) want_scrcpy=1; return 0 ;;
    nmap) want_nmap=1; return 0 ;;
    hardax) want_hardax=1; return 0 ;;
    pip) want_pip=1; return 0 ;;
    *) return 1 ;;
  esac
}

print_banner

ensure_python

if [[ -n "$COMPONENTS_RAW" ]]; then
  unknown=()
  _old_ifs="$IFS"
  IFS=','
  for p in $COMPONENTS_RAW; do
    p="$(echo "$p" | tr -d '[:space:]')"
    [[ -z "$p" ]] && continue
    if ! set_component "$p"; then
      unknown+=("$(echo "$p" | tr '[:upper:]' '[:lower:]')")
    fi
  done
  IFS="$_old_ifs"
  if [[ ${#unknown[@]} -gt 0 ]]; then
    ui_die "Unknown component(s): ${unknown[*]}. Valid: ${VALID_COMPONENTS}"
  fi
elif [[ "$INTERACTIVE" -eq 1 ]]; then
  print_env_block "$PRETTY_OS"
  ui_line "${C_BOLD}Choose what to install:${C_RESET}"
  prompt_yes "Install ADB (Android platform tools)?" && want_adb=1
  prompt_yes "Install Metasploit-Framework (large download)?" && want_metasploit=1
  prompt_yes "Install scrcpy?" && want_scrcpy=1
  prompt_yes "Install Nmap?" && want_nmap=1
  prompt_yes "Install HARDAX (vulnerability analysis, pip)?" && want_hardax=1
  prompt_yes "Run pip install -r requirements.txt?" && want_pip=1
else
  want_adb=1
  want_metasploit=1
  want_scrcpy=1
  want_nmap=1
  want_hardax=0
  want_pip=1
fi

if [[ "${PSP_SKIP_PIP:-}" == "1" ]] || [[ "$SKIP_PIP" -eq 1 ]]; then
  want_pip=0
fi

if [[ "$OS_KIND" = "unknown" ]]; then
  ui_die "Could not detect a supported package manager. Install dependencies manually (README → Installing external tools)."
fi

if [[ "$want_adb$want_metasploit$want_scrcpy$want_nmap$want_hardax$want_pip" = "000000" ]]; then
  ui_line "Nothing selected. Exiting."
  exit 0
fi

if [[ "$INTERACTIVE" -ne 1 ]] || [[ -n "$COMPONENTS_RAW" ]]; then
  print_env_block "$PRETTY_OS"
fi

# Mark already-installed (skip) and build plan
plan_entries=()
count_want=0

if [[ "$want_adb" -eq 1 ]]; then
  if have_adb; then
    want_adb=0
    step_skip_record "ADB"
    plan_entries+=("ADB|skip")
  else
    plan_entries+=("ADB|run")
    count_want=$((count_want + 1))
  fi
fi
if [[ "$want_nmap" -eq 1 ]]; then
  if have_nmap; then
    want_nmap=0
    step_skip_record "Nmap"
    plan_entries+=("Nmap|skip")
  else
    plan_entries+=("Nmap|run")
    count_want=$((count_want + 1))
  fi
fi
if [[ "$want_scrcpy" -eq 1 ]]; then
  if have_scrcpy; then
    want_scrcpy=0
    step_skip_record "scrcpy"
    plan_entries+=("scrcpy|skip")
  else
    plan_entries+=("scrcpy|run")
    count_want=$((count_want + 1))
  fi
fi
if [[ "$want_metasploit" -eq 1 ]]; then
  if have_metasploit; then
    want_metasploit=0
    step_skip_record "Metasploit"
    plan_entries+=("Metasploit|skip")
  else
    plan_entries+=("Metasploit|run")
    count_want=$((count_want + 1))
  fi
fi
if [[ "$want_pip" -eq 1 ]]; then
  if have_pip_reqs; then
    want_pip=0
    step_skip_record "Python packages (pip)"
    plan_entries+=("Python packages (pip)|skip")
  else
    plan_entries+=("Python packages (pip)|run")
    count_want=$((count_want + 1))
  fi
fi
if [[ "$want_hardax" -eq 1 ]]; then
  if have_hardax; then
    want_hardax=0
    step_skip_record "HARDAX"
    plan_entries+=("HARDAX|skip")
  else
    plan_entries+=("HARDAX|run")
    count_want=$((count_want + 1))
  fi
fi

print_plan "${plan_entries[@]}"

if [[ "$count_want" -eq 0 ]]; then
  print_summary
  exit 0
fi

STEP_TOTAL="$count_want"

if [[ "$want_adb" -eq 1 ]]; then
  run_step "Installing ADB (Android platform tools)" install_adb
fi
if [[ "$want_nmap" -eq 1 ]]; then
  run_step "Installing Nmap" install_nmap
fi
if [[ "$want_scrcpy" -eq 1 ]]; then
  run_step "Installing scrcpy" install_scrcpy
fi
if [[ "$want_metasploit" -eq 1 ]]; then
  run_step "Installing Metasploit-Framework" install_metasploit
fi
if [[ "$want_pip" -eq 1 ]]; then
  run_step "Installing Python packages (pip)" install_pip_reqs
fi
if [[ "$want_hardax" -eq 1 ]]; then
  run_step "Installing HARDAX" install_hardax
fi

print_summary
