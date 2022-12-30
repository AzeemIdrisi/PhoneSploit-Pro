import os
import random
from banner import banner_list


def display_menu():
    ''' Displays a random banner and menu'''
    print(random.choice(banner_list))  # Prints a random banner
    menu = '''

    1. Connect a device             5. Get screenshot               10. Install an APK
    2. List connected devices       6. Stop ADB server              11. Run an app
    3. Disconnect all devices       7. Access device shell          12. Uninstall an app
    4. List installed apps          8. Download file from device
                                    9. Send file to device


    99 : Clear Screen                0 : Exit
    
    '''
    print(menu)


def clear_screen():
    ''' Clears the screen and display menu '''
    os.system("clear")
    display_menu()


def connect():
    print("\n")
    os.system("adb tcpip 5555")
    print("Enter target phone's IP Address.       Example : 192.168.1.23")
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


def get_shell():
    print("\n")
    os.system("adb shell")


def get_screenshot():
    print("Saving screenshot to PhoneSploit-Pro directory...\n")
    os.system("adb shell screencap -p /sdcard/screen.png")
    os.system("adb pull /sdcard/screen.png")
    print("\n")


def stop_adb():
    os.system("adb kill-server")
    print("Stopped ADB Server")


def pull_file():
    print("\n")
    location = input("Enter file path : /sdcard/")
    destination = input("Enter destination path : ")
    os.system("adb pull /sdcard/" + location + " " + destination)


def push_file():
    print("\n")
    location = input("Enter file path : ")
    destination = input("Enter destination path : /sdcard/")
    os.system("adb push " + location + " /sdcard/" + destination)


def install_app():
    print("\n")
    file_location = input("Enter apk path : ")
    os.system("adb install " + file_location)
    print("\n")


def uninstall_app():
    print("\nEnter package name.     Example : com.spotify.music ")
    package_name = input("> ")
    os.system("adb uninstall " + package_name)
    print("\n")


def launch_app():

    print("\nEnter package name.     Example : com.spotify.music ")
    package = input("> ")

    os.system("adb shell monkey -p " + package + " 1")
    print("\n")


def list_apps():
    print('''

    1 - List third party packages
    2 - List all packages
    ''')
    mode = int(input("> "))
    if mode == 1:
        os.system("adb shell pm list packages -3")
    elif mode == 2:
        os.system("adb shell pm list packages")
    print("\n")


def main():

    # Clearing the screen and presenting the menu
    # taking selction input from user
    option = int(input("Enter selection > "))

    match option:
        case 0:
            exit_phonesploit_pro()
        case 99:
            clear_screen()
        case 1:
            connect()
        case 2:
            list_devices()
        case 3:
            disconnect()
        case 4:
            list_apps()
        case 5:
            get_screenshot()
        case 6:
            stop_adb()
        case 7:
            get_shell()
        case 8:
            pull_file()
        case 9:
            push_file()
        case 10:
            install_app()
        case 11:
            launch_app()
        case 12:
            uninstall_app()
        case other:
            print("Invalid selection!\n")


# Starting point of the program
run_phonesploit_pro = True
clear_screen()
while run_phonesploit_pro:
    main()
