import sys
import os
from cudatext import *
import cudatext_keys as keys
import cudatext_cmd as cmds
from cudax_lib import int_to_html_color, html_color_to_int
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock, active_count
from time import sleep
from signal import CTRL_C_EVENT

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_terminal.ini')
MAX_HISTORY = 20
IS_WIN = os.name=='nt'
DEF_SHELL = r'%windir%\system32\cmd' if IS_WIN else 'bash'
DEF_ADD_PROMPT = not IS_WIN
CODE_TABLE = 'cp866' if IS_WIN else 'utf8'
BASH_PROMPT = 'echo [`pwd`]$ '

def bool_to_str(v):
    return '1' if v else '0'

def str_to_bool(s):
    return s=='1'
    
class ControlTh(Thread):
    def __init__(self, Cmd):
        Thread.__init__(self)
        self.Cmd = Cmd
    def run(self):
        if not IS_WIN:
            while True:
                s = self.Cmd.p.stdout.read(1)
                if self.Cmd.p.poll() != None:
                    s = "\nConsole process was terminated.\n".encode(CODE_TABLE)
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.p=None
                    self.Cmd.block.release()
                    break
                if s != '':
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.block.release()
        else:
            while True:
                pp1 = self.Cmd.p.stdout.tell()
                self.Cmd.p.stdout.seek(0, 2)
                pp2 = self.Cmd.p.stdout.tell()
                self.Cmd.p.stdout.seek(pp1)
                if self.Cmd.p.poll() != None:
                    s = "\nConsole process was terminated.\n".encode(CODE_TABLE)
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.p=None
                    self.Cmd.block.release()
                    break
                if pp2!=pp1:
                    s = self.Cmd.p.stdout.read(pp2-pp1)
                    self.Cmd.block.acquire()
                    self.Cmd.btextchanged = True
                    self.Cmd.btext=self.Cmd.btext+s
                    self.Cmd.block.release()
                sleep(0.02)


