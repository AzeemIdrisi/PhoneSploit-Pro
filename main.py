import os
import random
from banner import banner_list


def display_menu():
    ''' Displays a random banner and menu'''
    print(random.choice(banner_list))  # Prints a random banner
    menu = '''

    1. Connect a device             6. Get screenshot                11. Run an app
    2. List connected devices       7. List installed apps           12. Uninstall an app   
    3. Disconnect all devices       8. Download file from device     13. Screen Record     
    4. Access device shell          9. Send file to device           14. Restart device
    5. Stop ADB server             10. Install an APK                 
    
    '''
    print(menu)


def clear_screen():
    ''' Clears the screen and display menu '''
    os.system("clear")
    display_menu()


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
    os.system("adb shell screencap -p /sdcard/screen.png")
    print("\nEnter location to save screenshot, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        print("\nSaving screenshot to PhoneSploit-Pro directory...\n")
    os.system(f"adb pull /sdcard/screen.png {destination}")
    print("\n")


def stop_adb():
    os.system("adb kill-server")
    print("\nStopped ADB Server")


def pull_file():
    location = input("\nEnter file path : /sdcard/")
    print("\nEnter location to save file, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        print("\nSaving file to PhoneSploit-Pro directory...\n")
    os.system("adb pull /sdcard/" + location + " " + destination)


def push_file():
    location = input("\nEnter file path : ")
    destination = input("Enter destination path : /sdcard/")
    os.system("adb push " + location + " /sdcard/" + destination)


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

    1 - List third party packages
    2 - List all packages
    ''')
    mode = int(input("> "))
    if mode == 1:
        os.system("adb shell pm list packages -3")
    elif mode == 2:
        os.system("adb shell pm list packages")
    print("\n")


def screenrecord():
    time = input("\nEnter the recording duration (in seconds) > ")
    os.system(
        f"adb shell screenrecord --verbose --time-limit {time} /sdcard/demo.mp4")
    print("\nEnter location to save video, Press 'Enter' for default")
    destination = input("> ")
    if destination == "":
        print("\nSaving video to PhoneSploit-Pro directory...\n")
    os.system(f"adb pull /sdcard/demo.mp4 {destination}")
    print("\n")


def reboot():
    os.system('adb reboot')
    print('\n')


def main():

    # Clearing the screen and presenting the menu
    # taking selction input from user
    print("\n 99 : Clear Screen                0 : Exit")
    option = int(input("\n[Main Menu] Enter selection > "))

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
            get_shell()
        case 5:
            stop_adb()
        case 6:
            get_screenshot()
        case 7:
            list_apps()
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
        case 13:
            screenrecord()
        case 14:
            reboot()
        case other:
            print("\nInvalid selection!\n")


# Starting point of the program
run_phonesploit_pro = True
clear_screen()
while run_phonesploit_pro:
    main()
