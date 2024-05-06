import pandas as pd
import inquirer as inq
from scripts import console, config, common
from os import path, system
from platform import system

# Since we use the win32 API in config.py this script will not work on any other OS for now
if system() != 'Windows':
    print(f"\n{console.Colors.RED} PLATFORM IS NOT WINDOWS. EXITING.")
    die(1)

def die(code: int = 0):
    print("Press enter to exit...")
    input()
    exit(code)

# Load the script config
conf = config.Configuration()

# Get the games config file
game_config = open(f'{conf.get('game_path')}\\config.blk', 'r+').readlines()

# Update the games config file if neccessary
if game_config and not '  testLocalization:b=yes\n' in game_config:
    console.pretty_print("FOUND GAME CONFIG BUT NO LOCALIZATION ACTIVE. CREATING BACKUP FILE <'config.blk.backup'>", console.Colors.YELLOW)
    with open(f'{conf.get('game_path')}\\config.blk.backup', 'w+') as backup:
        backup.writelines(game_config)
        console.pretty_print("BACKUP CREATED! UPDATING ORIGINAL...", console.Colors.YELLOW)
    debug_index = game_config.index('debug{\n')
    if debug_index:
        game_config.insert(debug_index+1, '  testLocalization:b=yes\n')
        with open(f'{conf.get('game_path')}\\config.blk', 'w') as config_file:
            config_file.writelines(game_config)
        console.pretty_print("CONFIG UPDATED! RUN THE GAME ONCE TO GENERATE BASE TRANSLATION FILES!", console.Colors.GREEN)
        input("Press enter to quit...")
        exit(0)

# If there is no lang folder, warn the user and quit
elif game_config and '  testLocalization:b=yes\n' in game_config and not path.exists(f'{conf.get('game_path')}\\lang'):
    console.pretty_print("FOUND <'testLocalization'> KEY IN CONFIG BUT NO <'lang'> FOLDER! DID YOU RUN THE GAME ONCE?", console.Colors.RED)
    die(404)

def _choice(title, options, question, default: int = None, allow_none: bool = False):
    ret = None
    console.cls()
    console.title(title)
    i = 1
    for option in options:
        console.pretty_print(f"{i}: <{option}>")
        i += 1
    print("-"*30)
    while True:
        choice = input(f"{question} (1-{len(options)}){f' [{default}]' if default else ''}: ")
        try:
            if choice == "":
                if default is not None:
                    ret = default-1
                    break
                elif allow_none:
                    ret = None
                    break
                else:
                    continue
            choice = int(choice)-1
            if choice < 0 or choice >= len(options):
                continue
            ret = choice
            break
        except:
            pass
    return ret

def main():
    csv = pd.read_csv(open(f'{conf.get('game_path')}\\lang\\menu.csv', 'r', encoding="utf8"), sep=';', index_col=[0])
    languages = csv.columns[:-2]
    language = inq.prompt([inq.List('lang', message="Choose a language to edit", choices=list(languages), carousel=True)])['lang']
    changes = {}

    while True:
        console.cls()
        options = list(map(lambda x: f'{csv.loc[x, language]}{f"{console.Colors.END} => {console.Colors.RED}{changes[x]}{console.Colors.CYAN}" if x in changes.keys() else ""}', common.COMMON_IDS))
        string_to_edit = _choice(f"{console.Colors.BLUE}Editing {console.Colors.CYAN}{language}{console.Colors.BLUE} strings!\nPick one of the pre-chosen strings to edit (Search feature coming soon)\nJust press {console.Colors.CYAN}[Enter]{console.Colors.BLUE} without any input to save changes and exit.{console.Colors.END}", options, 'String to edit', allow_none=True)
        
        if string_to_edit is not None:
            console.cls()
            print("-"*30)
            print(f"{console.Colors.BLUE}Enter replacement string for {console.Colors.CYAN}{csv.loc[common.COMMON_IDS[string_to_edit], language]}{console.Colors.BLUE}\nAlternatively, hit {console.Colors.CYAN}[Enter]{console.Colors.BLUE} without any input to cancel.{console.Colors.END}")
            print("-"*30)
            while True:
                new_text = input('New text: ')
                if new_text != "":
                    changes[common.COMMON_IDS[string_to_edit]] = new_text
                break;
        else:
            console.cls()
            if len(changes.keys()) > 0:
                print("-"*30)
                print(f"{console.Colors.CYAN}{len(changes.keys())}{console.Colors.BLUE} changes were made. Applying...{console.Colors.END}")
                print("-"*30)
                for change in changes.keys():
                    print(f"{console.Colors.CYAN}{csv.loc[change, language]}{console.Colors.END} => {console.Colors.RED}{changes[change]}{console.Colors.END}")
                    csv.loc[change, language] = changes[change]
                csv.to_csv(open(f'{conf.get('game_path')}\\lang\\menu.csv', 'w', encoding="utf8"), encoding="utf8", sep=';')
                print("-"*30)
                print(f"{console.Colors.BLUE} All changes applied. Exiting.{console.Colors.END}")
                print("-"*30)
                print()
                die(0)
            else:
                print("-"*30)
                print(f"{console.Colors.BLUE}No changes were made. Exiting.{console.Colors.END}")
                print("-"*30)
                print()
                die(0)

if __name__ == "__main__":
    main()