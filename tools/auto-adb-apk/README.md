# Auto WiFi Reconnector

APK Android 12+ non-root qui remet le Wi-Fi automatiquement quand il est desactive.

## Point Android important

Ce projet cible Android moderne :

```gradle
minSdk 31
targetSdk 34
```

Avec une app normale non-root qui cible Android 12+, Android bloque `WifiManager#setWifiEnabled(true)`. Pour une remise en route automatique, silencieuse et sans popup, il faut donc un privilege supplementaire :

- Shizuku demarre en mode ADB et donne a l'app un acces shell local ;
- Device Owner / DPC sur un telephone provisionne pour cela ;
- ou app systeme/privilegiee integree a la ROM.

Ce projet implemente Shizuku et Device Owner. La voie testee ici est Shizuku.

## Build

```powershell
.\gradlew.bat assembleDebug
```

APK genere :

```text
app\build\outputs\apk\debug\app-debug.apk
```

## Installation Shizuku

```powershell
powershell -ExecutionPolicy Bypass -File .\install_and_grant_permissions.ps1 -DeviceSerial ad0517022ea6e37b85 -SetupShizuku
```

Le script :

- installe Shizuku si un APK `shizuku-*.apk` est present dans ce dossier ;
- demarre le service Shizuku via ADB ;
- installe Auto WiFi ;
- accorde la permission Shizuku a Auto WiFi ;
- lance Auto WiFi.

Apres ce setup, Auto WiFi lance un UserService Shizuku en mode daemon. La surveillance se fait localement dans ce service shell, sans foreground service Android, sans notification persistante de l'APK et sans icone launcher Auto WiFi. Quand le Wi-Fi est coupe, la remise en route attend 30 secondes avant d'executer la commande.

Pour activer aussi ADB sur le reseau en port 5555 pendant le setup :

```powershell
powershell -ExecutionPolicy Bypass -File .\install_and_grant_permissions.ps1 -DeviceSerial ad0517022ea6e37b85 -SetupShizuku -EnableTcpAdb
```

L'APK maintient ensuite `service.adb.tcp.port=5555` depuis le UserService Shizuku et verifie le port apres les retours Wi-Fi. La premiere activation complete reste faite par le PC avec l'equivalent de `adb tcpip 5555`, car Android refuse a un UID `shell` local de redemarrer `adbd` sans root.

Le script nettoie `persist.adb.tcp.port` avant d'activer ADB reseau. Cette propriete persistante a ete retiree volontairement : sur certaines ROM, elle casse le comportement ADB reseau au lieu de le restaurer au demarrage.

Note : sur un telephone non-root, Shizuku doit etre redemarre apres chaque reboot du telephone.

Pour couper les notifications Shizuku et tenter de masquer son icone launcher :

```powershell
powershell -ExecutionPolicy Bypass -File .\install_and_grant_permissions.ps1 -DeviceSerial ad0517022ea6e37b85 -SetupShizuku -HideShizuku
```

Sur certains builds Android/LineageOS, le masquage de l'icone Shizuku par ADB est refuse par le systeme. Dans ce cas, le script coupe quand meme les notifications et garde le service utilisable.

## Installation Device Owner

Sur un appareil compatible avec l'enrolement DPC, souvent juste apres reset usine et avant l'ajout d'un compte :

```powershell
powershell -ExecutionPolicy Bypass -File .\install_and_grant_permissions.ps1 -SetDeviceOwner
```

Commande ADB equivalente :

```powershell
adb shell dpm set-device-owner com.autowifi.reconnector/.AutoWifiDeviceAdminReceiver
```

Si Android refuse cette commande, l'app ne peut pas obtenir le privilege requis sur cet appareil deja provisionne.

## Test manuel

Avec le telephone connecte en ADB :

```powershell
adb logcat -c
adb shell svc wifi disable
Start-Sleep -Seconds 15
adb shell cmd wifi status
adb logcat -d -v time | findstr /R "ShizukuWifiEnabler WifiShellUserService WifiRestorer WifiPrompt WifiCheckWorker BootReceiver WifiStateReceiver MainActivity"
```

Resultat attendu avec Shizuku :

```text
Wi-Fi is disabled, enabling through Shizuku UserService
Executing shell Wi-Fi enable command
Shizuku Wi-Fi command result, enabled=true
Wifi is enabled
```

Sans Device Owner, les logs afficheront :

```text
Cannot enable Wi-Fi: app is not Device Owner/Profile Owner and Shizuku is not granted
```
