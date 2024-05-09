# This is a simple helper class to manage the configuration of this script
import win32api
import inquirer as inq
from os import listdir, mkdir, path, getenv
from yaml import safe_load, safe_dump
from scripts import console

class Configuration:
    folder_path = f"{getenv('LOCALAPPDATA')}\\War Thunder translation editor"
    file_path = f"{folder_path}/config.yml"
    if not path.exists(folder_path):
        mkdir(folder_path)
    version = 1  # Version of the config file.
    config = {}

    def __init__(self):
        if not path.exists(self.file_path):
            open(self.file_path, 'w+').close()
        with open(self.file_path, 'r') as data:
            self.config = safe_load(data)
        self._validate()
    
    def _validate(self):
        if self.config is None:  # Gotta make sure the safe_load didn't load *nothing*
            self.config = {}

        if not 'version' in self.config.keys():
            self.set('version', self.version)

        if not 'display_colors' in self.config.keys():
            self._check_colors()
        elif self.get('display_colors') is False:
            console.disable_colors()

        if not 'game_path' in self.config.keys() or not path.exists(f'{self.get('game_path')}\\config.blk'):
            self._find_game()

    def _check_colors(self):
        print(f"\n{console.Colors.RED}◼{console.Colors.END}\n")
        enable = inq.prompt([inq.Confirm('enable', message="Does this look like a red square?")])['enable']
        self.set('display_colors', enable)
        if not enable:
            console.disable_colors()

    def _find_game(self):
        console.pretty_print("<'game_path'> not set! Trying to locate warthunder...", console.Colors.YELLOW)
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        
        for drive in drives:
            letter = drive[0]
            if letter == 'C':
                if path.exists("C:\\Program Files (x86)\\Steam\\steamapps\\common\\War Thunder\\config.blk"):
                    console.pretty_print(f"Found the game on drive <{letter}>", console.Colors.GREEN)
                    self.set('game_path', "C:\\Program Files (x86)\\Steam\\steamapps\\common\\War Thunder")
                    return
                if path.exists("C:\\Program Files\\Steam\\steamapps\\common\\War Thunder\\config.blk"):
                    console.pretty_print(f"Found the game on drive <{letter}>", console.Colors.GREEN)
                    self.set('game_path', "C:\\Program Files\\Steam\\steamapps\\common\\War Thunder")
                    return
            
            if path.exists(f"{letter}:\\SteamLibrary\\steamapps\\common\\War Thunder\\config.blk"):
                console.pretty_print(f"Found the game on drive <{letter}>", console.Colors.GREEN)
                self.set('game_path', f"{letter}:\\SteamLibrary\\steamapps\\common\\War Thunder")
                return
        
        console.pretty_print(f"Couldn't find the game! Enter the path manually...", console.Colors.RED)
        while True:
            _path = inq.prompt([inq.Path('path', path_type=inq.Path.DIRECTORY)])['path']
            if path.exists(f"{_path}\\config.blk"):
                print(f"{console.Colors.GREEN}Path successfully set!{console.Colors.END}")
                self.set('game_path', _path)
                break;
            else:
                print("Game not found in that path!")

    def set(self, key, value):
        self.config[key] = value
        with open(self.file_path, 'w') as ds:
            safe_dump(self.config, ds)

    def get(self, key):
        if key in self.config.keys():
            return self.config[key]
        else:
            return None