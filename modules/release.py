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
"""
Copyright © 2023 Mohd Azeem (github.com/AzeemIdrisi)
"""
