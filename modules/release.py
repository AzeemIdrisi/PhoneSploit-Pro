from modules import color
from modules import banner
import os
import platform


def exit_phonesploit_pro():
    global run_phonesploit_pro
    run_phonesploit_pro = False
    print("\nExiting...\n")


def display_menu():
    """Displays banner and menu"""
    print(selected_banner, page)


def clear_screen():
    """Clears the screen and display menu"""
    os.system(clear)
    display_menu()


def start():
    operating_system = platform.system()
    if operating_system == "Windows":
        # Windows specific configuration
        windows_config()


def windows_config():
    global clear
    clear = "cls"


def change_page(name):
    global page, page_number, selected_banner
    if name == "p":
        if page_number > 0:
            page_number = page_number - 1
    elif name == "n":
        if page_number < 2:
            page_number = page_number + 1
    if page_number == 0:
        selected_banner = color.RED + banner.banner6
    elif page_number == 1:
        selected_banner = color.CYAN + banner.banner11
    elif page_number == 2:
        selected_banner = color.YELLOW + banner.banner2
    page = banner.menu[page_number]
    clear_screen()


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
        case "0":
            exit_phonesploit_pro()
        case "99":
            clear_screen()


clear = "clear"
page_number = 0
page = banner.menu[page_number]

# Concatenating banner color with the selected banner
selected_banner = color.RED + banner.banner6

start()
run_phonesploit_pro = True
if run_phonesploit_pro:
    clear_screen()
    while run_phonesploit_pro:
        try:
            main()
        except KeyboardInterrupt:
            exit_phonesploit_pro()
