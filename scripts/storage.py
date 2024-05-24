import sqlite3
from os import getenv, mkdir, path
from semver import Version
from time import time
from requests import get
from urllib import request
from nicegui import ui
from _version import __version__


class StorageInterface():
    _storage_path = f'{getenv('LOCALAPPDATA')}/War Thunder Translation Editor/'
    _database = None

    def __init__(self):
        # Ensure the storage path exists in appdata
        try:
            mkdir(self._storage_path)
        except: pass

        if not path.exists(self._storage_path):
            pass # TODO: Throw exception of some sort...

        # Open Database connection
        self._database = sqlite3.connect(self._storage_path + 'local.db')
        self._sanity_check()

    def _sanity_check(self):
        # Make sure all relevant tables exist
        cur = self._database.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key VARCHAR(255) NOT NULL PRIMARY KEY,
                value VARCHAR(65535)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                key VARCHAR(255) NOT NULL,
                language VARCHAR(255) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original TEXT,
                value TEXT,
                PRIMARY KEY (key, language, filename)
            );
        """)
        cur.close()
        version = self.get_config('version')
        # TODO: If compare returns 1, an update was installed. Check for DB updates?
        if version == None or Version.parse(__version__[1:]).compare(version[1:]) == 1:
            self.set_config('version', __version__)
        self._check_for_updates()
        self.save()

    def _check_for_updates(self):
        last_check = float(self.get_config('last_update_check'))
        if last_check != None and time() < last_check + (60 * 5):  # Only allow an update check every 5 minutes.
            print("Skipping check!")
            return
        
        rate_limit = None
        try:
            rate_limit = get('https://api.github.com/rate_limit').json()
        except:  # If we cannot fetch rate limit information, abort to be sure
            return
        
        if rate_limit['resources']['core']['remaining'] < 5:  # If we have less than 5 requests remaining, abort
            return

        versions = None
        try:
            versions = get('https://api.github.com/repos/b4t3s/warthunder-translation-editor/tags').json()
        except:
            return  # Again, if we cannot request, we might be getting rate-limited. Abort any further action
        
        self.set_config('last_update_check', time())

        if Version.parse(versions[0]['name'][1:]).compare(__version__[1:]) == 1:
            with ui.dialog() as diag:
                with ui.card():
                    with ui.row():
                        ui.label('New version available!')
                        ui.badge(__version__, color='negative')
                        ui.icon('east')
                        ui.badge(versions[0]['name'], color='positive')
                    with ui.row():
                        ui.button('Download', on_click=lambda: request.urlopen('https://github.com/B4T3S/Warthunder-Translation-Editor/releases'), color='positive', icon='download')
                        ui.button('Skip for now', on_click=diag.close, color='gray')
                diag.open()

    def get_config(self, key: str, default = None):
        cur = self._database.cursor()
        value = cur.execute('SELECT value FROM config WHERE key = ?', [key]).fetchone()
        cur.close()
        if value == None and default != None:
            return default
        return value[0] if value != None else value
    
    def set_config(self, key: str, value: str):
        cur = self._database.cursor()
        cur.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?);', [key, value])
        cur.close()

    def get_translation(self, key: str, language: str, file_name: str):
        cur = self._database.cursor()
        value = cur.execute('SELECT * FROM translations WHERE key = ? AND language = ? AND filename = ?;', [key, language, file_name]).fetchone()
        cur.close()
        return value
    
    def get_translations_for_file(self, file_name: str):
        cur = self._database.cursor()
        value = cur.execute('SELECT * FROM translations WHERE filename = ?;', [file_name]).fetchall()
        cur.close()
        return value
    
    def set_translation(self, key: str, language: str, file_name: str, original: str, value: str):
        cur = self._database.cursor()
        saved = self.get_translation(key, language, file_name)
        if saved != None:
            original = saved[3]
        cur.execute('INSERT OR REPLACE INTO translations (key, language, filename, original, value) VALUES (?, ?, ?, ?, ?);', [key, language, file_name, original, value])
        cur.close()
    
    def remove_translation(self, key: str, language: str, file_name: str):
        cur = self._database.cursor()
        cur.execute('DELETE FROM translations WHERE key = ? AND language = ? AND filename = ?;', [key, language, file_name])
        cur.close()
    
    def save(self):
        self._database.commit()


