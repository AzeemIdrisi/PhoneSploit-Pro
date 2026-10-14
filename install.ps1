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

$versionFile = Join-Path $ScriptDir "VERSION"
if (-not (Test-Path $versionFile)) {
    throw "VERSION file not found at $versionFile"
}
$InstallerVersion = (Get-Content $versionFile -Raw).Trim()
if ($InstallerVersion -eq "") {
    throw "VERSION file is empty: $versionFile"
}

$script:StepCurrent = 0
$script:StepTotal = 0
$script:FailedCount = 0
$script:SummaryOk = @()
$script:SummarySkip = @()
$script:SummaryFail = @()
$script:StepHint = ""

if ($Interactive -and $NonInteractive) {
    throw "Use either -Interactive or -NonInteractive, not both."
}

function Test-UseColor {
    if ($env:NO_COLOR) { return $false }
    return [Console]::IsOutputRedirected -eq $false
}

$UseColor = Test-UseColor

$script:BannerInnerWidth = 50
$encName = [Console]::OutputEncoding.WebName
$script:UseUtf8Box = ($encName -match 'utf-8|65001')
if ($script:UseUtf8Box) {
    $script:BoxTL = [string][char]0x2554
    $script:BoxTR = [string][char]0x2557
    $script:BoxBL = [string][char]0x255A
    $script:BoxBR = [string][char]0x255D
    $script:BoxH = [string][char]0x2550
    $script:BoxV = [string][char]0x2551
} else {
    $script:BoxTL = "+"; $script:BoxTR = "+"; $script:BoxBL = "+"; $script:BoxBR = "+"
    $script:BoxH = "-"; $script:BoxV = "|"
}

function Write-UiLine([string]$Text) { Write-Host $Text }

function Get-BoxPad([string]$PlainRow) {
    $pad = $script:BannerInnerWidth - $PlainRow.Length
    if ($pad -lt 0) { $pad = 0 }
    return (" " * $pad)
}

function Write-Banner {
    $title = "PhoneSploit Pro Auto Installer"
    $sub = "All-in-one dependency setup"
    $row1 = "  $title"
    $row2 = "  $sub  $InstallerVersion"
    $top = $script:BoxTL + ($script:BoxH * $script:BannerInnerWidth) + $script:BoxTR
    $bottom = $script:BoxBL + ($script:BoxH * $script:BannerInnerWidth) + $script:BoxBR
    Write-UiLine ""
    if ($UseColor) {
        Write-Host $top -ForegroundColor Cyan
        Write-Host "$($script:BoxV)$row1$(Get-BoxPad $row1)$($script:BoxV)" -ForegroundColor Cyan
        Write-Host "$($script:BoxV)$row2$(Get-BoxPad $row2)$($script:BoxV)" -ForegroundColor Cyan
        Write-Host $bottom -ForegroundColor Cyan
    } else {
        Write-UiLine $top
        Write-UiLine "$($script:BoxV)$row1$(Get-BoxPad $row1)$($script:BoxV)"
        Write-UiLine "$($script:BoxV)$row2$(Get-BoxPad $row2)$($script:BoxV)"
        Write-UiLine $bottom
    }
    Write-UiLine ""
}

function Write-EnvBlock {
    param([string]$Mode, [string]$PythonLabel)
    $admin = if (Test-IsAdmin) { "Administrator" } else { "User (some steps need elevation)" }
    Write-UiLine "Environment"
    Write-UiLine "  OS:         Windows $([Environment]::OSVersion.Version)"
    Write-UiLine "  Python:     $PythonLabel"
    Write-UiLine "  Privilege:  $admin"
    Write-UiLine "  Mode:       $Mode"
    Write-UiLine ""
}

function Write-Plan {
    param([string[]]$Entries)
    Write-UiLine "Installation plan"
    foreach ($entry in $Entries) {
        $parts = $entry -split '\|', 2
        $label = $parts[0]
        $status = $parts[1]
        switch ($status) {
            "run" {
                if ($UseColor) { Write-Host "  > will install  $label" -ForegroundColor Green }
                else { Write-UiLine "  > will install  $label" }
            }
            "skip" {
                if ($UseColor) { Write-Host "  - already installed  $label" -ForegroundColor DarkGray }
                else { Write-UiLine "  - already installed  $label" }
            }
            default { Write-UiLine "  $status  $label" }
        }
    }
    Write-UiLine ""
}

