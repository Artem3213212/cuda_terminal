import sys
import os
from cudatext import *

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')

class Command:

    def open(self):
    
        self.h_dlg = self.init_form()
        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, ("Terminal", self.h_dlg, fn_icon))
        
        self.edit.set_text_all('Test...\nok?')
        
        

    def init_form(self):
        h = dlg_proc(0, DLG_CREATE)
        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        
        self.edit = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'edit',
            'align': ALIGN_CLIENT,
            })
        
        return h


    def on_console(self, ed_self, text):
        pass
    
    def on_console_nav(self, ed_self, text):
        pass
