import os
import random
from banner import banner_list


def display_menu():
    print(random.choice(banner_list))  # Prints a random banner everytime
    ''' Displays a random banner and menu'''
    menu = '''

    1. Connect a device
    2. List connected devices
    3. Disconnect all devices
    4. Clear Screen
    0. Exit
    
    '''
    print(menu)


def clear_screen():
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


def main():

    # Clearing the screen and presenting the menu
    # taking selction input from user
    option = int(input("Enter selection : "))

    match option:
        case 0:
            exit_phonesploit_pro()
        case 1:
            connect()
        case 2:
            list_devices()
        case 3:
            disconnect()
        case 4:
            clear_screen()
        case other:
            print("Invalid selection!\n")


# Starting point of the program
run_phonesploit_pro = True
clear_screen()
while run_phonesploit_pro:
    main()
