param(
    [int]$IntervalSeconds = 3,
    [switch]$Once
)

$ErrorActionPreference = "Continue"

function Write-Log {
    param([string]$Message, [ConsoleColor]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Test-AdbDevice {
    $state = adb get-state 2>$null
    return $LASTEXITCODE -eq 0 -and $state -eq "device"
}

function Get-WifiStatus {
    adb shell cmd wifi status 2>$null
}

function Enable-Wifi {
    Write-Log "Wi-Fi desactive detecte, activation via ADB shell..." Yellow
    adb shell cmd wifi set-wifi-enabled enabled | Out-Null
    Start-Sleep -Seconds 2
    $status = Get-WifiStatus

    if ($status -match "Wifi is enabled") {
        Write-Log "Wi-Fi reactive." Green
    } else {
        Write-Log "Activation demandee, mais le Wi-Fi n'est pas encore vu comme enabled." DarkYellow
    }
}

Write-Log "Auto WiFi ADB monitor demarre. Ctrl+C pour arreter." Cyan
Write-Log "Intervalle: $IntervalSeconds seconde(s)." DarkGray

do {
    if (-not (Test-AdbDevice)) {
        Write-Log "Aucun appareil ADB connecte." Red
    } else {
        $status = Get-WifiStatus
        if ($status -match "Wifi is disabled") {
            Enable-Wifi
        } elseif ($status -match "Wifi is enabled") {
            Write-Log "Wi-Fi deja actif." DarkGray
        } else {
            Write-Log "Statut Wi-Fi inconnu: $($status -join ' ')" DarkYellow
        }
    }

    if (-not $Once) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while (-not $Once)