class Command:

    def __init__(self):

        global CODE_TABLE
        CODE_TABLE = ini_read(fn_config, 'op', 'encoding', CODE_TABLE)

        self.shell_path = ini_read(fn_config, 'op', 'shell_path', DEF_SHELL)
        self.add_prompt = str_to_bool(ini_read(fn_config, 'op', 'add_prompt', bool_to_str(DEF_ADD_PROMPT)))
        self.color_back = html_color_to_int(ini_read(fn_config, 'color', 'back', '#555'))
        self.color_font = html_color_to_int(ini_read(fn_config, 'color', 'font', '#eee'))
        self.history = []
        self.h_menu = menu_proc(0, MENU_CREATE)

        self.menu_calls = []
        self.menu_calls += [ lambda: self.run_cmd_n(0) ]
        self.menu_calls += [ lambda: self.run_cmd_n(1) ]
        self.menu_calls += [ lambda: self.run_cmd_n(2) ]
        self.menu_calls += [ lambda: self.run_cmd_n(3) ]
        self.menu_calls += [ lambda: self.run_cmd_n(4) ]
        self.menu_calls += [ lambda: self.run_cmd_n(5) ]
        self.menu_calls += [ lambda: self.run_cmd_n(6) ]
        self.menu_calls += [ lambda: self.run_cmd_n(7) ]
        self.menu_calls += [ lambda: self.run_cmd_n(8) ]
        self.menu_calls += [ lambda: self.run_cmd_n(9) ]
        self.menu_calls += [ lambda: self.run_cmd_n(10) ]
        self.menu_calls += [ lambda: self.run_cmd_n(11) ]
        self.menu_calls += [ lambda: self.run_cmd_n(12) ]
        self.menu_calls += [ lambda: self.run_cmd_n(13) ]
        self.menu_calls += [ lambda: self.run_cmd_n(14) ]
        self.menu_calls += [ lambda: self.run_cmd_n(15) ]
        self.menu_calls += [ lambda: self.run_cmd_n(16) ]
        self.menu_calls += [ lambda: self.run_cmd_n(17) ]
        self.menu_calls += [ lambda: self.run_cmd_n(18) ]
        self.menu_calls += [ lambda: self.run_cmd_n(19) ]
        self.menu_calls += [ lambda: self.run_cmd_n(20) ]
        self.menu_calls += [ lambda: self.run_cmd_n(21) ]

        self.title = 'Terminal'
        self.h_dlg = self.init_form()
        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, (self.title, self.h_dlg, fn_icon))
        self.p = None
        self.block = Lock()
        self.block.acquire()
        self.btext = b''
        timer_proc(TIMER_START, self.timer_update, 200, tag='')


    def open(self):

        app_proc(PROC_BOTTOMPANEL_ACTIVATE, self.title)

        if self.p == None:
            self.p = Popen(
                os.path.expandvars(self.shell_path),
                stdin = PIPE,
                stdout = PIPE,
                stderr = STDOUT,
                shell = True,
                bufsize = 0
                )

            #w,self.r=os.pipe()
            self.p.stdin.flush()
            self.CtlTh=ControlTh(self)
            self.CtlTh.start()
            self.s = ''


    def init_form(self):

        h = dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={
            'border': False,
            'keypreview': True,
            'on_key_down': self.form_key_down,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        self.memo = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'memo',
            'align': ALIGN_CLIENT,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        self.input = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'input',
            'border': True,
            'align': ALIGN_BOTTOM,
            'h': 26,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'button_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'break',
            'p': 'input',
            'align': ALIGN_RIGHT,
            'w': 90,
            'cap': 'Break',
            'hint': 'Hotkey: Break',
            'on_change': self.button_break_click,
            })

        self.memo.set_prop(PROP_RO, True)
        self.memo.set_prop(PROP_CARET_VIRTUAL, False)
        self.memo.set_prop(PROP_GUTTER_ALL, False)
        self.memo.set_prop(PROP_UNPRINTED_SHOW, False)
        self.memo.set_prop(PROP_MARGIN, 2000)
        self.memo.set_prop(PROP_LAST_LINE_ON_TOP, False)
        self.memo.set_prop(PROP_HILITE_CUR_LINE, False)
        self.memo.set_prop(PROP_HILITE_CUR_COL, False)
        self.memo.set_prop(PROP_MODERN_SCROLLBAR, True)
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))

        self.input.set_prop(PROP_GUTTER_ALL, False)
        self.input.set_prop(PROP_ONE_LINE, True)
        self.input.set_prop(PROP_UNPRINTED_SHOW, False)
        self.input.set_prop(PROP_MARGIN, 2000)
        self.input.set_prop(PROP_HILITE_CUR_LINE, False)
        self.input.set_prop(PROP_HILITE_CUR_COL, False)
        self.input.set_prop(PROP_CARET_SHAPE, 15) #horz 3pix line
        self.input.set_prop(PROP_COLOR, (COLOR_ID_TextFont, self.color_font))
        self.input.set_prop(PROP_COLOR, (COLOR_ID_TextBg, self.color_back))

        dlg_proc(h, DLG_CTL_FOCUS, name='input')
        
        return h


    def config(self):

        ini_write(fn_config, 'op', 'encoding', CODE_TABLE)
        ini_write(fn_config, 'op', 'shell_path', self.shell_path)
        ini_write(fn_config, 'op', 'add_prompt', bool_to_str(self.add_prompt))
        ini_write(fn_config, 'color', 'back', int_to_html_color(self.color_back))
        ini_write(fn_config, 'color', 'font', int_to_html_color(self.color_font))

        file_open(fn_config)


    def timer_update(self, tag='', info=''):
        self.btextchanged = False
        self.block.release()
        sleep(0.03)
        self.block.acquire()
        if self.btextchanged:
            self.update_output(self.btext.decode(CODE_TABLE))


    def form_key_down(self, id_dlg, id_ctl, data='', info=''):

        #Enter
        if id_ctl==13:
            text = self.input.get_text_line(0)
            self.input.set_text_all('')
            self.input.set_caret(0, 0)
            self.run_cmd(text)
            return False

        #history menu
        if (id_ctl==keys.VK_DOWN):
            self.show_history()
            return False

        #Escape: go to editor
        if (id_ctl==keys.VK_ESCAPE) and (data==''):
            ed.focus()
            ed.cmd(cmds.cmd_ToggleBottomPanel)
            return False
            
        #Break (cannot react to Ctrl+Break)
        if (id_ctl==keys.VK_PAUSE):
            self.button_break_click(0, 0)
            return False
    

    def show_history(self):

        menu_proc(self.h_menu, MENU_CLEAR)
        for (index, item) in enumerate(self.history):
            menu_proc(self.h_menu, MENU_ADD,
                index=0,
                caption=item,
                command=self.menu_calls[index],
                )

        prop = dlg_proc(self.h_dlg, DLG_CTL_PROP_GET, name='input')
        x, y = prop['x'], prop['y']
        x, y = dlg_proc(self.h_dlg, DLG_COORD_LOCAL_TO_SCREEN, index=x, index2=y)
        menu_proc(self.h_menu, MENU_SHOW, command=(x, y))


    def run_cmd(self, text):

        while len(self.history) > MAX_HISTORY:
            del self.history[0]

        try:
            n = self.history.index(text)
            del self.history[n]
        except:
            pass

        self.history += [text]
        
        if self.add_prompt and not IS_WIN:
            self.p.stdin.write((BASH_PROMPT+text+'\n').encode(CODE_TABLE))
            self.p.stdin.flush()

        if self.p != None:
            self.p.stdin.write((text+'\n').encode(CODE_TABLE))
            self.p.stdin.flush()


    def run_cmd_n(self, n):

        self.run_cmd(self.history[n])


    def add_output(self, s):
        self.memo.set_prop(PROP_RO, False)
        text = self.memo.get_text_all()
        self.memo.set_text_all(text+s)
        self.memo.set_prop(PROP_RO, True)

        self.memo.cmd(cmds.cCommand_GotoTextEnd)


    def update_output(self, s):
        self.memo.set_prop(PROP_RO, False)
        self.memo.set_text_all(s)
        self.memo.set_prop(PROP_RO, True)

        self.memo.cmd(cmds.cCommand_GotoTextEnd)


    def on_exit(self, ed_self):

        timer_proc(TIMER_STOP, self.timer_update, 0)

        if self.p != None:
            self.p.send_signal(CTRL_C_EVENT)
            #sleep(0.1)

            self.block.release()
            sleep(0.25)


    def button_break_click(self, id_dlg, id_ctl, data='', info=''):
    
        try:
          self.p.send_signal(CTRL_C_EVENT)
        except:
          pass
        self.timer_update()
        self.open()
