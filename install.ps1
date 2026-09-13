# PhoneSploit Pro — dependency installer for Windows (Chocolatey + official Metasploit MSI).
# Run from an elevated PowerShell when installing system-wide tools: "Run as administrator".

[CmdletBinding()]
param(
    [string] $Components = "",
    [switch] $NonInteractive,
    [switch] $Interactive,
    [switch] $SkipPip,
    [switch] $SkipChocolateyInstall
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

function Write-Info($msg) { Write-Host "[install] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[install] $msg" -ForegroundColor Yellow }

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-ChocoExe {
    $c = Get-Command choco -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $guess = "$env:ProgramData\chocolatey\bin\choco.exe"
    if (Test-Path $guess) { return $guess }
    return $null
}

function Install-Chocolatey {
    if ($SkipChocolateyInstall) {
        throw "Chocolatey is not installed. Install from https://chocolatey.org/install or re-run without -SkipChocolateyInstall."
    }
    if (-not (Test-IsAdmin)) {
        throw "Chocolatey installation requires Administrator PowerShell. Right-click PowerShell → Run as administrator."
    }
    Write-Info "Installing Chocolatey (official script)…"
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

function Ensure-Chocolatey {
    $choco = Get-ChocoExe
    if ($choco) { return $choco }
    if ($SkipChocolateyInstall) {
        throw "Chocolatey is not installed. Install from https://chocolatey.org/install or re-run without -SkipChocolateyInstall."
    }
    if ($Interactive) {
        $ans = Read-Host "Chocolatey is not installed. Install it now? [y/N]"
        if ($ans -notmatch '^[yY]') {
            throw "Chocolatey is required for automatic installs on Windows. Install manually and re-run."
        }
    }
    elseif (-not (Test-IsAdmin)) {
        throw "Chocolatey is not installed. Run PowerShell as Administrator to install Chocolatey automatically, or install from https://chocolatey.org/install"
    }
    Install-Chocolatey
    $choco = Get-ChocoExe
    if (-not $choco) { throw "Chocolatey install finished but choco.exe was not found. Restart PowerShell and try again." }
    return $choco
}

function Refresh-PathFromMachine {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Test-CommandAvailable([string] $Name) {
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-AdbPresent {
    if (Test-CommandAvailable "adb") { return $true }
    $local = Join-Path $ScriptDir "adb.exe"
    return Test-Path $local
}

function Test-MetasploitPresent {
    return (Test-CommandAvailable "msfconsole") -and (Test-CommandAvailable "msfvenom")
}

function Test-ScrcpyPresent {
    if (Test-CommandAvailable "scrcpy") { return $true }
    if (Test-CommandAvailable "scrcpy.exe") { return $true }
    $local = Join-Path $ScriptDir "scrcpy.exe"
    return Test-Path $local
}

function Test-NmapPresent {
    return Test-CommandAvailable "nmap"
}

function Test-HardaxPresent {
    if (Test-CommandAvailable "hardax") { return $true }
    $venvHardax = Join-Path $ScriptDir ".venv\Scripts\hardax.exe"
    return Test-Path $venvHardax
}

function Test-PipReqsPresent {
    $req = Join-Path $ScriptDir "requirements.txt"
    $venv = Join-Path $ScriptDir ".venv"
    $pip = Join-Path $venv "Scripts\pip.exe"
    if (-not (Test-Path $req)) { return $true }
    if (-not (Test-Path $pip)) { return $false }

    $missing = $false
    foreach ($line in Get-Content $req) {
        $line = ($line -split '#', 2)[0].Trim()
        if ($line -eq "") { continue }
        $pkg = ($line -split '[<>=!~]', 2)[0].Trim()
        if ($pkg -eq "") { continue }
        & $pip show $pkg 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { $missing = $true; break }
    }
    return -not $missing
}

function Skip-ComponentsAlreadyPresent([hashtable] $Want) {
    if ($Want.adb -and (Test-AdbPresent)) {
        Write-Info "ADB already installed; skipping."
        $Want.adb = $false
    }
    if ($Want.nmap -and (Test-NmapPresent)) {
        Write-Info "Nmap already installed; skipping."
        $Want.nmap = $false
    }
    if ($Want.scrcpy -and (Test-ScrcpyPresent)) {
        Write-Info "scrcpy already installed; skipping."
        $Want.scrcpy = $false
    }
    if ($Want.metasploit -and (Test-MetasploitPresent)) {
        Write-Info "Metasploit already installed (msfconsole, msfvenom); skipping."
        $Want.metasploit = $false
    }
    if ($Want.hardax -and (Test-HardaxPresent)) {
        Write-Info "HARDAX already installed; skipping."
        $Want.hardax = $false
    }
    if ($Want.pip -and (Test-PipReqsPresent)) {
        Write-Info "Python dependencies already installed in .venv; skipping pip."
        $Want.pip = $false
    }
}

function Install-MetasploitMsi {
    param([string] $DownloadUrl = "https://windows.metasploit.com/metasploitframework-latest.msi")

    if (-not (Test-IsAdmin)) {
        throw "Metasploit Framework MSI install requires Administrator PowerShell."
    }

    $dlRoot = Join-Path $env:APPDATA "Metasploit"
    if (-not (Test-Path $dlRoot)) { New-Item -Path $dlRoot -ItemType Directory | Out-Null }
    $msi = Join-Path $dlRoot "metasploitframework-latest.msi"
    $log = Join-Path $dlRoot "metasploit-install.log"

    Write-Info "Downloading Metasploit Framework MSI…"
    Invoke-WebRequest -UseBasicParsing -Uri $DownloadUrl -OutFile $msi

    Write-Info "Running MSI (quiet). This may take several minutes…"
    $p = Start-Process -FilePath "msiexec.exe" -ArgumentList @(
        "/i", $msi,
        "/qn", "/norestart",
        "/L*v", $log
    ) -Wait -PassThru -NoNewWindow

    if ($p.ExitCode -ne 0) {
        Write-Warn "msiexec exit code: $($p.ExitCode). Log: $log"
    } else {
        Write-Info "Metasploit Framework installed. You may need a new terminal for PATH updates."
    }
}

# --- Parse components ---
$want = @{
    adb         = $false
    metasploit  = $false
    scrcpy      = $false
    nmap        = $false
    hardax      = $false
    pip         = $false
}

# Default: installs all components (adb, metasploit, scrcpy, nmap, pip) without prompts.
# Use -Components to limit what is installed, or -Interactive for per-component and Chocolatey prompts.
# -NonInteractive is kept for backward compatibility (default behavior is already non-interactive).

if ($Components -ne "") {
    foreach ($p in $Components.Split(",")) {
        $k = $p.Trim().ToLowerInvariant()
        if ($k -eq "") { continue }
        switch ($k) {
            "adb" { $want.adb = $true }
            "metasploit" { $want.metasploit = $true }
            "scrcpy" { $want.scrcpy = $true }
            "nmap" { $want.nmap = $true }
            "hardax" { $want.hardax = $true }
            "pip" { $want.pip = $true }
            default { Write-Warn "Unknown component ignored: $k" }
        }
    }
} elseif ($Interactive) {
    Write-Host ""
    Write-Host "PhoneSploit Pro — Windows dependency installer" -ForegroundColor Green
    Write-Host "Detected: Windows $([Environment]::OSVersion.Version)" -ForegroundColor Gray
    Write-Host ""
    function Ask([string]$q) {
        $a = Read-Host "$q [y/N]"
        return ($a -match '^[yY]')
    }
    $want.adb = Ask "Install ADB (Chocolatey package: adb)?"
    $want.metasploit = Ask "Install Metasploit Framework (official MSI, large download)?"
    $want.scrcpy = Ask "Install scrcpy (Chocolatey)?"
    $want.nmap = Ask "Install Nmap (Chocolatey)?"
    $want.hardax = Ask "Install HARDAX (vulnerability analysis, pip)?"
    $want.pip = Ask "Run pip install -r requirements.txt?"
}
else {
    $want.adb = $true
    $want.metasploit = $true
    $want.scrcpy = $true
    $want.nmap = $true
    $want.hardax = $false
    $want.pip = $true
}

if (-not ($want.Values -contains $true)) {
    Write-Host "Nothing selected. Exiting."
    exit 0
}

Write-Host ""
Write-Host "PhoneSploit Pro — Windows dependency installer" -ForegroundColor Green
Write-Host ""

# Python 3.10+ (prefer `python`, else Windows `py -3`)
$pythonExe = $null
$usePyLauncher = $false
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pyCmd) {
    & $pyCmd.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $pythonExe = $pyCmd.Source }
}
if (-not $pythonExe) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { $usePyLauncher = $true }
    }
}
if (-not $pythonExe -and -not $usePyLauncher) {
    throw "Python 3.10+ is required. Install from https://www.python.org/ and re-run."
}

