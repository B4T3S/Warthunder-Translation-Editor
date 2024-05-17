# This file provides some basic helper functions, to keep the main file clean(-ish)

import pandas as pd
import random

from os import path
from platform import system
from nicegui import ui, elements

def is_windows():
    return system() == 'Windows'

def find_game():
    if not is_windows():
        return None
    
    import win32api
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]

    for drive in drives:
        letter = drive[0]
        if letter == 'C':
            if path.exists("C:\\Program Files (x86)\\Steam\\steamapps\\common\\War Thunder\\config.blk"):
                return "C:\\Program Files (x86)\\Steam\\steamapps\\common\\War Thunder"
            if path.exists("C:\\Program Files\\Steam\\steamapps\\common\\War Thunder\\config.blk"):
                return "C:\\Program Files\\Steam\\steamapps\\common\\War Thunder"
        
        if path.exists(f"{letter}:\\SteamLibrary\\steamapps\\common\\War Thunder\\config.blk"):
            return f"{letter}:\\SteamLibrary\\steamapps\\common\\War Thunder"

def validate_game_path(_path: str):
    return "Couldn't find game" if not path.exists(f'{_path}\\config.blk') else None

def validate_game_config(_path: str):
    if not path.exists(f'{_path}\\config.blk'):
        return False
    
    # Get the games config file
    game_config = open(f'{_path}\\config.blk', 'r+').readlines()
    return '  testLocalization:b=yes\n' in game_config

def update_game_config(_path: str):
    if not path.exists(f'{_path}\\config.blk'):
        return False
    
    if validate_game_config(_path):
        return True
    
    game_config = open(f'{_path}\\config.blk', 'r+').readlines()
    with open(f'{_path}\\config.blk.backup', 'w+') as backup:
        backup.writelines(game_config)
        ui.notify('Backed up old config file', type='info')

    debug_index = game_config.index('debug{\n')
    if debug_index:
        game_config.insert(debug_index+1, '  testLocalization:b=yes\n')
        with open(f'{_path}\\config.blk', 'w') as config_file:
            config_file.writelines(game_config)
            return True
    
    return False

def validate_lang_file(_path: str):
    return path.exists(f'{_path}\\lang\\menu.csv')

def load_translations(_path: str):
    csv = pd.read_csv(open(f'{_path}\\lang\\menu.csv', 'r', encoding="utf8"), sep=';')
    return csv
