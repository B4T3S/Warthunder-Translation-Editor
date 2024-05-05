from scripts import colors, config
from os import path
from platform import system
import pandas as pd

# Since we use the win32 API in config.py this script will not work on any other OS for now
if system() != 'Windows':
    print(f"\n{colors.RED} PLATFORM IS NOT WINDOWS. EXITING.")
    exit(1)

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

def main():
    csv = pd.read_csv(open(f'{conf.get('game_path')}\\lang\\menu.csv', 'r', encoding="utf8"), sep=';', index_col=[0])
    print(csv.columns)
    languages = csv.columns[:-2]
    print(languages)
    print(csv.loc['exp_reasons/assist', '<German>'])

if __name__ == "__main__":
    main()