function Start-InstallStep {
    param([string]$Label)
    $script:StepCurrent++
    Write-UiLine ""
    if ($UseColor) {
        Write-Host "[$($script:StepCurrent)/$($script:StepTotal)] > $Label" -ForegroundColor Cyan
    } else {
        Write-UiLine "[$($script:StepCurrent)/$($script:StepTotal)] > $Label"
    }
    Write-UiLine "----------------------------------------"
}

function Complete-InstallStep {
    param([string]$Label, [int]$ExitCode)
    if ($ExitCode -eq 0) {
        $script:SummaryOk += $Label
        if ($UseColor) { Write-Host "OK  Done: $Label" -ForegroundColor Green }
        else { Write-UiLine "OK  Done: $Label" }
    } else {
        $script:SummaryFail += $Label
        $script:FailedCount++
        if ($UseColor) { Write-Host "X   Failed: $Label (exit $ExitCode)" -ForegroundColor Red }
        else { Write-UiLine "X   Failed: $Label (exit $ExitCode)" }
        if ($script:StepHint) {
            if ($UseColor) { Write-Host "    -> $($script:StepHint)" -ForegroundColor Yellow }
            else { Write-UiLine "    -> $($script:StepHint)" }
            $script:StepHint = ""
        }
    }
}

function Invoke-InstallStep {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    Start-InstallStep $Label
    $code = 0
    $global:LASTEXITCODE = 0
    try {
        & $Action
        if ($null -ne $LASTEXITCODE -and $LASTEXITCODE -ne 0) { $code = $LASTEXITCODE }
    } catch {
        Write-Host $_.Exception.Message -ForegroundColor Red
        $code = 1
        if (-not $script:StepHint) { $script:StepHint = $_.Exception.Message }
    }
    Complete-InstallStep $Label $code
}

function Write-Summary {
    Write-UiLine ""
    Write-UiLine "Summary"
    if ($script:SummaryOk.Count -gt 0) {
        Write-UiLine "  Installed ($($script:SummaryOk.Count)): $($script:SummaryOk -join ', ')"
    }
    if ($script:SummarySkip.Count -gt 0) {
        Write-UiLine "  Skipped ($($script:SummarySkip.Count)): $($script:SummarySkip -join ', ')"
    }
    if ($script:SummaryFail.Count -gt 0) {
        if ($UseColor) { Write-Host "  Failed ($($script:SummaryFail.Count)): $($script:SummaryFail -join ', ')" -ForegroundColor Red }
        else { Write-UiLine "  Failed ($($script:SummaryFail.Count)): $($script:SummaryFail -join ', ')" }
    }
    Write-UiLine ""
    if ($script:FailedCount -gt 0) {
        if ($UseColor) { Write-Host "Installation completed with errors. Fix failed steps and re-run." -ForegroundColor Red }
        else { Write-UiLine "Installation completed with errors. Fix failed steps and re-run." }
        Write-UiLine ""
        exit 1
    }
    if ($UseColor) { Write-Host "Installation completed successfully." -ForegroundColor Green }
    else { Write-UiLine "Installation completed successfully." }
    Write-UiLine ""
    Write-UiLine "If tools are still not found, close this window and open a new terminal (PATH refresh)."
    Write-UiLine "Activate the virtual environment and run:"
    Write-UiLine "  .\.venv\Scripts\activate"
    Write-UiLine "  python phonesploitpro.py"
    Write-UiLine ""
}

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
        throw "Chocolatey installation requires Administrator PowerShell. Right-click PowerShell -> Run as administrator."
    }
    Write-UiLine "Installing Chocolatey (official script)..."
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

function Add-MetasploitPathIfNeeded {
    $msfBin = "C:\metasploit-framework\bin"
    if (-not (Test-Path $msfBin)) { return }
    $pathParts = $env:Path -split ';'
    if ($pathParts -contains $msfBin) { return }
    $env:Path = "$msfBin;$env:Path"
    if (Test-IsAdmin) {
        $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        if ($machinePath -notlike "*$msfBin*") {
            [Environment]::SetEnvironmentVariable("Path", "$msfBin;$machinePath", "Machine")
        }
    }
}

function Test-IsWindowsAppsStub {
    param([string]$Path)
    return ($Path -like "*\Microsoft\WindowsApps\*")
}

function Resolve-Python310 {
    $usePyLauncher = $false
    $pythonExe = $null
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $usePyLauncher = $true
            return @{ Exe = $null; UsePyLauncher = $true; Label = ( (& py -3 --version 2>$null) -join '' ) }
        }
    }
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd -and -not (Test-IsWindowsAppsStub $pyCmd.Source)) {
        & $pyCmd.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $pyCmd.Source
            return @{ Exe = $pythonExe; UsePyLauncher = $false; Label = ( (& $pythonExe --version 2>$null) -join '' ) }
        }
    }
    return $null
}

