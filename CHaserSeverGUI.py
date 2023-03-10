import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tk_f
from PIL import ImageTk

import socket, os, random, multiprocessing, time, glob, json, pprint

from typing import Generator

from ReadConfig import ReadConfig
from CHaserServer import Game


class Game_Window(tk.Frame):
    def __init__(self, master: tk.Tk, pipe):
        self.pipe = pipe
        tk.Frame.__init__(self, master=master)
        master.title('MainWindow')

        # big_flame
        self.big_flame_menu = ttk.Frame()
        self.big_flame_game = ttk.Frame()

        self.__game_screen()
        self.__menu_screen()

        self.big_flame_menu.grid(row=0, column=0, sticky=tk.NSEW)

        
        self.cool_state = 0
        self.hot_state = 0
        '''
        0: 待機開始
        1: 待機中
        2: 接続中
        '''
        
        self.has_game_started = False
        self.__after()
        self.big_flame_menu.tkraise()

    def __game_screen(self):
        # frame
        self.game_frame_status = ttk.Frame(self.big_flame_game)
        self.game_frame_cool = ttk.Labelframe(self.big_flame_game, text='Cool')
        self.game_frame_hot = ttk.Labelframe(self.big_flame_game, text='Hot')

        # picture
        self.wall_image = ImageTk.PhotoImage(file='./画像/wall.png')
        self.item_image = ImageTk.PhotoImage(file='./画像/item.png')
        self.hot_image = ImageTk.PhotoImage(file='./画像/Hot.png')
        self.cool_image = ImageTk.PhotoImage(file='./画像/Cool.png')
        
        # canvas
        
        self.game_canvas = tk.Canvas(
            self.big_flame_game, width=378, height=428, bg='white', borderwidth=0)
        self.game_canvas.create_line(0, 2, 378, 2)
        self.game_canvas.create_line(0, 428, 379, 428)
        self.game_canvas.create_line(378, 2, 378, 428)
        self.game_canvas.create_line(2, 2, 2, 428)
        for i in range(1, 17):
            self.game_canvas.create_line(0, 2 + i * 25, 378, 2 + i * 25, dash=(1, 1))
        for i in range(1, 15):
            self.game_canvas.create_line(2 + i * 25, 0, 2 + i * 25, 428, dash=(1, 1))

        # separator
        ttk.Style().configure('black.TSeparator', background='black')
        self.game_separator = ttk.Separator(
            self.big_flame_game, orient='vertical', style='black.TSeparator')

        # font
        self.font_normal = tk_f.Font(family='MSゴシック', size=25)

        # status
        self.var_turn = tk.StringVar()
        self.var_winner = tk.StringVar()

        self.var_turn.set('Turn:100')
        self.var_winner.set('Draw')

        self.label_turn = ttk.Label(
            self.game_frame_status, textvariable=self.var_turn, font=self.font_normal)
        self.progressbar = ttk.Progressbar(
            self.game_frame_status, maximum=100, length=220)
        self.label_winner = ttk.Label(
            self.game_frame_status, textvariable=self.var_winner, font=(('MSゴシック', '30')))

        self.label_turn.pack()
        self.progressbar.pack()
        self.label_winner.pack()

        # Cool

        self.var_cool_score = tk.StringVar()
        self.var_cool_score.set('Score:0(Item:0)')

        self.label_cool_name = ttk.Label(
            self.game_frame_cool, text='自動君', font=self.font_normal)
        self.label_cool_score = ttk.Label(
            self.game_frame_cool, textvariable=self.var_cool_score, font=self.font_normal)

        self.label_cool_name.pack()
        self.label_cool_score.pack()

        # Hot
        self.var_hot_score = tk.StringVar()
        self.var_hot_score.set('Score:0(Item:0)')

        self.label_hot_name = ttk.Label(
            self.game_frame_hot, text='自動君', font=self.font_normal)
        self.label_hot_score = ttk.Label(
            self.game_frame_hot, textvariable=self.var_cool_score, font=self.font_normal)

        self.label_hot_name.pack()
        self.label_hot_score.pack()

        self.game_canvas.grid(column=0, row=0, padx=6, rowspan=3)
        self.game_separator.grid(
            column=1, row=0, sticky='ns', rowspan=3, padx=6)
        self.game_frame_status.grid(column=2, row=0, padx=6)
        self.game_frame_cool.grid(column=2, row=1, padx=6)
        self.game_frame_hot.grid(column=2, row=2, padx=6)

        self.big_flame_game.grid(row=0, column=0, sticky=tk.NSEW)

    def __menu_screen(self):
        # tk_setting
        self.font = ('', 10)
        self.big_flame_menu.columnconfigure(0, weight=1)
        self.big_flame_menu.columnconfigure(1, weight=1)

        # ver
        self.menu_settings_ver_score = tk.BooleanVar()
        self.menu_settings_ver_score.set(config.d['Score'])

        self.menu_settings_ver_log = tk.BooleanVar()
        self.menu_settings_ver_log.set(config.d['Log'])

        self.menu_settings_timeout_ver = tk.Variable()
        self.menu_settings_timeout_ver.set(2000)

        self.menu_settings_speed_ver = tk.Variable()
        self.menu_settings_speed_ver.set(100)

        self.menu_map_ver = tk.StringVar()
        self.menu_map_ver.set(config.d['NextMap'])

        # Cool
        self.menu_frame_cool, self.menu_label_ver_cool, self.menu_port_ver_cool, self.menu_mode_ver_cool, self.menu_button_cool, self.menu_cool_spinbox,  self.menu_cool_combobox = self.__cliants_menu(
            'COOL')
        self.menu_button_cool['command'] = self.__cool_wait
        self.menu_cool_combobox.bind('<<ComboboxSelected>>', self.__cool_stay)
        self.menu_port_ver_cool.set(config.d['CoolPort'])
        self.menu_mode_ver_cool.set(config.d['CoolMode'])
        

        # Hot
        self.menu_frame_hot, self.menu_label_ver_hot, self.menu_port_ver_hot, self.menu_mode_ver_hot, self.menu_button_hot, self.menu_hot_spinbox,  self.menu_hot_combobox = self.__cliants_menu(
            'HOT')
        self.menu_button_hot['command'] = self.__hot_wait
        self.menu_hot_combobox.bind('<<ComboboxSelected>>', self.__hot_stay)
        self.menu_port_ver_hot.set(config.d['HotPort'])
        self.menu_mode_ver_hot.set(config.d['HotMode'])

        # map_view
        size = 18
        self.menu_canvas = tk.Canvas(
            self.big_flame_menu, width=15 * size, height=17 * size, background='white')

        self.menu_canvas.grid(row=1, column=0, padx=10)

        # map_select
        self.menu_frame_map_select = ttk.Frame(self.big_flame_menu)

        self.menu_combobox = ttk.Combobox(
            self.menu_frame_map_select, textvariable=self.menu_map_ver, state='readonly', values=list(listup_maps()))
        self.menu_map_randomize = ttk.Button(
            self.menu_frame_map_select, text='ランダム', command=self.__map_randmize)
        self.menu_combobox.grid(row=0, column=0, pady=5)
        self.menu_map_randomize.grid(row=0, column=1)

        # server_address
        self.menu_server_address = ttk.Label(
            self.big_flame_menu, text=socket.gethostbyname(socket.gethostname()), font=self.font)

        self.menu_server_address.grid(row=4, column=0)

        # settings
        '''
        スコア
        ログ保存するか
        ゲーム進行速度
        タイムアウト
        ログ保存場所
        マップ保存場所
        '''
        self.menu_frame_settings = ttk.Labelframe(
            self.big_flame_menu, text='設定')

        self.menu_settings_box_score = ttk.Checkbutton(
            self.menu_frame_settings, text='スコアモード', variable=self.menu_settings_ver_score)
        self.menu_settings_box_log = ttk.Checkbutton(
            self.menu_frame_settings, text='ログ保存', variable=self.menu_settings_ver_log)

        self.menu_settings_label_timeout = ttk.Label(
            self.menu_frame_settings, text='タイムアウト(ms)', font=self.font)
        self.menu_settings_spinbox_timeout = ttk.Spinbox(
            self.menu_frame_settings, textvariable=self.menu_settings_timeout_ver)
        self.menu_settings_label_speed = ttk.Label(
            self.menu_frame_settings, text='進行速度(ms)', font=self.font)
        self.menu_settings_spinbox_speed = ttk.Spinbox(
            self.menu_frame_settings, textvariable=self.menu_settings_speed_ver)
        self.menu_settings_spinbox_timeout['from'] = 0
        self.menu_settings_spinbox_timeout['to'] = 10000
        self.menu_settings_spinbox_timeout['increment'] = 10
        self.menu_settings_spinbox_speed['from'] = 0
        self.menu_settings_spinbox_speed['to'] = 10000
        self.menu_settings_spinbox_speed['increment'] = 10

        self.menu_settings_button_log = ttk.Button(
            self.menu_frame_settings, text='ログ保存場所')
        self.menu_settings_button_log.grid(row=3, column=0)

        self.menu_settings_button_map = ttk.Button(
            self.menu_frame_settings, text='マップ保存場所')
        self.menu_settings_button_map.grid(row=3, column=1)

        self.menu_settings_box_score.grid(row=0, column=0)
        self.menu_settings_box_log.grid(row=0, column=1)
        self.menu_settings_label_timeout.grid(row=1, column=0)
        self.menu_settings_spinbox_timeout.grid(row=2, column=0)
        self.menu_settings_label_speed.grid(row=1, column=1)
        self.menu_settings_spinbox_speed.grid(row=2, column=1)

        # game_start
        self.menu_game_start = ttk.Button(self.big_flame_menu, text='ゲーム開始', command=self.__start_game)

        self.menu_game_start.grid(row=2, column=1, sticky=tk.W + tk.E)

        # Frame_grid
        self.menu_frame_cool.grid(
            row=0, column=0, sticky=tk.W + tk.E, pady=6, padx=5)
        self.menu_frame_hot.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.menu_frame_map_select.grid(row=2, column=0)
        self.menu_frame_settings.grid(row=1, column=1)

    def __cliants_menu(self, name):
        label_ver = tk.StringVar(value='名前\nIP')
        frame = ttk.Labelframe(self.big_flame_menu, text=name)
        frame.columnconfigure(2, weight=1)
        label = ttk.Label(frame, textvariable=label_ver,
                          justify='left', anchor=tk.NW, font=self.font)
        spinbox_ver = tk.Variable()
        spinbox = ttk.Spinbox(frame, textvariable=spinbox_ver, width=7, command=self.__set_config)
        spinbox['from'] = 1024
        spinbox['to'] = 5000
        combobox_ver = tk.StringVar()
        combobox = ttk.Combobox(frame, state='readonly', textvariable=combobox_ver, values=['User', 'Stay', 'Bot'], width=6)
        button = ttk.Button(frame, text='待機開始')
        label.grid(row=0, column=0, sticky=tk.W, columnspan=2)
        spinbox.grid(row=1, column=0)
        combobox.grid(row=1, column=1)
        button.grid(row=1, column=2, sticky=tk.E + tk.W)

        return frame, label_ver, spinbox_ver, combobox_ver, button, spinbox, combobox

    def __map_randmize(self):
        self.menu_combobox['values'] = (c := list(listup_maps()))
        self.menu_map_ver.set(random.choice(c))
    
    def __set_config(self):
        config.d['CoolPort'] = self.menu_port_ver_cool
        config.d['HotPort'] = self.menu_port_ver_hot
    
    def __cool_stay(self, _=None):
        if self.menu_mode_ver_cool.get() == 'Stay' and self.cool_state == 0:
            self.__cool_wait()

    def __hot_stay(self, _=None):
        if self.menu_mode_ver_hot.get() == 'Stay' and self.hot_state == 0:
            self.__hot_wait()
    
    def __cool_wait(self):
        self.pipe.send('C')
        if self.cool_state == 0:
            self.pipe.send('connect')
            self.pipe.send(self.menu_port_ver_cool.get())
            self.pipe.send(self.menu_mode_ver_cool.get())
            self.cool_state = 1
            self.menu_button_cool['text'] = '接続待ち'
            self.menu_cool_combobox['state'] = 'disable'
            self.menu_cool_spinbox['state'] = 'disable'
        else:
            self.pipe.send('disconnect')
            self.cool_state = 0
            self.menu_button_cool['text'] = '待機開始'
            self.menu_cool_combobox['state'] = 'readonly'
            self.menu_cool_spinbox['state'] = 'normal'

    def __hot_wait(self):
        self.pipe.send('H')
        if self.hot_state == 0:
            self.pipe.send('connect')
            self.pipe.send(self.menu_port_ver_hot.get())
            self.pipe.send(self.menu_mode_ver_hot.get())
            self.hot_state = 1
            self.menu_button_hot['text'] = '接続待ち'
            self.menu_hot_combobox['state'] = 'disable'
            self.menu_hot_spinbox['state'] = 'disable'
        else:
            self.pipe.send('disconnect')
            self.hot_state = 0
            self.menu_button_hot['text'] = '待機開始'
            self.menu_hot_combobox['state'] = 'readonly'
            self.menu_hot_spinbox['state'] = 'normal'
    
    def __start_game(self):
        if self.cool_state == self.hot_state == 2:
            self.__write_map()
            self.big_flame_game.tkraise()
            self.has_game_started = True
            
            self.pipe.send('start')
            self.pipe.send(self.menu_map_ver.get())
            self.pipe.send(self.menu_settings_timeout_ver.get())
            
            self.__game_tick()
    
    def __after(self):
        if not self.has_game_started:
            if self.pipe.poll():
                if self.pipe.recv() == 'H': # Hot
                    match self.pipe.recv():
                        case 'name':
                            print(self.pipe.recv(), 'が接続しました')
                            self.hot_state = 2
                            self.menu_button_hot['text'] = '切断'
                        case 'disconnect':
                            self.hot_state = 0
                            self.menu_button_hot['text'] = '待機開始'
                else: # Cool
                    match self.pipe.recv():
                        case 'name':
                            print(self.pipe.recv(), 'が接続しました')
                            self.cool_state = 2
                            self.menu_button_cool['text'] = '切断'
                        case 'disconnect':
                            self.hot_state = 0
                            self.menu_button_cool['text'] = '待機開始'
            if self.cool_state == self.hot_state == 2:
                self.menu_game_start['state'] = 'normal'
            else:
                self.menu_game_start['state'] = 'disable'
            root.after(100, self.__after)
    
    def __game_tick(self):
        self.pipe.send('ok')
        cl = self.pipe.recv()
        nowpos = self.pipe.recv()
        match self.pipe.recv():
            case 'w':
                i, j = self.pipe.recv()
                print(i, j)
                self.game_canvas.moveto(cl, i * 25 + 3, j * 25 + 3)
                if self.pipe.recv() == 'i':
                    self.game_canvas.create_image(15 + nowpos[0] * 25, 15 + nowpos[1] * 25, image=self.wall_image)
                    self.game_canvas.delete(self.game_screen_id[j][i])
        if self.pipe.recv() != 'gameset':
            root.after(self.menu_settings_speed_ver.get(), self.__game_tick)

    def __write_map(self):
        game_map = []
        hot = []
        cool = []
        
        self.game_screen_id = [[-1 for i in range(15)] for i in range(17)]
        
        try:
            with open(config.d['StagePath'] + r'/' + self.menu_map_ver.get() + '.CHmap', 'r') as f:
                j = json.load(f)
                game_map = j['Map']
                hot = j['Hot']
                cool = j['Cool']
        except FileNotFoundError:
            if self.menu_map_ver.get() == 'Blank':
                game_map = [[0 for i in range(15)] for i in range(17)]
                hot = [8, 9]
                cool = [6, 7]
            else:
                raise FileNotFoundError
        for i, x in enumerate(game_map):
            for j, y in enumerate(x):
                if hot == [j, i]:
                    self.game_canvas.create_image(15 + j * 25, 15 + i * 25, image=self.hot_image, tag='Hot')
                if cool == [j, i]:
                    self.game_canvas.create_image(15 + j * 25, 15 + i * 25, image=self.cool_image, tag='Cool')
                match y:
                    case 2:
                        self.game_canvas.create_image(15 + j * 25, 15 + i * 25, image=self.wall_image)
                    case 3:
                        self.game_screen_id[i][j] = self.game_canvas.create_image(15 + j * 25, 15 + i * 25, image=self.item_image)

def listup_maps() -> Generator[str, None, None]:
    for i in os.listdir(config.d['StagePath']):
        if i[-6:] == '.CHmap':
            yield os.path.basename(i)[:-6]
    yield 'Blank'


if __name__ == '__main__':
    config = ReadConfig()
    
    game_pipe, window_pipe = multiprocessing.Pipe()

    game = multiprocessing.Process(target=Game, name='Server', args=(game_pipe,))
    game.start()

    root = tk.Tk()
    root.geometry('680x450')
    root.resizable(False, False)
    game_window = Game_Window(root, window_pipe)

    game_window.mainloop()
