import datetime
import os
import sys

import cudatext_keys as keys
import cudatext_cmd as cmds

from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock, active_count
from time import sleep
from signal import SIGTERM

from cudatext import *

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_terminal.ini')
MAX_BUFFER = 100*1000
MAX_HISTORY = 20
IS_WIN = os.name=='nt'
IS_MAC = sys.platform=='darwin'
DEF_SHELL = r'%windir%\system32\cmd' if IS_WIN else 'bash'
DEF_ADD_PROMPT = not IS_WIN
CODE_TABLE = 'cp866' if IS_WIN else 'utf8'
BASH_PROMPT = 'echo [`pwd`]$ '
READSIZE = 6*1024


def log(s):
    # Change conditional to True to log messages in a Debug process
    if False:
        now = datetime.datetime.now()
        print(now.strftime("%H:%M:%S ") + s)
    pass


def bool_to_str(v):
    return '1' if v else '0'


def str_to_bool(s):
    return s=='1'


class ControlTh(Thread):
    def __init__(self, Cmd):
        Thread.__init__(self)
        self.Cmd = Cmd

    def run(self):
        global CODE_TABLE
        global MAX_BUFFER
        if not IS_WIN:
            while True:
                s = self.Cmd.p.stdout.read(READSIZE)
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
                self.Cmd.btext = self.Cmd.btext[-MAX_BUFFER:]
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
                self.Cmd.btext = self.Cmd.btext[-MAX_BUFFER:]
                sleep(0.02)


class Command:

    def __init__(self):

        global CODE_TABLE
        CODE_TABLE = ini_read(fn_config, 'op', 'encoding', CODE_TABLE)

        global MAX_BUFFER
        try:
            MAX_BUFFER = int(ini_read(fn_config, 'op', 'max_buffer_size', str(MAX_BUFFER)))
        except:
            pass

        self.shell_path = ini_read(fn_config, 'op', 'shell_path', DEF_SHELL)
        self.add_prompt = str_to_bool(ini_read(fn_config, 'op', 'add_prompt', bool_to_str(DEF_ADD_PROMPT)))
        self.font_size = int(ini_read(fn_config, 'op', 'font_size', '9'))
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

        if not self.p:
            env = os.environ
            if IS_MAC:
                env['PATH'] += ':/usr/local/bin:/usr/local/sbin:/opt/local/bin:/opt/local/sbin'

            self.p = Popen(
                os.path.expandvars(self.shell_path),
                stdin = PIPE,
                stdout = PIPE,
                stderr = STDOUT,
                shell = IS_WIN,
                bufsize = 0,
                env = env
                )

            #w,self.r=os.pipe()
            self.p.stdin.flush()
            self.CtlTh=ControlTh(self)
            self.CtlTh.start()

        dlg_proc(self.h_dlg, DLG_CTL_FOCUS, name='input')


    def init_form(self):

        h = dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={
            'border': False,
            'keypreview': True,
            'on_key_down': self.form_key_down,
            'on_show': self.form_show,
            'on_hide': self.form_hide,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        self.memo = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'memo',
            'align': ALIGN_CLIENT,
            'font_size': self.font_size,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        self.input = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'input',
            'border': True,
            'align': ALIGN_BOTTOM,
            'font_size': self.font_size,
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
        self.memo.set_prop(PROP_MINIMAP, False)
        self.memo.set_prop(PROP_MICROMAP, False)

        self.input.set_prop(PROP_GUTTER_ALL, False)
        self.input.set_prop(PROP_ONE_LINE, True)
        self.input.set_prop(PROP_UNPRINTED_SHOW, False)
        self.input.set_prop(PROP_MARGIN, 2000)
        self.input.set_prop(PROP_HILITE_CUR_LINE, False)
        self.input.set_prop(PROP_HILITE_CUR_COL, False)

        dlg_proc(h, DLG_CTL_FOCUS, name='input')

        return h


    def config(self):

        ini_write(fn_config, 'op', 'max_buffer_size', str(MAX_BUFFER))
        ini_write(fn_config, 'op', 'encoding', CODE_TABLE)
        ini_write(fn_config, 'op', 'shell_path', self.shell_path)
        ini_write(fn_config, 'op', 'add_prompt', bool_to_str(self.add_prompt))
        ini_write(fn_config, 'op', 'font_size', str(self.font_size))

        file_open(fn_config)


    def timer_update(self, tag='', info=''):

        # log("Entering in timer_update")
        self.btextchanged = False
        self.block.release()
        sleep(0.03)
        self.block.acquire()
        if self.btextchanged:
            self.update_output(self.btext.decode(CODE_TABLE))


    def form_key_down(self, id_dlg, id_ctl, data='', info=''):

        #Enter
        if id_ctl==keys.VK_ENTER:
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
            # Stops the timer
            timer_proc(TIMER_STOP, self.timer_update, 0)
            ed.focus()
            ed.cmd(cmds.cmd_ToggleBottomPanel)
            return False

        #Break (cannot react to Ctrl+Break)
        if (id_ctl==keys.VK_PAUSE):
            self.button_break_click(0, 0)
            return False


    def form_hide(self, id_dlg, id_ctl, data='', info=''):
        timer_proc(TIMER_STOP, self.timer_update, 0)
        pass


    def form_show(self, id_dlg, id_ctl, data='', info=''):
        timer_proc(TIMER_START, self.timer_update, 200, tag='')
        dlg_proc(self.h_dlg, DLG_CTL_FOCUS, name='input')
        pass


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

        #del lead spaces
        while text.startswith(' '):
            text = text[1:]

        while len(self.history) > MAX_HISTORY:
            del self.history[0]

        try:
            n = self.history.index(text)
            del self.history[n]
        except:
            pass

        self.history += [text]
        self.input.set_text_all('')

        #support password input in sudo
        if not IS_WIN and text.startswith('sudo '):
            text = 'sudo --stdin '+text[5:]

        #don't write prompt, if sudo asks for password
        line = self.memo.get_text_line(self.memo.get_line_count()-1)
        is_sudo = not IS_WIN and line.startswith('[sudo] ')

        if self.add_prompt and not IS_WIN and not is_sudo:
            self.p.stdin.write((BASH_PROMPT+text+'\n').encode(CODE_TABLE))
            self.p.stdin.flush()

        if self.p:
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
        if not self.p: return

        try:
            self.p.send_signal(SIGTERM)
        except:
            pass

        if IS_WIN:
            self.p.wait()
        while self.p:
            self.timer_update()

        self.block.release()
        sleep(0.25)


    def button_break_click(self, id_dlg, id_ctl, data='', info=''):

        if IS_WIN:
            try:
                self.p.send_signal(SIGTERM)
            except:
                pass
            self.p.wait()
        else:
            try:
                self.p.send_signal(SIGTERM)
            except:
                pass

        while self.p:
            self.timer_update()
        self.open()

