from nicegui import ui, app
from scripts.storage import StorageInterface
from os.path import exists
import pandas as pd


class Editor():
    logger = None
    storage = None
    parent = None
    table: pd.DataFrame = None
    ui_table = None
    lang_select = None
    filter_input = None
    file_name = None
    edit_dialog = None

    def __init__(self, storage: StorageInterface, filename: str, logger):
        self.logger = logger
        self.logger.debug('Initializing editor for ' + filename)
        self.storage = storage
        self.file_name = filename
        self.parent = ui.row().classes('w-full max-w-full')
        with self.parent:
            self.lang_select = ui.select([], label='Language', on_change=self._draw_table).classes('w-full')
            self.lang_select.disable()
            self.filter_input = ui.input('Filter', placeholder='Search for something to replace...').classes('w-full')
            # with ui.row().classes('w-full'):
            with ui.grid(columns=3).classes('w-full'):
                ui.button('Load translation file', on_click=self.open_table, icon='upload').bind_enabled_from(self, 'ui_table', backward=lambda x: x == None)
                ui.button('Close without saving', on_click=self.close_table, icon='close', color='negative').bind_enabled_from(self, 'ui_table')
                ui.button('Save translation file', on_click=self.save_table, icon='download', color='positive').bind_enabled_from(self, 'ui_table')
        self.edit_dialog = ui.dialog()

    def _edit_cell(self, key):
        self.logger.debug(f'Starting edit on cell ID: {key} LANG: {self.lang_select.value}')
        currentText = self.table.loc[key, self.lang_select.value]
        def _reset_cell():
            self.logger.debug(f'Resetting cell ID {key} for LANG {self.lang_select.value}')
            orig = self.storage.get_translation(key, self.lang_select.value, self.file_name)
            if orig != None:
                self.table.loc[key, self.lang_select.value] = orig[3]
                self.storage.remove_translation(key, self.lang_select.value, self.file_name)
                self._draw_table()
            self.edit_dialog.close()
            
        def _save_cell():
            self.logger.debug(f'Saving cell ID {key} for LANG {self.lang_select.value}')
            if inp.value != currentText:
                self.storage.set_translation(key, self.lang_select.value, self.file_name, currentText, inp.value)
                self.table.loc[key, self.lang_select.value] = inp.value
            self.edit_dialog.close()
            self._draw_table()
        
        self.edit_dialog.clear()
        with self.edit_dialog, ui.card().classes('w-1/2'):
            ui.label('Edit...')
            inp = ui.input(value=currentText, placeholder='Enter text').classes('w-full')
            with ui.row().classes('w-full'):
                ui.button('Close', on_click=self.edit_dialog.close)
                ui.button('Reset', color='negative', on_click=_reset_cell)
                ui.space()
                ui.button('Save', color='positive', on_click=_save_cell)

        self.edit_dialog.open()
    
    def _load_table(self):
        self.logger.debug(f'Loading file {self.file_name}')
        path = f'{self.storage.get_config('game_path')}\\lang\\{self.file_name}'
        if path == None or not exists(path):
            return False
        
        self.table = pd.read_csv(open(path, 'r', encoding="utf8"), sep=';')
        self.table.set_index('<ID|readonly|noverify>', drop=False, inplace=True)
        return True

    def _draw_table(self):
        self.logger.debug(f'Drawing table for file {self.file_name}')
        if not self.lang_select.enabled:
            return

        if self.ui_table != None:
            self.ui_table.delete()
            self.ui_table = None
        
        self.ui_table = ui.table.from_pandas(self.table[['<ID|readonly|noverify>', self.lang_select.value]], pagination=20, selection='single', row_key='<ID|readonly|noverify>')
        self.ui_table.add_slot('header', """
            <q-tr :props="props">
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.label }}
                </q-th>
                <q-th auto-width />
            </q-tr>
        """)
        self.ui_table.add_slot(f'body', """
            <q-tr :props="props">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
                <q-td auto-width>
                    <q-btn size="sm" color="accent" round dense @click="$parent.$emit('request_edit', props)" icon="edit" />
                </q-td>
            </q-tr>
        """)

        self.ui_table.on('request_edit', lambda msg: self._edit_cell(msg.args['key']))
        self.ui_table.classes('w-full max-w-full')
        self.ui_table.move(self.parent)
        self.ui_table.bind_filter_from(self.filter_input, 'value')
        pass

    def open_table(self):
        self.logger.debug(f'Opening table for file {self.file_name}')
        if not self._load_table():
            return
        languages = self.table.columns[1:-2].to_list()
        self.lang_select.set_options(languages)
        if self.lang_select.value == None:
            self.lang_select.value = languages[0]
        self.lang_select.enable()
        self._draw_table()
    
    def save_table(self):
        self.logger.debug(f'Saving file {self.file_name}')
        self.table.to_csv(open(f'{self.storage.get_config('game_path')}\\lang\\{self.file_name}', 'w', encoding="utf8"), encoding="utf8", sep=';', index=False, lineterminator='\n')
        self.storage.save()
        self.close_table()

    def close_table(self):
        self.table = None
        if self.ui_table != None:
            self.ui_table.delete()
            self.ui_table = None
    
    def reapply(self):
        self.logger.debug(f'Reapplying all changes for file {self.file_name}')
        if not self._load_table():
            return

        translations = self.storage.get_translations_for_file(self.file_name)
        if translations == None:
            return
        
        if len(translations) == 0:
            self.logger.debug(f'No changes found. Aborting!')
            ui.notify(f'No changes saved for {self.file_name}!', type='info')
            return

        for trans in translations:
            self.table.loc[trans[0], trans[1]] = trans[4]
        
        self.save_table()
        ui.notify(f'Made {len(translations)} changes in "{self.file_name}"!', type='positive')


    def move(self, new_parent):
        self.parent.move(new_parent)