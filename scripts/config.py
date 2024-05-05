# This is a simple helper class to manage the configuration of this script
import win32api
from os import listdir, path
from yaml import safe_load, safe_dump
from scripts import colors

class Configuration:
    version = 1  # Version of the config file.
    config = {}

    def __init__(self):
        files = listdir()
        if not 'config.yml' in files:
            open('./config.yml', 'w+').close()
        with open('./config.yml', 'r') as data:
            self.config = safe_load(data)
        self._validate()
    
    def _validate(self):
        if self.config is None:  # Gotta make sure the safe_load didn't load *nothing*
            self.config = {}

        if not 'version' in self.config.keys():
            self.set('version', self.version)

        if not 'game_path' in self.config.keys():
            self._find_game()

    def _find_game(self):
        print(f"{colors.CYAN}'game_path'{colors.YELLOW} not set! Trying to locate warthunder...{colors.END}")
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        
        for drive in drives:
            letter = drive[0]
            if letter == 'C':
                if path.exists("C:\\Program Files (x86)\\Steam\\steamapps\\common\\War Thunder\\config.blk"):
                    print(f"{colors.GREEN}Found game on drive {colors.CYAN}{letter}{colors.END}")
                    self.set('game_path', "C:\\Program Files (x86)\\Steam\\steamapps\\common\\War Thunder")
                    return
                if path.exists("C:\\Program Files\\Steam\\steamapps\\common\\War Thunder\\config.blk"):
                    print(f"{colors.GREEN}Found game on drive {colors.CYAN}{letter}{colors.END}")
                    self.set('game_path', "C:\\Program Files\\Steam\\steamapps\\common\\War Thunder")
                    return
            
            if path.exists(f"{letter}:\\SteamLibrary\\steamapps\\common\\War Thunder\\config.blk"):
                print(f"{colors.GREEN}Found game on drive {colors.CYAN}{letter}{colors.END}")
                self.set('game_path', f"{letter}:\\SteamLibrary\\steamapps\\common\\War Thunder")
                return
        
        print(f"{colors.RED}Couldn't find game! Enter path manually... {colors.YELLOW}(The path to your game files){colors.END}")
        while True:
            _path = input('Enter path:')
            if _path.exists(f"{path}\\config.blk"):
                print(f"{colors.GREEN}Path successfully set!{colors.END}")
                break;
            else:
                print("Game not found in that path!")

    def set(self, key, value):
        self.config[key] = value
        with open('./config.yml', 'w') as ds:
            safe_dump(self.config, ds)

    def get(self, key):
        if key in self.config.keys():
            return self.config[key]
        else:
            return None