function New-ProjectVenv {
    param([hashtable]$Python)
    $venv = Join-Path $ScriptDir ".venv"
    if (Test-Path $venv) { return $venv }
    Write-UiLine "Creating virtual environment at .venv..."
    if ($Python.UsePyLauncher) {
        & py -3 -m venv $venv
    } else {
        & $Python.Exe -m venv $venv
    }
    if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment (exit $LASTEXITCODE)." }
    return $venv
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

    foreach ($line in Get-Content $req) {
        $line = ($line -split '#', 2)[0].Trim()
        if ($line -eq "") { continue }
        $pkg = ($line -split '[<>=!~]', 2)[0].Trim()
        if ($pkg -eq "") { continue }
        & $pip show $pkg 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { return $false }
    }
    return $true
}

function Download-FileWithProgress {
    param(
        [string]$Uri,
        [string]$OutFile
    )
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        Write-UiLine "Downloading (curl progress bar below)..."
        & curl.exe -L --progress-bar -o $OutFile $Uri
        if ($LASTEXITCODE -ne 0) { throw "Download failed (curl exit $LASTEXITCODE)." }
        return
    }
    Write-UiLine "Downloading..."
    $wc = New-Object System.Net.WebClient
    $progressHandler = {
        param($sender, $e)
        Write-Host -NoNewline ("`r  Downloading... {0,3}%  " -f $e.ProgressPercentage)
    }
    $completeHandler = {
        Write-Host ""
    }
    $wc.add_DownloadProgressChanged($progressHandler)
    $wc.add_DownloadFileCompleted($completeHandler)
    try {
        $wc.DownloadFile($Uri, $OutFile)
    } finally {
        $wc.Dispose()
        $global:LASTEXITCODE = 0
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

    Download-FileWithProgress -Uri $DownloadUrl -OutFile $msi

    Write-UiLine "Running MSI (quiet). This may take several minutes..."
    $p = Start-Process -FilePath "msiexec.exe" -ArgumentList @(
        "/i", $msi,
        "/qn", "/norestart",
        "/L*v", $log
    ) -Wait -PassThru -NoNewWindow

    if ($p.ExitCode -eq 0 -or $p.ExitCode -eq 3010) {
        if ($p.ExitCode -eq 3010) {
            Write-UiLine "Metasploit installed; a reboot may be required (exit 3010)."
        } else {
            Write-UiLine "Metasploit Framework installed."
        }
        Refresh-PathFromMachine
        Add-MetasploitPathIfNeeded
    } else {
        $script:StepHint = "msiexec exit $($p.ExitCode). Log: $log"
        throw "Metasploit MSI install failed with exit code $($p.ExitCode)."
    }
}

function Install-ChocoPackage {
    param(
        [string]$ChocoExe,
        [string]$PackageName
    )
    Write-UiLine "choco install $PackageName -y"
    & $ChocoExe install $PackageName -y
    if ($LASTEXITCODE -ne 0) {
        $script:StepHint = "Try running this script as Administrator."
        throw "choco install $PackageName failed (exit $LASTEXITCODE)."
    }
}

$ValidComponents = @("adb", "metasploit", "scrcpy", "nmap", "hardax", "pip")

$want = @{
    adb        = $false
    metasploit = $false
    scrcpy     = $false
    nmap       = $false
    hardax     = $false
    pip        = $false
}

Write-Banner

$pythonInfo = Resolve-Python310
if (-not $pythonInfo) {
    throw "Python 3.10+ is required. Install from https://www.python.org/ and re-run."
}

if ($Components -ne "") {
    $unknown = @()
    foreach ($p in $Components.Split(",")) {
        $k = $p.Trim().ToLowerInvariant()
        if ($k -eq "") { continue }
        if ($ValidComponents -notcontains $k) {
            $unknown += $k
            continue
        }
        $want[$k] = $true
    }
    if ($unknown.Count -gt 0) {
        throw "Unknown component(s): $($unknown -join ', '). Valid: $($ValidComponents -join ', ')"
    }
} elseif ($Interactive) {
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
} else {
    $want.adb = $true
    $want.metasploit = $true
    $want.scrcpy = $true
    $want.nmap = $true
    $want.hardax = $false
    $want.pip = $true
}

if ($SkipPip) {
    $want.pip = $false
}

