from modules.config import AppConfig
from modules import banner
from modules.console import console, print_success, adb


def use_keycode(config: AppConfig) -> None:
    import os
    os.system(config.clear_cmd)
    console.print(banner.keycode_menu)

    while True:
        console.print(f"\n [cyan]99 : Clear Screen                0 : Main Menu[/cyan]")
        option = console.input(
            "[red]\\[KEYCODE][/red] [white]Enter selection > [/white]"
        ).lower()

        match option:
            case "0":
                return
            case "99":
                os.system(config.clear_cmd)
                console.print(banner.keycode_menu)
            case "1":
                text = console.input(f"\n[cyan]Enter text > [/cyan]")
                adb(["shell", "input", "text", text])
                print_success(f'Entered: "{text}"')
            case "2":
                adb(["shell", "input", "keyevent", "3"])
                print_success("Pressed Home Button")
            case "3":
                adb(["shell", "input", "keyevent", "4"])
                print_success("Pressed Back Button")
            case "4":
                adb(["shell", "input", "keyevent", "187"])
                print_success("Pressed Recent Apps Button")
            case "5":
                adb(["shell", "input", "keyevent", "26"])
                print_success("Pressed Power Key")
            case "6":
                adb(["shell", "input", "keyevent", "19"])
                print_success("Pressed DPAD Up")
            case "7":
                adb(["shell", "input", "keyevent", "20"])
                print_success("Pressed DPAD Down")
            case "8":
                adb(["shell", "input", "keyevent", "21"])
                print_success("Pressed DPAD Left")
            case "9":
                adb(["shell", "input", "keyevent", "22"])
                print_success("Pressed DPAD Right")
            case "10":
                adb(["shell", "input", "keyevent", "67"])
                print_success("Pressed Delete/Backspace")
            case "11":
                adb(["shell", "input", "keyevent", "66"])
                print_success("Pressed Enter")
            case "12":
                adb(["shell", "input", "keyevent", "24"])
                print_success("Pressed Volume Up")
            case "13":
                adb(["shell", "input", "keyevent", "25"])
                print_success("Pressed Volume Down")
            case "14":
                adb(["shell", "input", "keyevent", "126"])
                print_success("Pressed Media Play")
            case "15":
                adb(["shell", "input", "keyevent", "127"])
                print_success("Pressed Media Pause")
            case "16":
                adb(["shell", "input", "keyevent", "61"])
                print_success("Pressed Tab Key")
            case "17":
                adb(["shell", "input", "keyevent", "111"])
                print_success("Pressed Esc Key")
            case _:
                console.print("\n[red]Invalid selection![/red]\n")
