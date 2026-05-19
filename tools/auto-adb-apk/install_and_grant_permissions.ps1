param(
    [string]$DeviceSerial = "",
    [switch]$SetupShizuku,
    [switch]$SetDeviceOwner,
    [switch]$HideShizuku,
    [switch]$EnableTcpAdb,
    [int]$TcpAdbPort = 5555
)

# Script pour installer l'APK et configurer Auto WiFi par ADB.
# Connectez le telephone en USB ou en ADB wireless, puis executez ce script.

$PackageName = "com.autowifi.reconnector"
$DeviceAdmin = "$PackageName/.AutoWifiDeviceAdminReceiver"
$ApkPath = "app\build\outputs\apk\debug\app-debug.apk"
$ShizukuPackage = "moe.shizuku.privileged.api"
$AdbArgs = @()
if ($DeviceSerial -ne "") {
    $AdbArgs = @("-s", $DeviceSerial)
}

function Test-WirelessAdbSerial {
    return $DeviceSerial -match "^[0-9]+(?:\.[0-9]+){3}:[0-9]+$"
}

function Test-SelectedAdbDevice {
    $state = adb @AdbArgs get-state 2>$null
    return $LASTEXITCODE -eq 0 -and (($state -join " ").Trim() -eq "device")
}

function Start-ShizukuAdbService {
    Write-Host "Demarrage du service Shizuku via ADB..." -ForegroundColor Yellow
    $packagePath = adb @AdbArgs shell pm path $ShizukuPackage
    if ($LASTEXITCODE -ne 0 -or -not $packagePath) {
        Write-Host "Erreur: Shizuku n'est pas installe." -ForegroundColor Red
        return
    }

    $apkPathOnDevice = ($packagePath -replace "package:", "").Trim()
    $apkDir = Split-Path $apkPathOnDevice -Parent
    $starter = ($apkDir + "/lib/arm64/libshizuku.so").Replace("\", "/")
    adb @AdbArgs shell $starter
}

function Disable-AppNotifications {
    param([string]$TargetPackage)

    Write-Host "Desactivation des notifications pour $TargetPackage..." -ForegroundColor Yellow
    adb @AdbArgs shell cmd appops set $TargetPackage POST_NOTIFICATION ignore 2>$null
    adb @AdbArgs shell pm revoke $TargetPackage android.permission.POST_NOTIFICATIONS 2>$null
}

function Hide-ShizukuLauncher {
    Write-Host "Masquage de l'icone launcher Shizuku..." -ForegroundColor Yellow
    $hideOutput = adb @AdbArgs shell pm disable-user --user 0 "$ShizukuPackage/moe.shizuku.manager.MainActivity" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Info: masquage Shizuku refuse par Android. Le service reste utilisable." -ForegroundColor DarkYellow
    }
}

function Stop-AutoWifiShellUserServices {
    Write-Host "Nettoyage des anciens services shell Auto WiFi..." -ForegroundColor Yellow
    $pidOutput = adb @AdbArgs shell pidof "$PackageName:wifi_shell" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $pidOutput) {
        return
    }

    $pids = (($pidOutput -join " ") -split "\s+") | Where-Object { $_ -match "^\d+$" }
    foreach ($pid in $pids) {
        adb @AdbArgs shell kill -9 $pid 2>$null
    }
}

function Get-DeviceWifiIp {
    $ipOutput = adb @AdbArgs shell ip -4 addr show wlan0 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $ipOutput) {
        return ""
    }

    $ipText = ($ipOutput -join "`n")
    $match = [regex]::Match($ipText, "inet\s+([0-9]+(?:\.[0-9]+){3})/")
    if ($match.Success) {
        return $match.Groups[1].Value
    }

    return ""
}

function Enable-AdbTcp {
    if ($TcpAdbPort -lt 1 -or $TcpAdbPort -gt 65535) {
        Write-Host "Erreur: port ADB TCP invalide: $TcpAdbPort" -ForegroundColor Red
        return
    }

    if (Test-WirelessAdbSerial) {
        Write-Host "Mode ADB wireless detecte: $DeviceSerial" -ForegroundColor Yellow
        Write-Host "ADB TCP/IP est deja utilise; verification/reconnexion sans redemarrer adbd..." -ForegroundColor Yellow
        adb connect $DeviceSerial | Out-Host
        Start-Sleep -Seconds 1
        if (Test-SelectedAdbDevice) {
            Write-Host "ADB wireless pret: $DeviceSerial" -ForegroundColor Green
            adb @AdbArgs shell getprop service.adb.tcp.port
        } else {
            Write-Host "Info: la cible wireless n'est pas prete. Reconnectez-la puis relancez le script." -ForegroundColor DarkYellow
        }
        return
    }

    $wifiIp = Get-DeviceWifiIp
    Write-Host "Nettoyage de l'ancien mode ADB TCP persistant..." -ForegroundColor Yellow
    adb @AdbArgs shell setprop persist.adb.tcp.port "" 2>$null
    adb @AdbArgs shell setprop service.adb.tcp.port $TcpAdbPort

    Write-Host "Activation ADB reseau sur le port $TcpAdbPort..." -ForegroundColor Yellow
    adb @AdbArgs tcpip $TcpAdbPort
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Info: ADB TCP/IP non active. Rebranchez en USB et relancez le script." -ForegroundColor DarkYellow
        return
    }

    Start-Sleep -Seconds 2
    if ($wifiIp -ne "") {
        Write-Host "Connexion ADB reseau: ${wifiIp}:$TcpAdbPort" -ForegroundColor Yellow
        adb connect "${wifiIp}:$TcpAdbPort"
    } else {
        Write-Host "Info: IP Wi-Fi introuvable. Utilisez 'adb connect IP:$TcpAdbPort' manuellement." -ForegroundColor DarkYellow
    }

    Write-Host "Verification des proprietes ADB TCP..." -ForegroundColor Yellow
    adb @AdbArgs shell getprop service.adb.tcp.port
}

