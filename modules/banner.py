"""
    COPYRIGHT DISCLAIMER

    Script : PhoneSploit Pro - All in One Android Hacking ADB Toolkit

    Copyright (C) 2026  Azeem Idrisi (github.com/AzeemIdrisi)

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
    original developer, [Azeem Idrisi (github.com/AzeemIdrisi)], and copying the code
    is not permitted without permission.

    For any queries, Contact me at : azeemidrisiofficial@gmail.com
"""

version = "v2.0"

menu1 = """
    [white]1. [green]Connect a Device             [white]6. [green]Get Screenshot                       [white]11. [green]Install an APK
    [white]2. [green]List Connected Devices       [white]7. [green]Screen Record                        [white]12. [green]Uninstall an App
    [white]3. [green]Disconnect All Devices       [white]8. [green]Download File/Folder from Device     [white]13. [green]List Installed Apps
    [white]4. [green]Scan Network for Devices     [white]9. [green]Send File/Folder to Device           [white]14. [green]Access Device Shell
    [white]5. [green]Mirror & Control Device     [white]10. [green]Run an App                           [white]15. [green]Hack Device [red](Using Metasploit)[/red]

  [yellow]N: Next Page                                      (Page : 1 / 5)[/yellow]"""

menu2 = """
    [white]16. [green]List All Folders/Files      [white]21. [green]Anonymous Screenshot                [white]26. [green]Play a Video on Device
    [white]17. [green]Send SMS                    [white]22. [green]Anonymous Screen Record             [white]27. [green]Get Device Information
    [white]18. [green]Copy WhatsApp Data          [white]23. [green]Open a Link on Device               [white]28. [green]Get Battery Information
    [white]19. [green]Copy All Screenshots        [white]24. [green]Display a Photo on Device           [white]29. [green]Restart Device
    [white]20. [green]Copy All Camera Photos      [white]25. [green]Play an Audio on Device             [white]30. [green]Advanced Reboot Options

  [yellow]P: Previous Page         N: Next Page            (Page : 2 / 5)[/yellow]"""

menu3 = """
    [white]31. [green]Unlock Device               [white]36. [green]Extract APK from Installed App      [white]41. [green]Record Mic Audio
    [white]32. [green]Lock Device                 [white]37. [green]Stop ADB Server                     [white]42. [green]Listen Device Audio
    [white]33. [green]Dump All SMS                [white]38. [green]Power Off Device                    [white]43. [green]Record Device Audio
    [white]34. [green]Dump All Contacts           [white]39. [green]Use Keycodes (Control Device)       [white]44. [green]TCP Port Forward / Reverse
    [white]35. [green]Dump Call Logs              [white]40. [green]Listen Mic Audio                    [white]45. [green]Force Stop App

  [yellow]P: Previous Page         N: Next Page            (Page : 3 / 5)[/yellow]"""

menu4 = """
    [white]46. [green]Clear App Data                 [white]51. [green]Network Snapshot               [white]56. [green]WiFi Status Dump
    [white]47. [green]Save Logcat Snippet            [white]52. [green]Install Split APKs             [white]57. [green]WLAN IP Info
    [white]48. [green]Grant / Revoke Permission      [white]53. [green]Developer Settings             [white]58. [green]WiFi Radio Toggle
    [white]49. [green]Restart App                    [white]54. [green]Read Locale                    [white]59. [green]Ping Connectivity
    [white]50. [green]Live Logcat Stream             [white]55. [green]Screen Stay-On                 [white]60. [green]Saved WiFi Networks

  [yellow]P: Previous Page         N: Next Page            (Page : 4 / 5)[/yellow]"""

menu5 = """
    [white]61. [green]Root Heuristics                [white]62. [green]Update PhoneSploit-Pro

  [yellow]P: Previous Page                                  (Page : 5 / 5)[/yellow]"""

menu = [menu1, menu2, menu3, menu4, menu5]

instruction = """
This attack will launch Metasploit-Framework    (msfconsole)

Use 'Ctrl + C' to stop at any point

1. Wait until you see:

    [green]meterpreter >      [/green]

2. Then use 'help' command to see all meterpreter commands:

    [green]meterpreter > [yellow]help       [/yellow][/green]

3. To exit meterpreter enter 'exit' or To exit Metasploit enter 'exit -y':

    [green]meterpreter > [yellow]exit       [/yellow][/green]

    [green]msf6 > [yellow]exit -y       [/yellow][/green]

[red]\\[PhoneSploit Pro][/red]   Press 'Enter' to continue attack / '0' to Go Back to Main Menu
    """

