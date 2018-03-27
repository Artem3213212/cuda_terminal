import sys
import os
from cudatext import *

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')

class Command:

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
        self.edit.set_prop(PROP_COLOR, (COLOR_ID_TextFont, 0xFFFFFF))
        self.edit.set_prop(PROP_COLOR, (COLOR_ID_TextBg, 0x0))
        
        return h