if (-not ($want.Values -contains $true)) {
    Write-UiLine "Nothing selected. Exiting."
    exit 0
}

$modeLabel = if ($Interactive) { "Interactive" } elseif ($Components -ne "") { "Custom components" } else { "Full install (non-interactive)" }

Write-EnvBlock -Mode $modeLabel -PythonLabel $pythonInfo.Label

$script:PlanEntries = @()
$script:StepTotal = 0

function Add-PlanItem {
    param([string]$Label, [bool]$Requested, [scriptblock]$TestPresent, [string]$WantKey)
    if (-not $Requested) { return }
    if (& $TestPresent) {
        $script:SummarySkip += $Label
        $script:PlanEntries += "$Label|skip"
        $want[$WantKey] = $false
    } else {
        $script:PlanEntries += "$Label|run"
        $script:StepTotal++
    }
}

Add-PlanItem "ADB" $want.adb { Test-AdbPresent } "adb"
Add-PlanItem "Nmap" $want.nmap { Test-NmapPresent } "nmap"
Add-PlanItem "scrcpy" $want.scrcpy { Test-ScrcpyPresent } "scrcpy"
Add-PlanItem "Metasploit" $want.metasploit { Test-MetasploitPresent } "metasploit"
Add-PlanItem "Python packages (pip)" $want.pip { Test-PipReqsPresent } "pip"
Add-PlanItem "HARDAX" $want.hardax { Test-HardaxPresent } "hardax"

Write-Plan $script:PlanEntries

if ($script:StepTotal -eq 0) {
    Write-Summary
    exit 0
}

$chocoExe = $null
$needChoco = $want.adb -or $want.scrcpy -or $want.nmap

if ($needChoco) {
    try {
        Write-UiLine "Checking Chocolatey..."
        $chocoExe = Ensure-Chocolatey
        if (-not (Test-IsAdmin)) {
            Write-UiLine "Note: Chocolatey installs usually need Administrator rights."
        }
        Refresh-PathFromMachine
    } catch {
        $chocoErr = $_.Exception.Message
        $script:StepHint = "Install Chocolatey manually or run PowerShell as Administrator."
        if ($want.adb) {
            Invoke-InstallStep "Installing ADB (Chocolatey)" { throw $chocoErr }
        }
        if ($want.nmap) {
            Invoke-InstallStep "Installing Nmap (Chocolatey)" { throw $chocoErr }
        }
        if ($want.scrcpy) {
            Invoke-InstallStep "Installing scrcpy (Chocolatey)" { throw $chocoErr }
        }
        $chocoExe = $null
    }
}

if ($want.adb -and $chocoExe) {
    Invoke-InstallStep "Installing ADB (Chocolatey)" {
        Install-ChocoPackage -ChocoExe $chocoExe -PackageName "adb"
        Refresh-PathFromMachine
    }
}

if ($want.nmap -and $chocoExe) {
    Invoke-InstallStep "Installing Nmap (Chocolatey)" {
        Install-ChocoPackage -ChocoExe $chocoExe -PackageName "nmap"
        Refresh-PathFromMachine
    }
}

if ($want.scrcpy -and $chocoExe) {
    Invoke-InstallStep "Installing scrcpy (Chocolatey)" {
        Install-ChocoPackage -ChocoExe $chocoExe -PackageName "scrcpy"
        Refresh-PathFromMachine
    }
}

if ($want.metasploit) {
    Invoke-InstallStep "Installing Metasploit Framework (MSI)" {
        Install-MetasploitMsi
    }
}

if ($want.pip) {
    Invoke-InstallStep "Installing Python packages (pip)" {
        $req = Join-Path $ScriptDir "requirements.txt"
        if (-not (Test-Path $req)) {
            Write-UiLine "requirements.txt not found; skipping pip."
            return
        }
        $venv = New-ProjectVenv $pythonInfo
        $pip = Join-Path $venv "Scripts\pip.exe"
        Write-UiLine "pip install -r requirements.txt"
        & $pip install -r $req
        if ($LASTEXITCODE -ne 0) { throw "pip install failed (exit $LASTEXITCODE)." }
    }
}

if ($want.hardax) {
    Invoke-InstallStep "Installing HARDAX" {
        $venv = New-ProjectVenv $pythonInfo
        $pip = Join-Path $venv "Scripts\pip.exe"
        Write-UiLine 'pip install "hardax>=6.2.0"'
        & $pip install "hardax>=6.2.0"
        if ($LASTEXITCODE -ne 0) { throw "pip install hardax failed (exit $LASTEXITCODE)." }
    }
}

Write-Summary
