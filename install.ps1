# PhoneSploit Pro — dependency installer for Windows (Chocolatey + official Metasploit MSI).
# Run from an elevated PowerShell when installing system-wide tools: "Run as administrator".

[CmdletBinding()]
param(
    [string] $Components = "",
    [switch] $NonInteractive,
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
    if ($NonInteractive -and -not $SkipChocolateyInstall) {
        Install-Chocolatey
        $choco = Get-ChocoExe
        if ($choco) { return $choco }
        throw "Chocolatey install finished but choco.exe was not found. Restart PowerShell and try again."
    }
    if ($NonInteractive) {
        throw "Chocolatey is required. Install from https://chocolatey.org/install"
    }
    $ans = Read-Host "Chocolatey is not installed. Install it now? [y/N]"
    if ($ans -notmatch '^[yY]') {
        throw "Chocolatey is required for automatic installs on Windows. Install manually and re-run."
    }
    Install-Chocolatey
    $choco = Get-ChocoExe
    if (-not $choco) { throw "choco.exe not found after install. Restart PowerShell and re-run." }
    return $choco
}

function Refresh-PathFromMachine {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
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
    pip         = $false
}

if ($Components -ne "") {
    foreach ($p in $Components.Split(",")) {
        $k = $p.Trim().ToLowerInvariant()
        if ($k -eq "") { continue }
        switch ($k) {
            "adb" { $want.adb = $true }
            "metasploit" { $want.metasploit = $true }
            "scrcpy" { $want.scrcpy = $true }
            "nmap" { $want.nmap = $true }
            "pip" { $want.pip = $true }
            default { Write-Warn "Unknown component ignored: $k" }
        }
    }
} else {
    if ($NonInteractive) {
        throw "With -NonInteractive you must pass -Components, e.g. -Components adb,nmap,scrcpy,pip"
    }
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
    $want.pip = Ask "Run pip install -r requirements.txt?"
}

$any = $want.Values -contains $true
if (-not $any) {
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
        Write-Info "pip install -r requirements.txt …"
        $req = Join-Path $ScriptDir "requirements.txt"
        if ($usePyLauncher) {
            & py -3 -m pip install -r $req
        } else {
            & $pythonExe -m pip install -r $req
        }
    } else {
        Write-Warn "requirements.txt not found; skipping pip."
    }
}

Write-Host ""
Write-Info "Done. If tools are still not found, close this window and open a new terminal (PATH refresh)."
Write-Info "Then run: python phonesploitpro.py"
Write-Host ""
