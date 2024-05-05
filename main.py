from scripts import colors, config, common
from os import path, system
from platform import system
import pandas as pd

# Since we use the win32 API in config.py this script will not work on any other OS for now
if system() != 'Windows':
    print(f"\n{colors.RED} PLATFORM IS NOT WINDOWS. EXITING.")
    exit(1)

# Just a quick function to clear the console
cls = lambda: print("\033c", end='')

# Load script the config
conf = config.Configuration()

# Get the games config file
game_config = open(f'{conf.get('game_path')}\\config.blk', 'r+').readlines()

# Update the games config file if neccessary
if game_config and not '  testLocalization:b=yes\n' in game_config:
    print(f"{colors.YELLOW}FOUND GAME CONFIG BUT NO LOCALIZATION ACTIVE. CREATING BACKUP FILE {colors.CYAN}'config.blk.backup'{colors.END}")
    with open(f'{conf.get('game_path')}\\config.blk.backup', 'w+') as backup:
        backup.writelines(game_config)
        print(f"{colors.YELLOW}BACKUP CREATED! UPDATING ORIGINAL...{colors.END}")
    debug_index = game_config.index('debug{\n')
    if debug_index:
        game_config.insert(debug_index+1, '  testLocalization:b=yes\n')
        with open(f'{conf.get('game_path')}\\config.blk', 'w') as config_file:
            config_file.writelines(game_config)
        print(f"\n{colors.GREEN}CONFIG UPDATED! RUN THE GAME ONCE TO GENERATE BASE TRANSLATION FILES!{colors.END}")
        exit(0)

# If there is no lang folder, warn the user and quit
elif game_config and '  testLocalization:b=yes\n' in game_config and not path.exists(f'{conf.get('game_path')}\\lang'):
    print(f"\n{colors.RED} FOUND {colors.CYAN}'testLocalization'{colors.RED} KEY IN CONFIG BUT NO {colors.CYAN}'lang'{colors.RED} FOLDER! DID YOU RUN THE GAME ONCE?{colors.END}")
    exit(404)

def _choice(title, options, question, default: int = None, allow_none: bool = False):
    ret = None
    cls()
    print("-"*30)
    print(f"{colors.BLUE}{title}{colors.END}")
    print("-"*30)
    i = 1
    for option in options:
        print(f"{colors.BLUE}{i}: {colors.CYAN}{option}{colors.END}")
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
    language = languages[_choice("Choose a language to edit", languages, "Pick a language", 1)]
    changes = {}

    while True:
        cls()
        options = list(map(lambda x: f'{csv.loc[x, language]}{f"{colors.END} => {colors.RED}{changes[x]}{colors.CYAN}" if x in changes.keys() else ""}', common.COMMON_IDS))
        string_to_edit = _choice(f"{colors.BLUE}Editing {colors.CYAN}{language}{colors.BLUE} strings!\nPick one of the pre-chosen strings to edit (Search feature coming soon)\nJust press {colors.CYAN}[Enter]{colors.BLUE} without any input to save changes and exit.{colors.END}", options, 'String to edit', allow_none=True)
        
        if string_to_edit is not None:
            cls()
            print("-"*30)
            print(f"{colors.BLUE}Enter replacement string for {colors.CYAN}{csv.loc[common.COMMON_IDS[string_to_edit], language]}{colors.BLUE}\nAlternatively, hit {colors.CYAN}[Enter]{colors.BLUE} without any input to cancel.{colors.END}")
            print("-"*30)
            while True:
                new_text = input('New text: ')
                if new_text is not "":
                    changes[common.COMMON_IDS[string_to_edit]] = new_text
                break;
        else:
            cls()
            if len(changes.keys()) > 0:
                print("-"*30)
                print(f"{colors.CYAN}{len(changes.keys())}{colors.BLUE} changes were made. Applying...{colors.END}")
                print("-"*30)
                for change in changes.keys():
                    print(f"{colors.CYAN}{csv.loc[change, language]}{colors.END} => {colors.RED}{changes[change]}{colors.END}")
                    csv.loc[change, language] = changes[change]
                csv.to_csv(open(f'{conf.get('game_path')}\\lang\\menu.csv', 'w', encoding="utf8"), encoding="utf8", sep=';')
                print("-"*30)
                print(f"{colors.BLUE} All changes applied. Exiting.{colors.END}")
                print("-"*30)
                exit(0)
            else:
                print("-"*30)
                print(f"{colors.BLUE}No changes were made. Exiting.{colors.END}")
                print("-"*30)
                exit(0)

if __name__ == "__main__":
    main()