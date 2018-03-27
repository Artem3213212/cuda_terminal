from cudatext import *
import sys

class Command:
    def Open(self):
        try:
            MainForm = dlg_proc(0, DLG_CREATE)
            app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, tuple(["test", MainForm, "terminal.png"]))
            #dlg_proc(MainForm, DLG_CTL_ADD, param="")#ALIGN_CLIENT
            #dlg_proc()
        except Exception as e:
            msg_box(str(e), MB_OK)
    def on_console(self, ed_self, text):
        pass
    def on_console_nav(self, ed_self, text):
        pass