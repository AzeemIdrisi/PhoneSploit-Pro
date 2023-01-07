# PhoneSploit Pro
### PhoneSploit with Metasploit integration.
[![CodeFactor](https://www.codefactor.io/repository/github/azeemidrisi/phonesploit-pro/badge)](https://www.codefactor.io/repository/github/azeemidrisi/phonesploit-pro)

A hacking tool written in `Python` to remotely exploit Android devices using `ADB` (Android Debugging Bridge).


> Complete Automation to get a `meterpreter` session in One Click

This tool can automatically __Create__, __Install__, and __Run__ payload on the target device using __Metasploit-Framework__ and __ADB__ to completely hack the Android Device in one click.

The goal of this project is to make penetration testing on Android devices easy. Now you don't have to learn commands and arguments, PhoneSploit Pro does it for you. Using this tool, you can test the security of your Android devices easily.


# Features 
* Connect device using ADB remotely.
* List connected devices.
* Disconnect all devices.
* Access connected device shell.
* Stop ADB Server.
* Take screenshot and pull it to computer automatically.
* Screen Record target device screen for a specified time and automatically pull it to computer.
* Download file/folder from target device.
* Send file/folder from computer to target device.
* Run an app.
* Install an APK file from computer to target device.
* Uninstall an app.
* List all installed apps in target device.
* Restart/Reboot the target device to `System`, `Recovery`, `Bootloader`, `Fastboot`.
* __Hack Device Completely__ : 
  - Automatically fetch `IP Address` to create payload.
  - Automatically create a payload using `msfvenom`, install it, and run it on target device.
  - Then automatically launch and setup __Metasploit-Framework__ to get a `meterpreter` session.
  - Getting a `meterpreter` session means the device is completely hacked using Metasploit-Framework, and you can do anything with it.

* List all files and folders of the target devices.
* Copy all WhatsApp Data to computer.
* Copy all Screenshots to computer.
* Copy all Camera Photos to computer.
* Take screenshots and screen-record anonymously (Automatically delete file from target device).
* Open a link on target device.
* Display an image/photo on target device.
* Play an audio on target device.
* Play a video on target device.

# Requirements  
* [`git`](https://git-scm.com/) : Git
* [`python3`](https://www.python.org/) : Python 3.10 or Newer
* [`adb`](https://developer.android.com/studio/command-line/adb) : Android Debugging Bridge (ADB) from `Android SDK Platform Tools`
* [`metasploit-framework`](https://www.metasploit.com/) : Metasploit-Framework (`msfvenom` and `msfconsole`)

# Run PhoneSploit Pro 

__PhoneSploit Pro__ does not need any installation and runs directly using `python3`

#### On Linux / macOS :

Make sure all the [required](https://github.com/AzeemIdrisi/PhoneSploit-Pro#requirements) softwares are installed.

Open terminal and paste the following commands : 
```
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git

cd PhoneSploit-Pro/

python3 phonesploitpro.py
```
#### On Windows :

Make sure all the [required](https://github.com/AzeemIdrisi/PhoneSploit-Pro#requirements) softwares are installed.


Open terminal and paste the following commands : 
```
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git

cd PhoneSploit-Pro/
```
1. Download and extract latest `platform-tools` from [here](https://developer.android.com/studio/releases/platform-tools.html#downloads).

2. Copy all files from the extracted `platform-tools` or `adb` directory to __PhoneSploit-Pro__ directory and then run :

```
python phonesploitpro.py
```


# Screenshots

![Screenshot from 2023-01-07 16-59-58](https://user-images.githubusercontent.com/112647789/211148389-3473b716-1639-48e8-9355-7407e1a227f7.png)
![Screenshot from 2023-01-07 16-43-50](https://user-images.githubusercontent.com/112647789/211148491-f60e3eae-dcb6-40fc-8527-ae8774767dc9.png)



# Installing ADB 

#### ADB on Linux :

Open terminal and paste the following commands :

* __Debian / Ubuntu__
```
sudo apt install adb
```

* __Fedora__
```
sudo dnf install adb
```

* __Arch Linux / Manjaro__
```
sudo pacman -Sy android-tools
```

#### ADB on macOS :

Open terminal and paste the following command :

```
brew install android-platform-tools
```

or Visit this link : [Click Here](https://developer.android.com/studio/releases/platform-tools.html#downloads)

#### ADB on Windows :

Visit this link : [Click Here](https://developer.android.com/studio/releases/platform-tools.html#downloads)


# Installing Metasploit-Framework 

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
10. Run __PhoneSploit Pro__ and select `Connect a device` and enter the target's `IP Address` to connect wirelessly.



## Connecting the Android phone for the next time

1. Connect your Android device and host computer to a common Wi-Fi network.
2. Run __PhoneSploit Pro__ and select `Connect a device` and enter the target's `IP Address` to connect wirelessly.


# This tool is tested on

- [x] Ubuntu
- [x] Linux Mint
- [ ] Kali Linux
- [x] Fedora
- [x] Arch Linux
- [x] Parrot Security OS
- [x] Windows 11
- [ ] macOS

**Linux** is recommended for running PhoneSploit Pro, thus all new features are primarily tested on this platform.
Some features might not work properly on Windows.


# Disclaimer

* Neither the project nor its developers promote any kind of illegal activity and are not responsible for any misuse or damage caused by this project.
* This project is for the purpose of penetration testing only.
* Please do not use this tool on other people's devices without their permission.
* Do not use this tool to harm others.
* Use this project responsibly on your own devices only.
* It is the end user's responsibility to obey all applicable local, state, federal, and international laws.


# Developer

<a href="https://github.com/azeemidrisi/">
  <img src="https://contrib.rocks/image?repo=azeemidrisi/phonesploit-pro" />
</a>


**Mohd Azeem** - [@AzeemIdrisi](https://github.com/azeemidrisi/)
 
