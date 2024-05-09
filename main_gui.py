import pandas as pd
from nicegui import app, ui
from scripts import file_picker as fp, helpers
from os import path
from shutil import rmtree
from subprocess import run
from _version import __version__

# --== SET UP VARIABLES ==--
dark = ui.dark_mode().bind_value(app.storage.general, 'dark_mode')
file_picker = fp.local_file_picker('C:/', multiple=False)
config_stepper = None
translations = None
language_selector = None
editor_card = None

# --== FUNCTIONS ==--

def toggle_dark_theme():
    app.storage.general['dark_mode'] = not dark.value

def set_game_path(path: str):
    app.storage.general['game_path'] = path
    file_picker.close()
    update_stepper()

file_picker.submit = set_game_path

def try_find_game():
    path = helpers.find_game()
    if path is not None:
        set_game_path(path)
    else:
        ui.notify('Couldn\'t find game automatically, select game folder manually!', type='negative')

def update_stepper():
    if config_stepper == None:
        return
    
    if helpers.validate_game_path(app.storage.general['game_path']) == None:
        config_stepper.value = 'config'
    else:
        return
    if helpers.validate_game_config(app.storage.general['game_path']):
        config_stepper.value = 'lang'
    else:
        return
    if helpers.validate_lang_file(app.storage.general['game_path']):
        config_stepper.value = 'done'

    load_file()

def load_file():
    translations = helpers.load_translations(app.storage.general['game_path'])
    if language_selector != None:
        language_selector.set_options(translations.columns[:-2].to_list())

def try_update_game_config():
    if helpers.update_game_config(app.storage.general['game_path']):
        ui.notify('Updated game config', type='positive')
    update_stepper()

def launch_wt():
    run('start steam://rungameid/236390', shell=True)

def delete_language_file():
    if not helpers.validate_lang_file(app.storage.general['game_path']):
        return
    
    rmtree(f'{app.storage.general['game_path']}\\lang')
    ui.notify('Removed language file. Start the game to regenerate it!', type='info')
    update_stepper()

# --== ACTUAL WEBPAGE SETUP ==--

# Header
with ui.header(bordered=True):
    ui.label('War Thunder translation editor').classes('uppercase text-2xl self-center')
    ui.badge(__version__, color='secondary').classes('text-md self-center')
    ui.space()
    ui.button(on_click=toggle_dark_theme, icon='light_mode', color='secondary').bind_visibility_from(dark, 'value', value=True)
    ui.button(on_click=toggle_dark_theme, icon='dark_mode', color='secondary').bind_visibility_from(dark, 'value', value=False)

# Config
with ui.expansion('Configuration', icon='build').classes('w-full border'):
    with ui.splitter().classes("w-full") as splitter:
        with splitter.before:
            with ui.row().classes('w-full'):
                ui.input('Game location', placeholder='C:/Path/To/Your/Game', validation=helpers.validate_game_path).bind_value(app.storage.general, 'game_path').classes("w-3/5").disable()
                ui.button(icon='auto_fix_high', on_click=try_find_game).tooltip('Try to find the game automagically').classes('self-center')
                ui.button(icon='folder', on_click=file_picker.open).tooltip('Open file picker').classes('self-center')

            with ui.row().classes('w-full'):
                ui.button('Launch War Thunder', icon='sports_esports', on_click=launch_wt).tooltip('only works with the steam version')
                ui.button('Reset language files', icon='delete', color='red', on_click=delete_language_file).tooltip('Deletes the \'lang\' folder to force the game to re-create it')
            
        with splitter.after:
            with ui.stepper().props('vertical').classes('w-full') as stepper:
                config_stepper = stepper
                with ui.step('locate', title='Find game', icon='search'):
                    ui.label('Locate the game files')
                with ui.step('config', title='Check game config', icon='build'):
                    ui.label('Your config is not set up correctly')
                    with ui.stepper_navigation():
                        ui.button('Fix it', on_click=try_update_game_config)
                with ui.step('lang', title='Find language file', icon='description'):
                    ui.label('You\'ll have to launch the game once to generate the language file.')
                    with ui.stepper_navigation():
                        ui.button(icon='refresh', on_click=update_stepper).tooltip('Click this after closing the game again')
                with ui.step('done', title="Done!", icon='done'):
                    pass

update_stepper()

ui.run()