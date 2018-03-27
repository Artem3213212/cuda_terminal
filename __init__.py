import sys
import os
from cudatext import *

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_termilal.ini')


class Command:

    def __init__(self):

        self.shell_path = ini_read(fn_config, 'op', 'shell_path', '/bin/bash')
        self.color_back = int(ini_read(fn_config, 'colors', 'back', '0x0'), 16)
        self.color_font = int(ini_read(fn_config, 'colors', 'font', '0xFFFFFF'), 16)
            
    def open(self):
    
        self.title = 'Terminal'
        self.h_dlg = self.init_form()
        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, (self.title, self.h_dlg, fn_icon))
        app_proc(PROC_BOTTOMPANEL_ACTIVATE, self.title)
        
        self.edit.set_text_all('Test...\nok?')
        

    def init_form(self):
    
        h = dlg_proc(0, DLG_CREATE)
        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        
        self.edit = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'edit',
            'align': ALIGN_CLIENT,
            })
        
        self.edit.set_prop(PROP_GUTTER_ALL, False)
        self.edit.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.edit.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))
        
        return h


    def config(self):

        ini_write(fn_config, 'op', 'shell_path', self.shell_path)
        ini_write(fn_config, 'colors', 'back', hex(self.color_back))
        ini_write(fn_config, 'colors', 'font', hex(self.color_font))
        
        file_open(fn_config)
