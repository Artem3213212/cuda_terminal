import sys
import os
from cudatext import *
from subprocess import Popen, PIPE, STDOUT

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

        timer_proc(TIMER_START, self.timer_update, 150, tag="")
        self.p = Popen(
            'ddddddd', #self.shell_path,
            #stdin = , 
            stdout = PIPE, 
            stderr = STDOUT, 
            shell = True
            )
        self.s = ''
                

    def init_form(self):
    
        h = dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={
            'border': False,
            'keypreview': True,
            'on_key_down': self.form_key_down,
            })
        
        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        nn = dlg_proc(h, DLG_CTL_ADD, 'editor')
        
        self.memo = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        self.input = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=nn))
        
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'memo',
            'align': ALIGN_CLIENT,
            })
        
        dlg_proc(h, DLG_CTL_PROP_SET, index=nn, prop={
            'name': 'input',
            'border': True,
            'align': ALIGN_BOTTOM,
            'h': 25,
            })
            
        dlg_proc(h, DLG_CTL_FOCUS, name='input')
        
        self.memo.set_prop(PROP_RO, True)
        self.memo.set_prop(PROP_CARET_VIRTUAL, False)
        self.memo.set_prop(PROP_GUTTER_ALL, False)
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))
        
        self.input.set_prop(PROP_GUTTER_ALL, False)
        self.input.set_prop(PROP_ONE_LINE, True)
        self.input.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.input.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))
        
        return h


    def config(self):

        ini_write(fn_config, 'op', 'shell_path', self.shell_path)
        ini_write(fn_config, 'colors', 'back', hex(self.color_back))
        ini_write(fn_config, 'colors', 'font', hex(self.color_font))
        
        file_open(fn_config)


    def timer_update(self, tag='', info=''):
        ss = self.p.stdout.read()
        try:
            s = ss.decode()
        except:
            s = ss.decode("cp1251")
        if not s:
            return
            
        self.add_output(s)


    def form_key_down(self, id_dlg, id_ctl, data='', info=''):
    
        if id_ctl==13: #Enter
            text = self.input.get_text_line(0)
            self.input.set_text_all('')
            self.input.set_caret(0, 0)
            self.run_cmd(text)


    def run_cmd(self, text):
    
        print('run:', text)
        #self.p.stdin.write(text)
        
        
    def add_output(self, s):
    
        self.memo.set_prop(PROP_RO, False)
        text = self.memo.get_text_all()
        self.memo.set_text_all(text+s)
        self.memo.set_prop(PROP_RO, True)
        
        n = self.memo.get_line_count()-1
        line = self.memo.get_text_line(n)
        self.memo.set_caret(len(line), n)
        
