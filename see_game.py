import time
from tkinter import Tk
from main import Game

from timeit import timeit

from functools import partial
from  pynput import keyboard

from pynput.keyboard import Key, KeyCode

from type_attack import TypeAttack

class Analyser:

    def update_view(self):
        self.init_view(self.iview)

    def delta_iview(self, n: int):
        self.iview += n
        if self.iview < 0:
            self.iview += self.turn + 1
        if self.iview > self.turn:
            self.iview -= (self.turn + 1)
        print(f"Current view {self.iview}/{self.turn}")
        self.update_view()

    def set_view(self, n: int):
        print(f"set_view {n}")
        self.iview = n
        self.update_view()

    def on_press_key(self, key):
        if not self.save_game:
            print("Pas de view")
            return
        if self.turn > 100:
            if key == Key.down:
                self.delta_iview(-100)
            if key == Key.up:
                self.delta_iview(100)
        if key == Key.left:
            self.delta_iview(-1)
        if key == Key.right:
            self.delta_iview(1)
        # print(key)
        if key == KeyCode.from_char('b'):
            self.set_view(0)
        if key == KeyCode.from_char('é'):
            self.set_view(self.turn)

    def get_location_at_time(self, nid, time):
        if nid in self.FAKE_ID_BLACK:
            nid = self.ID_BLACK_PYRAMID
        if nid in self.FAKE_ID_WHITE:
            nid = self.ID_WHITE_PYRAMID
        # print(self.moves_by_id[nid])
        # print(self.moves_by_id[nid].keys())
        # print(list(self.moves_by_id[nid].keys()))
        keys = np.array(list(self.moves_by_id[nid].keys()))
        # print(keys)
        keys = keys[keys < time]

        # print(keys)
        t = np.max(keys)
        return self.moves_by_id[nid][t]

    def is_alive_at_time(self, nid, time):
        return self.get_location_at_time(nid, time) != -1

    def init_view(self, time):
        self.canvas.delete("suppress")
        for nid in range(self.initial_number_of_real_pieces):
            if not self.is_alive_at_time(nid, time):
                continue

            point = self.value_by_id[nid]
            form = self.form_by_id[nid]
            team = self.team_by_id[nid]
            (j, i) = self.get_location_at_time(nid, time)
            color = "Blue" if team == 0 else "Red"
            if form == 1:
                self.canvas.create_oval(i * 50 + 5, j * 50 + 5, (i + 1) * 50 - 5, (j + 1) * 50 - 5,
                                        outline=color,
                                        fill="WHITE", width=2, tags="suppress")
            if form == 2:
                dp = np.array([(-20, 20), (20, 20), (0, -20)])
                points = (i * 50 + 25, j * 50 + 25) + dp
                self.canvas.create_polygon(points.flatten().tolist(), outline=color, fill="WHITE", width=2, tags="suppress")
            if form == 3:
                self.canvas.create_rectangle(i * 50 + 5, j * 50 + 5, (i + 1) * 50 - 5, (j + 1) * 50 - 5,
                                             outline=color, fill="WHITE", width=2, tags="suppress")

            if form <= 3:
                self.canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point) + "(" + str(nid) + ")", tags="suppress")
            else:
                self.canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point) + "(" + str(nid) + ")",
                                        fill=color, tags="suppress")
            

        if time > 0:
            (y, x), (y2, x2) = self.move_history[time - 1]
            self.canvas.create_line(x * 50 + 25, y * 50 + 25, x2 * 50 + 25, y2 * 50 + 25, arrow=tk.LAST,
                                    fill="GREEN", width=2, tags="suppress")
            for attacks in self.game_attacks[self.iview - 1]:
                (type_attack, attackers, attacked) = attacks
                n2 = attacked
                (y2, x2) = self.get_location_at_time(n2, time - 1)
                color_attack = ""
                if type_attack == TypeAttack.MEET:
                    color_attack = "deepskyblue4"  # bleu foncé
                elif type_attack == TypeAttack.GALLOWS:
                    color_attack = "lightslateblue"  # violet
                elif type_attack == TypeAttack.AMBUSH:
                    color_attack = "orangered1"
                elif type_attack == TypeAttack.PROGRESSION_A \
                        or type_attack == TypeAttack.PROGRESSION_G \
                        or type_attack == TypeAttack.PROGRESSION_H:
                    color_attack = "cyan"
                elif type_attack == TypeAttack.ASSAULT:
                    color_attack = "pink"
                elif type_attack == TypeAttack.SIEGE:
                    color_attack = "chocolate4"  # marron
                if SHOW_PRINT:
                    print(attacks)
                for attacker in attackers:
                    n = attacker
                    (y, x) = self.get_location_at_time(n, time)
                    self.canvas.create_line(x * 50 + 25, y * 50 + 25, x2 * 50 + 25, y2 * 50 + 25, arrow=tk.LAST,
                                            fill=color_attack, width=2, tags="suppress")

        self.canvas.update()

    def init_frame(self):
        # Ajout des éléments à la liste
        for i in range(1, self.turn + 1):
            if not self.game_attacks[i - 1]:
                continue
            types = set()
            # add star
            star = ""  # s’il y a une pyramide
            for attack in self.game_attacks[i - 1]:
                (type, attackers, attacked) = attack
                if self.form_by_id[attacked] == 4:
                    star = "*"
                types.add(type)
            label = ""
            for possibilities in TypeAttack:
                if possibilities in types:
                    label += possibilities.value
            button = tk.Button(self.frame, text=f"{i}:{label}{star} ", command=partial(self.set_view, i))
            button.pack(fill=tk.BOTH)

    def scrolllistbox2(self, event):
        self.canvas2.yview_scroll(int(-1 * (event.delta / 60)), "units")

    

    def show_game(self):
        if not self.save_game:
            return
        print("Temps d\'initialisation :", time.time() - self.start_time)
        self.iview = self.turn

        self.display = Tk.Tk()
        self.display.config(width=500, height=800)
        self.display.geometry("500x800")
        self.display.title('Grid')
        self.display.columnconfigure(0, weight=5)
        # self.display.columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(self.display, width=400, height=800, bg='#FFFFFF')
        # ligne
        
        list(map( lambda j : self.canvas.create_line(0, j * 50, self.width * 50, j * 50, fill="grey"), range(1, self.height)))
        
        list(map (lambda i: self.canvas.create_line(i * 50, 0, i * 50, self.height * 50, fill="grey"), range(1, self.width)))
        
        self.init_view(0)
        self.canvas.pack(side="left")
        # Comme fichier sroll_frame
        self.canvas2 = tk.Canvas(self.display, width=100, height=800)
        self.canvas2.pack(fill=tk.BOTH, expand=True)

        self.canvas2.bind('<Configure>', lambda e: self.canvas2.configure(scrollregion=self.canvas2.bbox('all')))
        self.frame = tk.Frame(self.canvas2, width=100, height=800)
        self.canvas2.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas2.bind_all("<MouseWheel>", self.scrolllistbox2)

        self.init_frame()
        # self.frame.pack(side="right", expand=True, fill=tk.BOTH)

        listener = keyboard.Listener(on_press=self.on_press_key)
        listener.start()  # start thread

        self.display.mainloop()

        listener.stop()  # stop thread
        listener.join()  # wait till thread really ends its job

    def __init__(self, game: Game) -> None:
        self.view = True

        self.iview = -1