Skip-ComponentsAlreadyPresent $want

$any = $want.Values -contains $true
if (-not $any) {
    Write-Host "Everything requested is already installed. Exiting."
    exit 0
}

$chocoExe = $null
$needChoco = $want.adb -or $want.scrcpy -or $want.nmap
if ($needChoco) {
    $chocoExe = Ensure-Chocolatey
    if (-not (Test-IsAdmin)) {
        Write-Warn "Chocolatey installs usually need Administrator rights. If install fails, re-run PowerShell as Administrator."
    }
    Refresh-PathFromMachine
}

$chocoArgs = @()
if ($want.adb) { $chocoArgs += "adb" }
if ($want.nmap) { $chocoArgs += "nmap" }
if ($want.scrcpy) { $chocoArgs += "scrcpy" }

if ($chocoArgs.Count -gt 0) {
    Write-Info "Installing via Chocolatey: $($chocoArgs -join ', ') …"
    $argList = @("install") + $chocoArgs + @("-y", "--no-progress")
    $proc = Start-Process -FilePath $chocoExe -ArgumentList $argList -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        Write-Warn "choco install exited with code $($proc.ExitCode). Try running this script as Administrator."
    }
    Refresh-PathFromMachine
}

if ($want.metasploit) {
    try {
        Install-MetasploitMsi
    } catch {
        Write-Warn $_.Exception.Message
        Write-Warn "You can install Metasploit manually: https://www.metasploit.com/download"
    }
}

