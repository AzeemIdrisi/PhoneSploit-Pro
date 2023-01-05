# PhoneSploit Pro
### PhoneSploit with Metasploit integration.

A hacking script written in `Python 3` to remotely exploit Android devices using `ADB` (Android Debugging Bridge).

This script can automatically __Create__, __Install__, and __Run__ payload to the target device using __Metasploit-Framework__ and __ADB__ to completely hack the Android Device in one click.

# Script Features :
* Connect device using ADB remotely
* List connected devices
* Disconnect all devices
* Access connected device shell
* Stop ADB Server
* Take screenshot and pull it to computer automatically
* List all installed apps in target device
* Download file/folder from target device
* Send file/folder from computer to target device
* Install an APK file from computer to target device
* Run an App
* Uninstall an app
* Screen Record target device screen for a specified time and automatically pull it to computer
* Restart/Reboot the target device
* __Hack Device Completely__ : Automatically create a payload using `msfvenom`, install it, and run it in target device, then automatically launch and setup __Metasploit-Framework__ to get a `meterpreter` session.

Getting a meterpreter session means the device is completely hacked using Metasploit Framework, and you can do anything with it.

# Requirements : 
* [`git`](https://git-scm.com/) : Git
* [`python3`](https://www.python.org/) : Python 3.10 or Newer
* [`adb`](https://developer.android.com/studio/command-line/adb) : Android Debugging Bridge (ADB) from `Android SDK Platform Tools`
* [`metasploit-framework`](https://www.metasploit.com/) : Metasploit-Framework (`msfvenom` and `msfconsole`)

# Run PhoneSploit Pro :

> __PhoneSploit Pro__ does not need any installation and runs directly using `python3`

#### On Linux / macOS :

Make sure all the [required](https://github.com/AzeemIdrisi/PhoneSploit-Pro#requirements-) softwares are installed.

Open terminal and paste the following commands : 
```
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git

cd PhoneSploit-Pro/

python3 phonesploitpro.py
```
#### On Windows :

Make sure all the [required](https://github.com/AzeemIdrisi/PhoneSploit-Pro#requirements-) softwares are installed.


Open terminal and paste the following commands : 
```
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git

cd PhoneSploit-Pro/
```
1. Download and extract latest `platform-tools` from [here](https://github.com/AzeemIdrisi/PhoneSploit-Pro#adb-on-windows-).

2. Copy all files from the extracted `platform-tools` or `adb` directory to __PhoneSploit-Pro__ directory and then run :

```
python phonesploitpro.py
```


# Install ADB

#### ADB on Linux :

Open terminal and paste the following commands :

__Debian / Ubuntu__
```
sudo apt install adb
```

__Fedora__
```
sudo dnf install adb
```

__Arch Linux / Manjaro__
```
sudo pacman -S adb
```

#### ADB on macOS :

Open terminal and paste the following command :

```
brew install android-platform-tools
```

or Visit this link : [Click Here](https://developer.android.com/studio/releases/platform-tools.html#downloads)

#### ADB on Windows :

Visit this link : [Click Here](https://developer.android.com/studio/releases/platform-tools.html#downloads)


# Install Metasploit-Framework:

#### On Linux / macOS :
```
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && \
  chmod 755 msfinstall && \
  ./msfinstall
 ```
 
or Follow this link : [Click Here](https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html#installing-metasploit-on-linux--macos)

or Visit this link : [Click Here](https://www.metasploit.com/download)

#### On Windows :

Visit this link : [Click Here](https://www.metasploit.com/download)

or Follow this link : [Click Here](https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html#windows-anti-virus-software-flags-the-contents-of-these-packages)

# Tutorial


## Setting up Android Phone for the first time

* __Enabling the Developer Options__

1. Open `Settings`.
2. Go to `About Phone`.
3. Find `Build Number`.
4. Tap on `Build Number` 7 times.
5. Enter your pattern, PIN or password to enable the `Developer options` menu.
6. The `Developer options` menu will now appear in your Settings menu.

* __Enabling USB Debugging__
1. Open `Settings`.
2. Go to `System` > `Developer options`.
3. Scroll down and Enable `USB debugging`.

* __Connecting with Computer__
1. Connect your Android device and `adb` host computer to a common Wi-Fi network.
2. Connect the device to the host computer with a USB cable.
3. Open terminal in the computer and enter the following command :
```
adb devices
```
4. A pop up will appear in the Android phone when you connect your phone to a new PC for the first time : `Allow USB debugging?`.
5. Click on `Always allow from this computer` check-box and then click `Allow`.
6. Then enter the following command :
```
adb tcpip 5555
```
7. Now you can connect the Android Phone over Wi-Fi.
8. Disconnect the USB cable.
9. Go to `Settings` >  `About Phone` > `Status` > `IP address` and note the phone's `IP Address`.
10. Run __PhoneSploit Pro__ and select `Connect a device` and enter the target's `IP address` to connect wirelessly.



## Connecting the Android phone for the next time

1. Connect your Android device and host computer to a common Wi-Fi network.
2. Run __PhoneSploit Pro__ and select `Connect a device` and enter the target's `IP address` to connect wirelessly.


# Disclaimer

* Neither the project nor its developers promote any kind of illegal activity and are not responsible for any misuse or damage caused by this program.
* This project is for the purpose of penetration testing only.
* Please do not use this tool on other people's devices without their permission.
* Do not use this tool to harm others.
* Use this project responsibly on your own devices only.
* It is the end user's responsibility to obey all applicable local, state, federal, and international laws.
