# PhoneSploit Pro
#### PhoneSploit with Metasploit integration.

A hacking script written in Python3 to remotely exploit Android devices using ADB.

This script can automatically __Create__, __Install__, and __Run__ payload to the target device using __Metasploit-Framework__ and __ADB__ to completely hack the Android Device in one-click.

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
* __Hack Device Completely__ : Automatically create a payload using __msfvenom__, install it, and run it in target device, then automatically launch and setup __Metasploit-Framework__ to get a __meterpreter__ session.

Getting a meterpreter session means the device is completely hacked using Metasploit-Framework and you can do anything with it.

# Requirements : 
* Git
* Python 3.10 or newer
* Android-Tools (ADB)
* Metasploit-Framework

# Installation :
#### On Linux / macOS :

Open terminal and paste the following commands : 
```
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git

cd PhoneSploit-Pro/

python3 phonesploitpro.py
```
#### On Windows :

Open terminal and paste the following commands : 
```
git clone https://github.com/AzeemIdrisi/PhoneSploit-Pro.git

cd PhoneSploit-Pro/
```

Copy all files from your ADB directory to PhoneSploit-Pro directory and then run :

```
python3 phonesploitpro.py
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

or Visit : https://developer.android.com/studio/releases/platform-tools.html#downloads

#### ADB on Windows :

Visit : https://developer.android.com/studio/releases/platform-tools.html#downloads


# Install Metasploit-Framework:
__Linux or macOS__ :
```
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && \
  chmod 755 msfinstall && \
  ./msfinstall
 ```
 
or Follow this link : https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html#installing-metasploit-on-linux--macos

or Visit : https://www.metasploit.com/download

__Windows__ :

Visit : https://www.metasploit.com/download

or Follow : https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html#windows-anti-virus-software-flags-the-contents-of-these-packages
