import sys
import datetime
import os
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock

import cudatext_keys as keys
import cudatext_cmd as cmds
from cudatext import *

fn_icon = os.path.join(os.path.dirname(__file__), 'terminal.png')
fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_terminal.ini')
MAX_BUFFER = 100*1000
IS_WIN = os.name=='nt'
IS_MAC = sys.platform=='darwin'
IS_UNIX_ROOT = not IS_WIN and os.geteuid()==0
SHELL_UNIX = 'bash'
SHELL_MAC = 'bash'
SHELL_WIN = 'cmd.exe'
ENC = 'cp866' if IS_WIN else 'utf8'
BASH_CHAR = '#' if IS_UNIX_ROOT else '$'
BASH_PROMPT = 'echo [$USER:$PWD]'+BASH_CHAR+' '
BASH_CLEAR = 'clear';
MSG_ENDED = "\nConsole process was terminated.\n"
READSIZE = 4*1024
HOMEDIR = os.path.expanduser('~')
INPUT_H = 26
stop_t = False # stop thread

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

def pretty_path(s):
    if not IS_WIN:
        s = s.rstrip('\n')
        if s==HOMEDIR:
            s = '~'
        elif s.startswith(HOMEDIR+'/'):
            s = '~'+s[len(HOMEDIR):]
    return s


class ControlTh(Thread):
    def __init__(self, Cmd):
        Thread.__init__(self)
        self.Cmd = Cmd

    def add_buf(self, s, clear):
        self.Cmd.block.acquire()
        self.Cmd.btextchanged = True
        #limit the buffer size!
        self.Cmd.btext = (self.Cmd.btext+s)[-MAX_BUFFER:]
        if clear:
            self.Cmd.p=None
        self.Cmd.block.release()

    def run(self):
        global stop_t
        if not IS_WIN:
            while True:
                if stop_t: return
                if not self.Cmd.p:
                    sleep(0.5)
                    continue
                s = self.Cmd.p.stdout.read(READSIZE)
                if self.Cmd.p.poll() != None:
                    s = MSG_ENDED.encode(ENC)
                    self.add_buf(s, True)
                    # don't break, shell will be restarted
                elif s != '':
                    self.add_buf(s, False)
        else:
            while True:
                if stop_t: return
                if not self.Cmd.p:
                    sleep(0.5)
                    continue
                pp1 = self.Cmd.p.stdout.tell()
                self.Cmd.p.stdout.seek(0, 2)
                pp2 = self.Cmd.p.stdout.tell()
                self.Cmd.p.stdout.seek(pp1)
                if self.Cmd.p.poll() != None:
                    s = MSG_ENDED.encode(ENC)
                    self.add_buf(s, True)
                    # don't break, shell will be restarted
                elif pp2!=pp1:
                    s = self.Cmd.p.stdout.read(pp2-pp1)
                    self.add_buf(s, False)
                sleep(0.02)