banner2 = """
        ░█▀▀█ █──█ █▀▀█ █▀▀▄ █▀▀ ░█▀▀▀█ █▀▀█ █── █▀▀█ ─▀─ ▀▀█▀▀ 　 ░█▀▀█ █▀▀█ █▀▀█
        ░█▄▄█ █▀▀█ █──█ █──█ █▀▀ ─▀▀▀▄▄ █──█ █── █──█ ▀█▀ ──█── 　 ░█▄▄█ █▄▄▀ █──█
        ░█─── ▀──▀ ▀▀▀▀ ▀──▀ ▀▀▀ ░█▄▄▄█ █▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ ──▀── 　 ░█─── ▀─▀▀ ▀▀▀▀


            [red]{version}[/red]            [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner3 = """
        █▀█ █░█ █▀█ █▄░█ █▀▀ █▀ █▀█ █░░ █▀█ █ ▀█▀   █▀█ █▀█ █▀█
        █▀▀ █▀█ █▄█ █░▀█ ██▄ ▄█ █▀▀ █▄▄ █▄█ █ ░█░   █▀▀ █▀▄ █▄█


            [red]{version}[/red]             [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner4 = """
    _________.__                           _________      .__         .__  __    __________
    \\______  \\  |__   ____   ____  ____  /   _____/_____ |  |   ____ |__|/  |_  \\______   \\_______  ____
    |     ___/  |  \\ /  _ \\ /    \\_/ __ \\ \\_____  \\\\____ \\|  |  /  _ \\|  \\   __\\  |     ___/\\_  __ \\/  _ \\
    |    |   |   Y  (  <_> )   |  \\  ___/ /        \\  |_> >  |_(  <_> )  ||  |    |    |     |  | \\(  <_> )
    |____|   |___|  /\\____/|___|  /\\___  >_______  /   __/|____/\\____/|__||__|    |____|     |__|   \\____/
                  \\/            \\/     \\/        \\/ |__|


        [red]{version}[/red]                             [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner5 = """
       ___  __                 ____     __     _ __     ___
      / _ \\/ /  ___  ___  ___ / __/__  / /__  (_) /_   / _ \\_______ 
     / ___/ _ \\/ _ \\/ _ \\/ -_)\\ \\/ _ \\/ / _ \\/ / __/  / ___/ __/ _ \\
    /_/  /_//_/\\___/_//_/\\__/___/ .__/_/\\___/_/\\__/  /_/  /_/  \\___/
                               /_/

        [red]{version}[/red]        [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner6 = """
        ____  __                    _____       __      _ __       ____
       / __ \\/ /_  ____  ____  ___ / ___/____  / /___  (_) /_     / __ \\___________
      / /_/ / __ \\/ __ \\/ __ \\/ _ \\\\__ \\/ __ \\/ / __ \\/ / __/    / /_/ / ___/ __ \\
     / ____/ / / / /_/ / / / /  __/__/ / /_/ / / /_/ / / /_     / ____/ /  / /_/ /
    /_/   /_/ /_/\\____/_/ /_/\\___/____/ .___/_/\\____/_/\\__/    /_/   /_/   \\____/
                                     /_/

           [red]{version}[/red]               [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner10 = """
     ____    __                              ____            ___               __        ____
    /\\  _`\\ /\\ \\                            /\\  _`\\         /\\_ \\           __/\\ \\__    /\\  _`\\
    \\ \\ \\L\\ \\ \\ \\___     ___     ___      __\\ \\,\\L\\_\\  _____\\//\\ \\     ___ /\\_\\ \\ ,_\\   \\ \\ \\L\\ \\_ __   ___
     \\ \\ ,__/\\ \\  _ `\\  / __`\\ /' _ `\\  /'__`\\/_\\__ \\ /\\ '__`\\\\\\ \\ \\   / __`\\/\\ \\ \\ \\/    \\ \\ ,__/\\`'__\\/ __`\\
      \\ \\ \\/  \\ \\ \\ \\ \\/\\ \\L\\ \\/\\ \\/\\ \\/\\  __/ /\\ \\L\\ \\ \\ \\L\\ \\\\_\\ \\_/\\ \\L\\ \\ \\ \\ \\ \\_    \\ \\ \\/\\ \\ \\//\\ \\L\\ \\
       \\ \\_\\   \\ \\_\\ \\_\\ \\____/\\ \\_\\ \\_\\ \\____\\\\ `\\____\\ \\ ,__//\\____\\ \\____/\\ \\_\\ \\__\\    \\ \\_\\ \\ \\_\\\\ \\____/
        \\/_/    \\/_/\\/_/\\/___/  \\/_/\\/_/\\/____/ \\/_____/\\ \\ \\/ \\/____/\\/___/  \\/_/\\/__/     \\/_/  \\/_/ \\/___/
                                                         \\ \\_\\
                                                          \\/_/

            [red]{version}[/red]                                [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner11 = """
    _____________                   ________       ______     __________       ________
    ___  __ \\__  /_____________________  ___/__________  /________(_)_  /_      ___  __ \\____________
    __  /_/ /_  __ \\  __ \\_  __ \\  _ \\____ \\___  __ \\_  /_  __ \\_  /_  __/      __  /_/ /_  ___/  __ \\
    _  ____/_  / / / /_/ /  / / /  __/___/ /__  /_/ /  / / /_/ /  / / /_        _  ____/_  /   / /_/ /
    /_/     /_/ /_/\\____//_/ /_/\\___//____/ _  .___//_/  \\____//_/  \\__/        /_/     /_/    \\____/
                                            /_/


            [red]{version}[/red]                            [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner12 = """
        ▒█▀▀█ █░░█ █▀▀█ █▀▀▄ █▀▀ ▒█▀▀▀█ █▀▀█ █░░ █▀▀█ ░▀░ ▀▀█▀▀ 　 ▒█▀▀█ █▀▀█ █▀▀█
        ▒█▄▄█ █▀▀█ █░░█ █░░█ █▀▀ ░▀▀▀▄▄ █░░█ █░░ █░░█ ▀█▀ ░░█░░ 　 ▒█▄▄█ █▄▄▀ █░░█
        ▒█░░░ ▀░░▀ ▀▀▀▀ ▀░░▀ ▀▀▀ ▒█▄▄▄█ █▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ ░░▀░░ 　 ▒█░░░ ▀░▀▀ ▀▀▀▀


            [red]{version}[/red]                            [white]By github.com/AzeemIdrisi[/white]
""".format(version=version)

banner_list = [
    banner2,
    banner3,
    banner4,
    banner5,
    banner6,
    banner10,
    banner11,
    banner12,
]

instructions_banner = """[cyan]
        ____           __                  __  _
       /  _/___  _____/ /________  _______/ /(_)___  ____  _____
       / // __ \\/ ___/ __/ ___/ / / / ___/ __/ / __ \\/ __ \\/ ___/
     _/ // / / (__  ) /_/ /  / /_/ / /__/ /_/ / /_/ / / / (__  )
    /___/_/ /_/____/\\__/_/   \\__,_/\\___/\\__/_/\\____/_/ /_/____/
[/cyan]"""

hacking_banner = """[green]
    █░█ ▄▀█ █▀▀ █▄▀ █ █▄░█ █▀▀ ░ ░ ░
    █▀█ █▀█ █▄▄ █░█ █ █░▀█ █▄█ ▄ ▄ ▄
[/green]"""

keycode_menu = """
    [white]1. [green]Keyboard Text Input                [white]11. [green]Enter
    [white]2. [green]Home                               [white]12. [green]Volume Up
    [white]3. [green]Back                               [white]13. [green]Volume Down
    [white]4. [green]Recent Apps                        [white]14. [green]Media Play
    [white]5. [green]Power Button                       [white]15. [green]Media Pause
    [white]6. [green]DPAD Up                            [white]16. [green]Tab
    [white]7. [green]DPAD Down                          [white]17. [green]Esc
    [white]8. [green]DPAD Left
    [white]9. [green]DPAD Right
   [white]10. [green]Delete/Backspace[/green]
"""