Write-Host "=== Installation et configuration automatique de Auto WiFi ===" -ForegroundColor Green
Write-Host ""

Write-Host "Verification de la connexion ADB..." -ForegroundColor Yellow
adb devices
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur: ADB n'est pas disponible ou le telephone n'est pas connecte" -ForegroundColor Red
    exit 1
}

if ($DeviceSerial -ne "" -and -not (Test-SelectedAdbDevice)) {
    Write-Host "Erreur: l'appareil selectionne ne repond pas: $DeviceSerial" -ForegroundColor Red
    Write-Host "Verifiez 'adb devices' puis relancez avec le bon -DeviceSerial." -ForegroundColor DarkYellow
    exit 1
}

Write-Host ""

if ($SetupShizuku) {
    $shizukuApk = Get-ChildItem -Path . -Filter "shizuku-*.apk" | Select-Object -First 1
    if ($null -ne $shizukuApk) {
        Write-Host "Installation de Shizuku..." -ForegroundColor Yellow
        adb @AdbArgs install -r $shizukuApk.FullName
        Write-Host ""
    } else {
        Write-Host "Info: aucun APK Shizuku trouve dans le dossier. Installation Shizuku ignoree." -ForegroundColor DarkGray
        Write-Host ""
    }

    Start-ShizukuAdbService
    Write-Host ""

    Disable-AppNotifications $ShizukuPackage
    Write-Host ""
}

Write-Host "Installation de l'APK..." -ForegroundColor Yellow
adb @AdbArgs install -r $ApkPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de l'installation" -ForegroundColor Red
    exit 1
}

Write-Host ""

if ($SetupShizuku) {
    Write-Host "Accord de la permission Shizuku a Auto WiFi..." -ForegroundColor Yellow
    adb @AdbArgs shell pm grant $PackageName moe.shizuku.manager.permission.API_V23 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Info: permission Shizuku non accordee via ADB. Ouvrez Auto WiFi et acceptez la demande Shizuku sur le telephone." -ForegroundColor DarkYellow
    }
    Write-Host ""
}

Disable-AppNotifications $PackageName
Write-Host ""

if ($SetDeviceOwner) {
    Write-Host "Activation Device Owner/DPC..." -ForegroundColor Yellow
    Write-Host "Cette etape ne fonctionne que sur un appareil provisionne pour cela (souvent apres reset usine, sans compte deja configure)." -ForegroundColor DarkYellow
    adb @AdbArgs shell dpm set-device-owner $DeviceAdmin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur: Device Owner non active. L'app ne pourra pas rallumer le WiFi automatiquement en target Android 12+." -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "Tentative de desactivation de l'optimisation de la batterie..." -ForegroundColor Yellow
adb @AdbArgs shell dumpsys deviceidle whitelist +$PackageName

Write-Host ""

if ($HideShizuku) {
    Hide-ShizukuLauncher
    Write-Host ""
}

Stop-AutoWifiShellUserServices
Write-Host ""

Write-Host "Demarrage de l'application..." -ForegroundColor Yellow
adb @AdbArgs shell am start -n $PackageName/.MainActivity

Write-Host ""

if ($EnableTcpAdb) {
    Enable-AdbTcp
    Write-Host ""
}

Write-Host "=== Installation et configuration terminees ===" -ForegroundColor Green
Write-Host ""
Write-Host "Important:" -ForegroundColor Yellow
Write-Host "- Ce build cible Android 12+ et ne demande pas root." -ForegroundColor White
Write-Host "- Pour rallumer le WiFi automatiquement sans popup, utilisez Shizuku avec -SetupShizuku." -ForegroundColor White
Write-Host "- Ajoutez -HideShizuku pour masquer l'icone launcher Shizuku si Android l'accepte." -ForegroundColor White
Write-Host "- Ajoutez -EnableTcpAdb pour activer ADB reseau depuis USB, ou verifier la cible si vous etes deja en wireless." -ForegroundColor White
Write-Host "- Device Owner reste disponible avec -SetDeviceOwner sur appareil provisionne." -ForegroundColor White
Write-Host ""
Write-Host "Verifiez les logs avec:" -ForegroundColor Yellow
Write-Host "adb logcat | findstr 'ShizukuWifiEnabler WifiShellUserService WifiRestorer WifiPrompt WifiCheckWorker BootReceiver WifiStateReceiver MainActivity'" -ForegroundColor White