class Command:
    title = 'Terminal'
    title_float = 'CudaText Terminal'
    hint_float = 'Terminal opened in floating window'
    h_dlg = None

    def __init__(self):

        if IS_WIN:
            global ENC
            ENC = ini_read(fn_config, 'op', 'encoding_windows', ENC)

        global MAX_BUFFER
        try:
            MAX_BUFFER = int(ini_read(fn_config, 'op', 'max_buffer_size', str(MAX_BUFFER)))
        except:
            pass

        self.shell_unix = ini_read(fn_config, 'op', 'shell_unix', SHELL_UNIX)
        self.shell_mac = ini_read(fn_config, 'op', 'shell_macos', SHELL_MAC)
        self.shell_win = ini_read(fn_config, 'op', 'shell_windows', SHELL_WIN)
        self.add_prompt = str_to_bool(ini_read(fn_config, 'op', 'add_prompt_unix', '1'))
        self.font_size = int(ini_read(fn_config, 'op', 'font_size', '9'))
        self.dark_colors = str_to_bool(ini_read(fn_config, 'op', 'dark_colors', '1'))
        self.floating = str_to_bool(ini_read(fn_config, 'op', 'floating_window', '0'))
        self.max_history = int(ini_read(fn_config, 'op', 'max_history', '10'))

        self.load_history()
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


    def load_pos(self):

        if not self.floating:
            return
        self.wnd_x = int(ini_read(fn_config, 'pos', 'x', '20'))
        self.wnd_y = int(ini_read(fn_config, 'pos', 'y', '20'))
        self.wnd_w = int(ini_read(fn_config, 'pos', 'w', '700'))
        self.wnd_h = int(ini_read(fn_config, 'pos', 'h', '400'))


    def save_pos(self):

        if not self.floating:
            return

        p = dlg_proc(self.h_dlg, DLG_PROP_GET)
        x = p['x']
        y = p['y']
        w = p['w']
        h = p['h']

        ini_write(fn_config, 'pos', 'x', str(x))
        ini_write(fn_config, 'pos', 'y', str(y))
        ini_write(fn_config, 'pos', 'w', str(w))
        ini_write(fn_config, 'pos', 'h', str(h))


    def upd_history_combo(self):

        self.input.set_prop(PROP_COMBO_ITEMS, '\n'.join(self.history))


    def load_history(self):

        self.history = []
        for i in range(self.max_history):
            s = ini_read(fn_config, 'history', str(i), '')
            if s:
                self.history += [s]


    def save_history(self):

        ini_proc(INI_DELETE_SECTION, fn_config, 'history')
        for (i, s) in enumerate(self.history):
            ini_write(fn_config, 'history', str(i), s)


    def open_init(self):

        self.h_dlg = self.init_form()

        if self.floating:
            self.load_pos()
            dlg_proc(self.h_dlg, DLG_PROP_SET, prop={
                'border': DBORDER_SIZE,
                'cap': self.title_float,
                'x': self.wnd_x,
                'y': self.wnd_y,
                'w': self.wnd_w,
                'h': self.wnd_h,
            })
            dlg_proc(self.h_dlg, DLG_SHOW_NONMODAL)
            h_embed = dlg_proc(0, DLG_CREATE)
            n = dlg_proc(h_embed, DLG_CTL_ADD, prop='panel')
            dlg_proc(h_embed, DLG_CTL_PROP_SET, index=n, prop={
                'color': 0xababab,
                'cap': self.hint_float,
                'align': ALIGN_CLIENT,
            })
        else:
            h_embed = self.h_dlg

        app_proc(PROC_BOTTOMPANEL_ADD_DIALOG, (self.title, h_embed, fn_icon))

        self.p = None
        self.block = Lock()
        self.block.acquire()
        self.btext = b''

        self.open_process()

        self.p.stdin.flush()
        self.CtlTh = ControlTh(self)
        self.CtlTh.start()

        timer_proc(TIMER_START, self.timer_update, 200, tag='')
        self.show_bash_prompt()


    def open_process(self):

        env = os.environ
        if IS_MAC:
            env['PATH'] += ':/usr/local/bin:/usr/local/sbin:/opt/local/bin:/opt/local/sbin'

        shell = self.shell_win if IS_WIN else self.shell_mac if IS_MAC else self.shell_unix

        self.p = Popen(
            os.path.expandvars(shell),
            stdin = PIPE,
            stdout = PIPE,
            stderr = STDOUT,
            shell = IS_WIN,
            bufsize = 0,
            env = env
            )


    def open(self):

        #dont init form twice!
        if not self.h_dlg:
            self.open_init()

        dlg_proc(self.h_dlg, DLG_CTL_FOCUS, name='input')

        if self.floating:
            #form can be hidden before, show
            dlg_proc(self.h_dlg, DLG_SHOW_NONMODAL)
            #via timer, to support clicking sidebar button
            timer_proc(TIMER_START, self.dofocus, 300, tag='')
        else:
            app_proc(PROC_BOTTOMPANEL_ACTIVATE, (self.title, True)) #True - set focus


    def exec(self, s):

        if self.p and s:
            self.p.stdin.write((s+'\n').encode(ENC))
            self.p.stdin.flush()


    def init_form(self):

        colors = app_proc(PROC_THEME_UI_DICT_GET,'')
        color_btn_back = colors['ButtonBgPassive']['color']
        color_btn_font = colors['ButtonFont']['color']

        color_memo_back = 0x0 if self.dark_colors else color_btn_back
        color_memo_font = 0xC0C0C0 if self.dark_colors else color_btn_font

        cur_font_size = self.font_size

        h = dlg_proc(0, DLG_CREATE)
        dlg_proc(h, DLG_PROP_SET, prop={
            'border': False,
            'keypreview': True,
            'on_key_down': self.form_key_down,
            'on_show': self.form_show,
            'on_hide': self.form_hide,
            'color': color_btn_back,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'button_ex')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'break',
            'a_l': None,
            'a_t': None,
            'a_r': ('', ']'),
            'a_b': ('', ']'),
            'w': 90,
            'h': INPUT_H,
            'cap': 'Break',
            'hint': 'Hotkey: Break',
            'on_change': self.button_break_click,
            })

        n = dlg_proc(h, DLG_CTL_ADD, 'editor_combo')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'input',
            'border': True,
            'h': INPUT_H,
            'a_l': ('', '['),
            'a_r': ('break', '['),
            'a_t': ('break', '-'),
            'font_size': cur_font_size,
            'texthint': 'Enter command here',
            })
        self.input = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))

        n = dlg_proc(h, DLG_CTL_ADD, 'editor')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
            'name': 'memo',
            'a_t': ('', '['),
            'a_l': ('', '['),
            'a_r': ('', ']'),
            'a_b': ('break', '['),
            'font_size': cur_font_size,
            })
        self.memo = Editor(dlg_proc(h, DLG_CTL_HANDLE, index=n))

        self.memo.set_prop(PROP_RO, True)
        self.memo.set_prop(PROP_CARET_VIRTUAL, False)
        self.memo.set_prop(PROP_GUTTER_ALL, False)
        self.memo.set_prop(PROP_UNPRINTED_SHOW, False)
        self.memo.set_prop(PROP_MARGIN, 2000)
        self.memo.set_prop(PROP_MARGIN_STRING, '')
        self.memo.set_prop(PROP_LAST_LINE_ON_TOP, False)
        self.memo.set_prop(PROP_HILITE_CUR_LINE, False)
        self.memo.set_prop(PROP_HILITE_CUR_COL, False)
        self.memo.set_prop(PROP_MODERN_SCROLLBAR, True)
        self.memo.set_prop(PROP_MINIMAP, False)
        self.memo.set_prop(PROP_MICROMAP, False)
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextBg, color_memo_back))
        self.memo.set_prop(PROP_COLOR, (COLOR_ID_TextFont, color_memo_font))

        self.input.set_prop(PROP_ONE_LINE, True)
        self.input.set_prop(PROP_GUTTER_ALL, True)
        self.input.set_prop(PROP_GUTTER_NUM, False)
        self.input.set_prop(PROP_GUTTER_FOLD, False)
        self.input.set_prop(PROP_GUTTER_BM, False)
        self.input.set_prop(PROP_GUTTER_STATES, False)
        self.input.set_prop(PROP_UNPRINTED_SHOW, False)
        self.input.set_prop(PROP_MARGIN, 2000)
        self.input.set_prop(PROP_MARGIN_STRING, '')
        self.input.set_prop(PROP_HILITE_CUR_LINE, False)
        self.input.set_prop(PROP_HILITE_CUR_COL, False)

        self.upd_history_combo()

        dlg_proc(h, DLG_SCALE)
        return h


    def config(self):

        ini_write(fn_config, 'op', 'shell_windows', self.shell_win)
        ini_write(fn_config, 'op', 'shell_unix', self.shell_unix)
        ini_write(fn_config, 'op', 'shell_macos', self.shell_mac)
        ini_write(fn_config, 'op', 'add_prompt_unix', bool_to_str(self.add_prompt))
        ini_write(fn_config, 'op', 'dark_colors', bool_to_str(self.dark_colors))
        ini_write(fn_config, 'op', 'floating_window', bool_to_str(self.floating))
        ini_write(fn_config, 'op', 'max_history', str(self.max_history))
        ini_write(fn_config, 'op', 'font_size', str(self.font_size))
        ini_write(fn_config, 'op', 'max_buffer_size', str(MAX_BUFFER))
        if IS_WIN:
            ini_write(fn_config, 'op', 'encoding_windows', ENC)

        file_open(fn_config)


    def timer_update(self, tag='', info=''):

        # log("Entering in timer_update")
        self.btextchanged = False
        if self.block.locked():
            self.block.release()
        sleep(0.03)
        self.block.acquire()
        if self.btextchanged:
            self.update_output(self.btext.decode(ENC))


    def form_key_down(self, id_dlg, id_ctl, data='', info=''):

        #Enter
        if (id_ctl==keys.VK_ENTER) and (data==''):
            text = self.input.get_text_line(0)
            self.input.set_text_all('')
            self.input.set_caret(0, 0)
            self.run_cmd(text)
            return False

        #Up/Down: scroll memo
        if (id_ctl==keys.VK_UP) and (data==''):
            self.scroll_memo(False)
            return False

        if (id_ctl==keys.VK_DOWN) and (data==''):
            self.scroll_memo(True)
            return False

        #Ctrl+Down: history menu
        if (id_ctl==keys.VK_DOWN) and (data=='c'):
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


    def form_show(self, id_dlg, id_ctl, data='', info=''):

        timer_proc(TIMER_START, self.timer_update, 300, tag='')


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


    def is_sudo_input(self):

        if IS_WIN:
            return False
        s = self.memo.get_text_line(self.memo.get_line_count()-1)
        return s and s.startswith('[sudo] password for ') and s.endswith(': ')


    def run_cmd(self, text):

        text = text.lstrip(' ')

        if text==BASH_CLEAR:
            self.btext = b''
            self.memo.set_text_all('')
            self.show_bash_prompt()
            return

        while len(self.history) >= self.max_history:
            del self.history[0]

        try:
            n = self.history.index(text)
            del self.history[n]
        except:
            pass

        self.history += [text]
        self.upd_history_combo()
        self.input.set_text_all('')

        sudo = not IS_WIN and text.startswith('sudo ')
        if sudo:
            text = 'sudo --stdin '+text[5:]

        self.exec(text)

        if not sudo:
            self.show_bash_prompt()


    def show_bash_prompt(self):

        if not IS_WIN:
            if self.add_prompt:
                self.exec(BASH_PROMPT)


    def run_cmd_n(self, n):

        if n<len(self.history):
            s = self.history[n]
            self.input.set_text_all(s)
            self.input.set_caret(len(s), 0)


    def update_output(self, s):

        #bash gives tailing EOL
        if not IS_WIN:
            s = s.rstrip('\n')

        self.memo.set_prop(PROP_RO, False)
        self.memo.set_text_all(s)
        self.memo.set_prop(PROP_RO, True)

        self.memo.cmd(cmds.cCommand_GotoTextEnd)
        self.memo.set_prop(PROP_LINE_TOP, self.memo.get_line_count()-3)


    def stop(self):

        try:
            if self.p:
                self.p.terminate()
                self.p.wait()
        except:
            pass


    def on_exit(self, ed_self):

        global stop_t
        stop_t = True

        timer_proc(TIMER_STOP, self.timer_update, 0)
        self.stop()

        if self.block.locked():
            self.block.release()

        self.save_pos()
        self.save_history()


    def button_break_click(self, id_dlg, id_ctl, data='', info=''):

        self.stop()
        self.open_process()
        self.show_bash_prompt()


    def scroll_memo(self, down):

        inf = self.memo.get_prop(PROP_SCROLL_VERT_INFO)
        n = inf['pos']
        nmax = inf['pos_last']
        if down:
            n = min(n+1, nmax)
        else:
            n = max(n-1, 0)
        self.memo.set_prop(PROP_SCROLL_VERT, n)


    def dofocus(self, tag='', info=''):

        timer_proc(TIMER_STOP, self.dofocus, 0)
        dlg_proc(self.h_dlg, DLG_FOCUS)
