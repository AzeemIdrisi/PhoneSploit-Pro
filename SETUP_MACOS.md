# PhoneSploit-Pro — macOS Setup Guide

Tested on: macOS (Apple Silicon / arm64)

---

## Prerequisites

| Tool | Version | Source |
|---|---|---|
| Python | 3.10+ | [python.org](https://www.python.org/) |
| adb | bundled with scrcpy | [scrcpy releases](https://github.com/Genymobile/scrcpy/releases) |
| scrcpy | 3.3.4+ | [scrcpy releases](https://github.com/Genymobile/scrcpy/releases) |
| nmap | 7.99+ | [nmap.org](https://nmap.org/download.html) |
| Metasploit Framework | 6.4.124+ | [osx.metasploit.com](https://osx.metasploit.com/) |

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git
cd PhoneSploit-Pro
```

## Step 2 — Install Python dependencies

```bash
pip3 install -r requirements.txt
```

Installs: `python-nmap`, `rich`

## Step 3 — Install scrcpy (includes adb)

Download the arm64 tarball from the [scrcpy releases page](https://github.com/Genymobile/scrcpy/releases):

```bash
# Extract the archive
tar -xzf scrcpy-macos-aarch64-v3.3.4.tar.gz

# Add to PATH permanently
echo 'export PATH="$HOME/Downloads/scrcpy-macos-aarch64-v3.3.4:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify:
```bash
adb version
scrcpy --version
```

## Step 4 — Install nmap

```bash
brew install nmap
```

Or download the installer from [nmap.org](https://nmap.org/download.html).

## Step 5 — Install Metasploit Framework

### Download

Get the latest macOS package from [osx.metasploit.com](https://osx.metasploit.com/):

```bash
curl -L -o metasploitframework-latest.pkg https://osx.metasploit.com/metasploitframework-latest.pkg
curl -L -o metasploitframework-latest.pkg.asc https://osx.metasploit.com/metasploitframework-latest.pkg.asc
```

### Verify PGP signature (recommended)

```bash
# Install gnupg if not present
brew install gnupg

# Import Rapid7's official signing key
curl -sL https://apt.metasploit.com/metasploit-framework.gpg.key | gpg --import

# Verify — look for "Good signature from Release Engineering <r7_re@rapid7.com>"
gpg --verify metasploitframework-latest.pkg.asc metasploitframework-latest.pkg
```

### Install

```bash
sudo installer -pkg metasploitframework-latest.pkg -target /
```

### Add to PATH

```bash
echo 'export PATH="/opt/metasploit-framework/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify:
```bash
msfconsole --version
```

### Clean up

```bash
rm metasploitframework-latest.pkg metasploitframework-latest.pkg.asc
```

---

## Running PhoneSploit-Pro

```bash
python3 phonesploitpro.py
```

---

## Notes

- **Apple Silicon**: The Metasploit macOS package is built for x86\_64 and runs via Rosetta 2 on Apple Silicon. Ensure Rosetta 2 is installed (`softwareupdate --install-rosetta`).
- **adb over Wi-Fi**: PhoneSploit-Pro connects to Android devices over TCP port 5555. Make sure USB debugging and ADB over Wi-Fi are enabled on the target device first (see the project README for the full device setup tutorial).
- **Metasploit features**: The "Hack device completely" option requires `msfvenom` and `msfconsole`, both included in the Metasploit Framework installation.
- **Updating Metasploit**: Run `msfupdate` to pull the latest nightly build.
