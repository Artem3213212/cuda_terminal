import sys
import os
from cudatext import *

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')

class Command:
    def open(self):
        self.h_dlg =  dlg_proc(0, DLG_CREATE)
        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, ("Terminal", self.h_dlg, fn_icon))
        #dlg_proc(MainForm, DLG_CTL_ADD, param="")#ALIGN_CLIENT

    def on_console(self, ed_self, text):
        pass
    
    def on_console_nav(self, ed_self, text):
        pass
