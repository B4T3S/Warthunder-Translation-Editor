import pandas as pd
import logging
from nicegui import app, ui
from scripts import file_picker as fp, helpers, editor, storage
from os import path, getenv
from sys import argv
from shutil import rmtree
from subprocess import run
from _version import __version__

# --== SET UP VARIABLES ==--
file_picker = fp.local_file_picker('C:/', multiple=False)
translations = None
editors = []
storage = storage.StorageInterface()
dark = ui.dark_mode()
dark.value = int(storage.get_config('darkmode', 0)) == 1

# --== SET UP LOGGING ==--
logFormatter = logging.Formatter('%(relativeCreated)d [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if '--verbose' in argv else logging.INFO)

fh = logging.FileHandler(f'{getenv('LOCALAPPDATA')}/War Thunder Translation Editor/logs.txt', mode='w')
fh.setFormatter(logFormatter)
logger.addHandler(fh)

sh = logging.StreamHandler()
sh.setFormatter(logFormatter)
logger.addHandler(sh)

logger.info('STARTING')
logger.info(f'Version {__version__}')

# --== FUNCTIONS ==--

def toggle_dark_theme():
    dark.toggle()
    storage.set_config('darkmode', dark.value)
    logger.info('Toggling darkmode. New value: ' + dark.value)

def set_game_path(path: str):
    if type(path) is list:  # The manual file picker gives back a list with one entry, so we just do this.
        path = path[0]
    storage.set_config('game_path', path)
    location_input.value = path
    file_picker.close()
    update_stepper()
    logger.info('Updating game path: ' + path)

file_picker.submit = set_game_path

def try_find_game():
    logger.info('Trying to find game automatically')
    path = helpers.find_game()
    if path is not None:
        set_game_path(path)
    else:
        ui.notify('Couldn\'t find game automatically, select game folder manually!', type='negative')

def update_stepper():
    if config_stepper == None:
        return
    
    reset_lang_files_button.disable()
    open_folder_button.disable()
    reapply_button.disable()

    if helpers.validate_game_path(storage.get_config('game_path')) == None:
        config_stepper.value = 'config'
    else:
        return
    if helpers.validate_game_config(storage.get_config('game_path')):
        config_stepper.value = 'lang'
        open_folder_button.enable()
    else:
        return
    if helpers.validate_lang_file(storage.get_config('game_path')):
        config_stepper.value = 'done'
        reset_lang_files_button.enable()
        reapply_button.enable()

def try_update_game_config():
    logger.info('Updating game config...')
    if helpers.update_game_config(storage.get_config('game_path')):
        ui.notify('Updated game config', type='positive')
        logger.info('Updated game config!')
    update_stepper()

def delete_language_file():
    if not helpers.validate_lang_file(storage.get_config('game_path')):
        return
    
    rmtree(f'{storage.get_config('game_path')}\\lang')
    ui.notify('Removed language file. Start the game to regenerate it!', type='info')
    update_stepper()

def reapply_changes():
    for e in editors:
        e.reapply()

# --== ACTUAL WEBPAGE SETUP ==--

# Header
with ui.header(bordered=True):
    ui.label('War Thunder translation editor').classes('uppercase text-2xl self-center')
    ui.badge(__version__, color='secondary').classes('text-md self-center')
    ui.space()
    ui.button(on_click=toggle_dark_theme, icon='light_mode', color='secondary').bind_visibility_from(dark, 'value', value=True)
    ui.button(on_click=toggle_dark_theme, icon='dark_mode', color='secondary').bind_visibility_from(dark, 'value', value=False)

# Config
with ui.expansion('Configuration', icon='build', group='group', value=True).classes('w-full border'):
    with ui.splitter().classes("w-full") as splitter:
        with splitter.before:
            with ui.row().classes('w-full'):
                location_input = ui.input('Game location', placeholder='C:/Path/To/Your/Game', validation=helpers.validate_game_path).classes("w-3/5")
                location_input.value = storage.get_config('game_path')
                location_input.disable()
                ui.button(icon='auto_fix_high', on_click=try_find_game).tooltip('Try to find the game automagically!').classes('self-center')
                ui.button(icon='folder', on_click=file_picker.open).tooltip('Open file picker').classes('self-center')

            with ui.grid(columns=2):
                ui.button('Launch War Thunder', icon='sports_esports', on_click=lambda: run('start steam://rungameid/236390', shell=True)).tooltip('Only works with the steam version')
                reset_lang_files_button = ui.button('Reset language files', icon='delete', color='red', on_click=delete_language_file).tooltip('Deletes the \'lang\' folder to force the game to re-create it')
                open_folder_button = ui.button('Open game folder', icon='folder').on_click(lambda: run(f'explorer {storage.get_config('game_path')}'))
                reapply_button = ui.button('Re-apply changes', icon='cached', color='positive', on_click=reapply_changes).tooltip('Tries to reapply all changes you\'ve made so far.\n\nUse this after resetting your language files to get all your changes back!')
            
        with splitter.after:
            with ui.stepper().props('vertical').classes('w-full') as stepper:
                config_stepper = stepper
                with ui.step('locate', title='Find game', icon='search'):
                    ui.label('Locate the game files')
                with ui.step('config', title='Check game config', icon='build'):
                    ui.label('Your config is not set up correctly')
                    with ui.stepper_navigation():
                        ui.button('Fix it', on_click=try_update_game_config)
                with ui.step('lang', title='Find language files', icon='description'):
                    ui.label('You\'ll have to launch the game once to generate the language file.')
                    with ui.stepper_navigation():
                        ui.button(icon='refresh', on_click=update_stepper).tooltip('Click this after closing the game again')
                with ui.step('done', title="Done!", icon='done'):
                    pass

update_stepper()

with ui.expansion('Common GUI', icon="language", group='group').classes('w-full border'):
    editors.append(editor.Editor(storage, 'menu.csv', logger))

with ui.expansion('Unit Names', icon="language", group='group').classes('w-full border'):
    editors.append(editor.Editor(storage, 'units.csv', logger))

try:
    import pyi_splash
    pyi_splash.close()
except: pass  # If we run into this, we're running outside of a pyinstaller bundle... just ignore the exception and move on

# If a file called .dev exists next to us, run in the browser with hot-reload enabled.
if '--dev' in argv:
    ui.run(title="Translation Editor")
else:  # Otherwise run natively and without hot reload
    ui.run(title="Translation Editor", reload=False, native=True, window_size=(1200, 800))