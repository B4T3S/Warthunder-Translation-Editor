from nicegui import ui, app
import pandas as pd


class Editor():
    parent = None
    table: pd.DataFrame = None
    ui_table = None
    lang_select = None
    filter_input = None
    file_path = None
    edit_dialog = None
    changes = {}

    def __init__(self, file_path):
        self.file_path = file_path
        self.parent = ui.row().classes('w-full max-w-full')
        with self.parent:
            self.lang_select = ui.select([], label='Language', on_change=self._draw_table).classes('w-full')
            self.lang_select.disable()
            self.filter_input = ui.input('Filter', placeholder='Search for something to replace...').classes('w-full')
            with ui.row().classes('w-full'):
                ui.button('Load translation file', on_click=self.open_table, icon='upload').classes('w-[49%]').bind_enabled_from(self, 'ui_table', backward=lambda x: x == None)
                ui.button('Save translation file', on_click=self.save_table, icon='download', color='positive').classes('w-[49%]').bind_enabled_from(self, 'ui_table')
        self.edit_dialog = ui.dialog()

    def _edit_cell(self, key):
        currentText = self.table.loc[key, self.lang_select.value]
        def _reset_cell():
            if key in self.changes.keys():
                self.table.loc[key, self.lang_select.value] = self.changes[key]['original']
                self.changes.pop(key)
                self._draw_table()
            self.edit_dialog.close()
            
        def _save_cell():
            if inp.value != currentText:
                if key not in self.changes.keys():
                    self.changes[key] = {
                        'original': currentText,
                        'updated': inp.value
                    }
                else:
                    self.changes[key]['updated'] = inp.value
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
        

    def _draw_table(self):
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
        if self.file_path == None:
            return

        self.table = pd.read_csv(open(self.file_path, 'r', encoding="utf8"), sep=';')
        self.table.set_index('<ID|readonly|noverify>', drop=False, inplace=True)
        languages = self.table.columns[1:-2].to_list()
        if 'changes' in app.storage.general.keys() and self.file_path in app.storage.general['changes'].keys():
            self.changes = app.storage.general['changes'][self.file_path]
        self.lang_select.set_options(languages)
        if self.lang_select.value == None:
            self.lang_select.value = languages[0]
        self.lang_select.enable()
        self._draw_table()
    
    def save_table(self):
        if not 'changes' in app.storage.general.keys():
            app.storage.general['changes'] = {}    
        app.storage.general['changes'][self.file_path] = self.changes
        self.table.to_csv(open(self.file_path, 'w', encoding="utf8"), encoding="utf8", sep=';', index=False, lineterminator='\n')
        self.table = None
        if self.ui_table != None:
            self.ui_table.delete()
            self.ui_table = None
    
    def move(self, new_parent):
        self.parent.move(new_parent)