if ($want.pip -and -not $SkipPip) {
    if (Test-Path (Join-Path $ScriptDir "requirements.txt")) {
        $venv = Join-Path $ScriptDir ".venv"
        if (-not (Test-Path $venv)) {
            Write-Info "Creating virtual environment at .venv…"
            if ($usePyLauncher) {
                & py -3 -m venv $venv
            } else {
                & $pythonExe -m venv $venv
            }
        }
        Write-Info "Installing Python dependencies into .venv…"
        $pip = Join-Path $venv "Scripts\pip.exe"
        $req = Join-Path $ScriptDir "requirements.txt"
        & $pip install -r $req
    } else {
        Write-Warn "requirements.txt not found; skipping pip."
    }
}

if ($want.hardax) {
    $venv = Join-Path $ScriptDir ".venv"
    if (-not (Test-Path $venv)) {
        Write-Info "Creating virtual environment at .venv…"
        if ($usePyLauncher) {
            & py -3 -m venv $venv
        } else {
            & $pythonExe -m venv $venv
        }
    }
    Write-Info "Installing HARDAX into .venv…"
    $pip = Join-Path $venv "Scripts\pip.exe"
    & $pip install "hardax>=6.2.0"
}

Write-Host ""
Write-Info "Done. If tools are still not found, close this window and open a new terminal (PATH refresh)."
Write-Info "Activate the virtual environment and run:"
Write-Info "  .\.venv\Scripts\activate"
Write-Info "  python phonesploitpro.py"
Write-Host ""
