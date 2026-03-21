from modules.config import AppConfig
from modules import banner
from modules.console import console, print_success, adb


def use_keycode(config: AppConfig) -> None:
    import os
    os.system(config.clear_cmd)
    console.print(banner.keycode_menu)

    while True:
        console.print("[dim]99[/dim] Clear   [dim]0[/dim] Menu")
        option = console.input(
            "[red]\\[KEYCODE][/red] [white]>[/white] "
        ).lower()

        match option:
            case "0":
                return
            case "99":
                os.system(config.clear_cmd)
                console.print(banner.keycode_menu)
            case "1":
                text = console.input("[cyan]Text[/cyan]> ")
                adb(["shell", "input", "text", text])
                print_success(f'Entered: "{text}"')
            case "2":
                adb(["shell", "input", "keyevent", "3"])
                print_success("Home")
            case "3":
                adb(["shell", "input", "keyevent", "4"])
                print_success("Back")
            case "4":
                adb(["shell", "input", "keyevent", "187"])
                print_success("Recent apps")
            case "5":
                adb(["shell", "input", "keyevent", "26"])
                print_success("Power")
            case "6":
                adb(["shell", "input", "keyevent", "19"])
                print_success("DPAD up")
            case "7":
                adb(["shell", "input", "keyevent", "20"])
                print_success("DPAD down")
            case "8":
                adb(["shell", "input", "keyevent", "21"])
                print_success("DPAD left")
            case "9":
                adb(["shell", "input", "keyevent", "22"])
                print_success("DPAD right")
            case "10":
                adb(["shell", "input", "keyevent", "67"])
                print_success("Delete")
            case "11":
                adb(["shell", "input", "keyevent", "66"])
                print_success("Enter")
            case "12":
                adb(["shell", "input", "keyevent", "24"])
                print_success("Volume up")
            case "13":
                adb(["shell", "input", "keyevent", "25"])
                print_success("Volume down")
            case "14":
                adb(["shell", "input", "keyevent", "126"])
                print_success("Media play")
            case "15":
                adb(["shell", "input", "keyevent", "127"])
                print_success("Media pause")
            case "16":
                adb(["shell", "input", "keyevent", "61"])
                print_success("Tab")
            case "17":
                adb(["shell", "input", "keyevent", "111"])
                print_success("Esc")
            case _:
                console.print("[red]Invalid[/red]")
