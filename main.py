
from math import log
import tkinter as tk
from typing import OrderedDict

import numba as nb
import numpy as np
from json import loads
import time
from timeit import timeit

from functools import partial
from  pynput import keyboard
from pynput.keyboard import Key, KeyCode

from enums.type_attack import TypeAttack
import random

from numba import njit, objmode, types
from numba.experimental import jitclass
from numba import int32, float32, boolean

width, height = (8, 16)

length_of_data_pawn = 1
ID_WHITE_PYRAMID = 37
ID_BLACK_PYRAMID = 11

BLACK_ID = list(range(0, 24))
WHITE_ID = list(range(24, 48))

FAKE_ID_WHITE = list(range(48, 53 + 1))
FIRST_FAKE_ID_WHITE = FAKE_ID_WHITE[0]
FAKE_ID_BLACK = list(range(54, 58 + 1))
FIRST_FAKE_ID_BLACK = FAKE_ID_BLACK[0]

SHOW_PRINT = False


def clear_file(f: str):
    with open(f + ".txt", "w"):
        pass



def print_file(f: str, args):
    arg = ""
    for a in args:
        arg += " " + str(a)
    with open(f + ".txt", "a") as file:
        file.write(arg + "\n")

@njit
def is_int(a):
    return int(a) == a

@njit
def is_power_or_root(a, b):
    if a <= 0 or b <= 0:
        if SHOW_PRINT:
            print("IS POWER OR ROOT ERROR", a, b)
        return
    if a == b:
        return True
    elif a == 1 or b == 1:
        return False
    return is_int(log(b) / log(a)) or is_int(log(a) / log(b))


@njit
def a_is_equation(a, b, c):
    return a + b == c \
        or abs(a - b) == c \
        or a * b == c \
        or a / b == c \
        or b / a == c


@njit
def get_progression(a, b, c):
    t = [a, b, c]
    t.sort()
    u, v, w = t
    if 2 * v == u + w:
        if SHOW_PRINT:
            print(f"aide: 2*{v} = {u}+{w}")
        return 1  # arithmétique
    if v * v == u * w:
        if SHOW_PRINT:
            print(f"aide: {v}*{v} = {u}*{w}")
        return 2  # géométrique
    if v * (u + w) == 2 * u * w:
        if SHOW_PRINT:
            print(f"aide: {v}*({u}+{w}) = 2*{u}*{w}")
        return 3  # harmonique
    return 0


t_locations = nb.typed.Dict.empty(
    key_type=int32,
    value_type=int32[:]
)

t_aim_value = np.array([[2], [2]])

t_aim = nb.typed.Dict.empty(
    key_type=int32,
    value_type=nb.typeof(t_aim_value)
)

t_shooter_value = np.array([[2], [2]])

t_shooter = nb.typed.Dict.empty(
    key_type=int32,
    value_type=nb.typeof(t_aim_value)
)

t_moves_by_id = nb.typed.Dict.empty(
    key_type=int32,
    value_type=int32[:]
)

double_int = nb.typeof(np.full((1, 1), 1))

spec2 = [
    ("start_time", float32),
    ("board", double_int),
    ("turn", int32),
    ("player_turn", int32),
    ("width", int32),
    ("height", int32),
    ("stop", boolean),
    ("last_move", double_int),
    ("view", int32),
    ("save_game", boolean),
    ("move_history", double_int),
    ("locations", nb.typeof(t_locations)),
    ("aim", nb.typeof(t_aim)),
    ("shooter", nb.typeof(t_shooter)),
    ("value_by_id", int32[:]),
    ("form_by_id", int32[:]),
    ("team_by_id", int32[:]),
    ("moves_by_id", nb.typeof(t_moves_by_id)),
    ("pieces_in_opponent_site", int32[:,:]),
    ("initial_number_of_real_pieces", int32),
    ("initial_number_of_pieces", int32),
]

spec = [
    ('board', int32[:, :]),
    ('turn', int32),
    ('player_turn', int32),
    ('width', int32),
    ('height', int32),
    ('stop', boolean),
    ('last_move', int32[:, :]),
    ('view', boolean),
    ('save_game', boolean),
    ('move_history', types.ListType(int32[:, :])),
    ('game_attacks', types.ListType(types.ListType(int32[:]))),
    ('locations', types.DictType(int32, int32[:])), 
    ('aim', types.DictType(int32, types.ListType(int32[:] ))),
    ('shooter', types.DictType(int32, types.ListType(int32[:] ))),
    ('value_by_id', int32[:]),
    ('form_by_id', int32[:]),
    ('team_by_id', int32[:]),
    ('moves_by_id', types.DictType(int32, types.DictType(int32, int32[:]))),
    ('pieces_in_opponent_site', int32[:, :]),
    ('iview', int32),
    ('winner', int32)
]




@jitclass(spec)
class Game:
    #fonctions d'évaluation, les pyramides sont comptées un peu double
    
    
    def piece_number(self):
        nbr_white = sum(map(lambda i:self.is_alive(i), WHITE_ID))
        nbr_pyr_white = sum(map(lambda i:self.is_alive(i), FAKE_ID_WHITE))

        nbr_black = sum(map(lambda i:self.is_alive(i), BLACK_ID))
        nbr_pyr_black = sum(map(lambda i:self.is_alive(i), FAKE_ID_BLACK))
        #return (nbr_white, nbr_pyr_white, nbr_black, nbr_pyr_black)
        return (nbr_white + nbr_pyr_white, nbr_black + nbr_pyr_black)
    

    
    def piece_rate(self):
        a,b = self.piece_number()
        return (a/30, b/29)


    
    def piece_sum(self):
        sum_white = sum(map(lambda i:self.value_by_id(i), WHITE_ID))
        sum_pyr_white = sum(map(lambda i:self.value_by_id(i), FAKE_ID_WHITE))

        sum_black = sum(map(lambda i:self.value_by_id(i), BLACK_ID))
        sum_pyr_black = sum(map(lambda i:self.value_by_id(i), FAKE_ID_BLACK))
        return (sum_white + sum_pyr_white, sum_black + sum_pyr_black)


    
    def isobarycenter(self, player):
        id_pawns = BLACK_ID if player else WHITE_ID
        x, y, n = 0, 0, 0
        for i in id_pawns:
            if self.is_alive(i):
                n=n+1
                y=self.locations[i][0] + y
                x=self.locations[i][1] + x
                
        return (y/n, x/n)
    def distance_center_to_isobary_center(self, player):
        mid_y, mid_x = (7.5, 3.5)
        y, x = self.isobarycenter(player)
        return(y-mid_y, x-mid_x)
    
    def dispersion(self, player):
        id_pawns = BLACK_ID if player else WHITE_ID
        ey, ex = self.isobarycenter(player)
        dx, dy, n = 0, 0, 0
        for i in id_pawns:
            if self.is_alive(i):
                n=n+1
                dy=(self.locations[i][0]-ey)**2 + dy
                dx=(self.locations[i][1]-ex)**2 + dx
        return (dy/n, dx/n)
    
    def progress(self, player):
        id_pawns = BLACK_ID if player else WHITE_ID
        repere =  0 if player else 15
        y, n = 0, 0
        #print("player", player)
        for i in id_pawns:
            if self.is_alive(i):
                #print(repere)
                #print(i, ":", abs(repere - self.locations[i][1]))
                n=n+1
                y= abs(repere - self.locations[i][0]) + y
        
        return y

    def get_delta_stats(self):

        white_pieces_rate, black_pieces_rate = self.piece_rate()
        (white_dispersion_y, white_dispersion_x), (black_dispersion_y, black_dispersion_x) = self.dispersion(0), self.dispersion(1)
        (white_dist_to_center_y, white_dist_to_center_x), (black_dist_to_center_y, black_dist_to_center_x) = self.distance_center_to_isobary_center(0), self.distance_center_to_isobary_center(1)
        white_progress, black_progress = self.progress(1), self.progress(0)
        return (white_pieces_rate - black_pieces_rate, 
                white_dispersion_y - black_dispersion_y,
                white_dispersion_x - black_dispersion_x,
                white_dist_to_center_y - black_dist_to_center_y,
                white_dist_to_center_x - black_dist_to_center_x,
                white_progress - black_progress)
    
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
        if nid in FAKE_ID_BLACK:
            nid = ID_BLACK_PYRAMID
        if nid in FAKE_ID_WHITE:
            nid = ID_WHITE_PYRAMID
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

        self.display = tk.Tk()
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

    def init_board(self):
        print("test")
        pre = "./boards/"
        with objmode():
            f = open(pre + "id_board.json", "r")
            data = loads(f.read())
            f.close()
 
            #self.board = np.array(data)
        
    # Vérifie si la position est bien dans le jeu
    def in_board(self, j, i):
        return 0 <= j < self.height and 0 <= i < self.width

    def set_board_empty(self, j, i):
        self.board[j][i] = -1

    def get_id_by_pos(self, y, x):
        return self.board[y][x]

    # Vérifie si une case est libre, sans pion
    def is_empty(self, j, i):
        return self.board[j][i] == -1


    # On récupère les mouvements réguliers, on doit vérifier que tout le trajet est libre
    def get_pawn_available_regular_moves(self, nid, j, i):
        available_moves = []
        if self.has_movement_of(nid, 1):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dj, di = rm
                if self.in_board(j + dj, i + di) and self.is_empty(j + dj, i + di):
                    available_moves += [((j, i), (dj, di))]

        if self.has_movement_of(nid, 2):
            r = 2
            # print(i, j)
            # print(np.equal(self.board[j-r:j, i], np.full((2, 3), -1)))
            # print(j, i)
            # print(self.in_board(j+r, i), self.in_board(j-r, i))
            # il y avait des 3 au lieu de length_of_data_pawn
            if self.in_board(j + r, i) and np.equal(self.board[j + 1:j + r + 1, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (r, 0))]
            if self.in_board(j - r, i) and np.equal(self.board[j - r:j, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (-r, 0))]
            if self.in_board(j, i + r) and np.equal(self.board[j, i + 1:i + r + 1],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (0, r))]
            if self.in_board(j, i - r) and np.equal(self.board[j, i - r:i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (0, -r))]

        if self.has_movement_of(nid, 3):
            r = 3
            if self.in_board(j + r, i) and np.equal(self.board[j + 1:j + r + 1, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (r, 0))]
            if self.in_board(j - r, i) and np.equal(self.board[j - r:j, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (-r, 0))]
            if self.in_board(j, i + r) and np.equal(self.board[j, i + 1:i + r + 1],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (0, r))]
            if self.in_board(j, i - r) and np.equal(self.board[j, i - r:i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                available_moves += [((j, i), (0, -r))]

        return available_moves

    def has_pawn_available_regular_moves(self, nid):
        (j, i) = self.locations[nid]
        if self.has_movement_of(nid, 1):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dj, di = rm
                if self.in_board(j + dj, i + di) and self.is_empty(j + dj, i + di):
                    return True

        if self.has_movement_of(nid, 2):
            r = 2
            # print(i, j)
            # print(np.equal(self.board[j-r:j, i], np.full((2, 3), -1)))
            # print(j, i)
            # print(self.in_board(j+r, i), self.in_board(j-r, i))
            # il y avait des 3 au lieu de length_of_data_pawn
            if self.in_board(j + r, i) and np.equal(self.board[j + 1:j + r + 1, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True
            if self.in_board(j - r, i) and np.equal(self.board[j - r:j, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True
            if self.in_board(j, i + r) and np.equal(self.board[j, i + 1:i + r + 1],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True
            if self.in_board(j, i - r) and np.equal(self.board[j, i - r:i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True

        if self.has_movement_of(nid, 3):
            r = 3
            if self.in_board(j + r, i) and np.equal(self.board[j + 1:j + r + 1, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True
            if self.in_board(j - r, i) and np.equal(self.board[j - r:j, i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True
            if self.in_board(j, i + r) and np.equal(self.board[j, i + 1:i + r + 1],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True
            if self.in_board(j, i - r) and np.equal(self.board[j, i - r:i],
                                                    np.full((r, length_of_data_pawn), -1)).all():
                return True

        return False

    # On récupère les mouvements irréguliers, juste à vérifier que la case finale est libre
    def get_pawn_available_irregular_moves(self, nid, j, i):
        available_moves = []
        
        for u in [-1, 1]:  # décalage de 1
            if self.has_movement_of(nid, 2):
                r = 2
                if self.in_board(j + r, i + u) and self.is_empty(j + r, i + u):
                    available_moves += [((j, i), (r, u))]
                if self.in_board(j - r, i + u) and self.is_empty(j - r, i + u):
                    available_moves += [((j, i), (-r, u))]
                if self.in_board(j + u, i + r) and self.is_empty(j + u, i + r):
                    available_moves += [((j, i), (u, r))]
                if self.in_board(j + u, i - r) and self.is_empty(j + u, i - r):
                    available_moves += [((j, i), (u, -r))]

            if self.has_movement_of(nid, 3):
                r = 3
                if self.in_board(j + r, i + u) and self.is_empty(j + r, i + u):
                    available_moves += [((j, i), (r, u))]
                if self.in_board(j - r, i + u) and self.is_empty(j - r, i + u):
                    available_moves += [((j, i), (-r, u))]
                if self.in_board(j + u, i + r) and self.is_empty(j + u, i + r):
                    available_moves += [((j, i), (u, r))]
                if self.in_board(j + u, i - r) and self.is_empty(j + u, i - r):
                    available_moves += [((j, i), (u, -r))]

        return available_moves
    
    def get_game_available_moves(self):
        available_moves = []  # 1 move = 2 couples (y, x)
        # pour toutes les cases non vides, on ajoute ses coups possibles dans la liste des coups
        
        ids = BLACK_ID if self.player_turn else WHITE_ID #Si c'est le joueur 1: blanc, sinon noir
        
        for i in ids:
            if not self.is_alive(i):
                continue
            (y, x) = self.locations[i]
            available_moves += self.get_pawn_available_regular_moves(i, y, x)
            available_moves += self.get_pawn_available_irregular_moves(i, y, x)
        
        return available_moves

    def update_fast_move(self, i):
        value = self.value_by_id[i]
        form = self.form_by_id[i]
        team = self.team_by_id[i]
        if self.is_alive(i):
            (y, x) = self.locations[i]
            self.fast_moves[i] = self.get_pawn_available_regular_moves((value, form, team, i), y, x) + self.get_pawn_available_irregular_moves((value, form, team, i), y, x)
        else:
            self.fast_moves[i] = []
    def init_fast_moves(self):
        for i in range(self.initial_number_of_real_pieces):
            self.update_fast_move(i)

    def update_fast_moves(self):
        ((old_y, old_x), (current_y, current_x)) = self.last_move
        neighbours = np.unique(self.get_pieces_to_check_for_siege(old_y, old_x) + self.get_pieces_to_check_for_siege(current_y, current_x) + self.board[current_y][current_x])
        for i in neighbours:
            if i < FIRST_FAKE_ID_WHITE:
                self.update_fast_move(i)

    def get_value_fast_moves(self):
        for i in range(self.initial_number_of_real_pieces):
            if i < FIRST_FAKE_ID_WHITE and self.is_alive(i):
                for coup in self.fast_moves[i]:
                    yield coup


    def is_alive(self, nid):
        return self.locations[nid] != -1

    # permet de déplacer une pièce
    def move_piece(self, rel_move):
        ((y, x), (dy, dx)) = rel_move
        nid = self.board[y][x]

        # Déplace la pièce
        self.board[y + dy][x + dx] = self.board[y][x]
        self.board[y][x] = -1
        # Enregistre le coup
        self.last_move = ((y, x), (y + dy, x + dx))
        if self.save_game:
            self.move_history.append(((y, x), (y + dy, x + dx)))

        # Met à jour pour aim/shooter
        self.locations[self.board[y + dy][x + dx]] = (y + dy, x + dx)  # je trouve ça fun comme ligne
        #print(y+dy, x+dx)
        self.moves_by_id[self.board[y + dy][x + dx]][self.turn] = (y + dy, x + dx)
        if nid == ID_WHITE_PYRAMID:
            for i in FAKE_ID_WHITE:
                if self.is_alive(i):
                    self.locations[i] = self.locations[ID_WHITE_PYRAMID]
        if nid == ID_BLACK_PYRAMID:
            for i in FAKE_ID_BLACK:
                if self.is_alive(i):
                    self.locations[i] = self.locations[ID_BLACK_PYRAMID]

        # Met à jour pour check_end
        if self.team_by_id[nid] == 0:
            # S’il est dans l’équipe blanche
            if y >= 8 and y + dy <= 7:
                # il vient de rentrer
                self.pieces_in_opponent_site[0].append(nid)

            if y <= 7 and y + dy >= 8:
                # il vient de sortir
                self.pieces_in_opponent_site[0].remove(nid)

        if self.team_by_id[nid] == 1:
            # S’il est dans l’équipe noire
            if y <= 7 and y + dy >= 8:
                # il vient de rentrer
                self.pieces_in_opponent_site[1].append(nid)

            if y >= 8 and y + dy <= 7:
                # il vient de sortir
                self.pieces_in_opponent_site[1].remove(nid)

    def end_turn(self):
        self.turn += 1
        self.player_turn = (self.player_turn + 1) % 2

    def kill(self, nid):
        if not self.is_alive(nid):
            return
        # si il est en vie
        if nid < FIRST_FAKE_ID_WHITE:
            # si c’est une attaque "totale"
            (y, x) = self.locations[nid]
            self.set_board_empty(y, x)
            for floor_n in self.develop_pyramid(nid):
                self.reset_links_of_pawn(floor_n)
                self.locations[floor_n] = -1
            self.moves_by_id[nid][self.turn] = (-1)
            # On la retire des pièces pouvant faire gagner
            for team in [0, 1]:
                if nid in self.pieces_in_opponent_site[team]:
                    self.pieces_in_opponent_site[team].remove(nid)
            return
        # si c’est une attaque partielle
        self.reset_links_of_pawn(nid)
        self.locations[nid] = -1

        if nid in FAKE_ID_WHITE:
            self.value_by_id[ID_WHITE_PYRAMID] -= self.value_by_id[nid]
            floor_pyramid_white = 0
            for i in FAKE_ID_WHITE:
                if self.is_alive(i):
                    floor_pyramid_white += 1
            if floor_pyramid_white == 0:
                self.kill(ID_WHITE_PYRAMID)
        if nid in FAKE_ID_BLACK:
            self.value_by_id[ID_BLACK_PYRAMID] -= self.value_by_id[nid]
            floor_pyramid_black = 0
            for i in FAKE_ID_BLACK:
                if self.is_alive(i):
                    floor_pyramid_black += 1
            if floor_pyramid_black == 0:
                self.kill(ID_BLACK_PYRAMID)

    def execute_all_attacks(self, attacks):
        for attack in attacks:
            (type_attack, attackers, attacked) = attack
            self.kill(attacked)

    def set_win(self, n, way):
        print("GAGNE", n)
        self.stop = True
        self.winner = n
        self.way_to_win = way

    def get_new_all_neighbours_id_with_directions(self, y, x, not_considered=None):
        if not_considered is None:
            not_considered = []
        neighbours = {}
        #
    
    def get_all_neighbours_id_with_directions(self, y, x, not_considered=None):
        if not_considered is None:
            not_considered = []
        neighbours = {}
        # for direction in ["s", "n", "o", "e", "no", "ne", "so", "se"]:
        #   neighbours[direction] = (-1, -1, -1)
        for ay in range(y + 1, 16):
            if not self.is_empty(ay, x) and (ay, x) not in not_considered:
                neighbours["s"] = self.board[ay][x]
                break
        for ay in range(y - 1, -1, -1):
            if not self.is_empty(ay, x) and (ay, x) not in not_considered:
                neighbours["n"] = self.board[ay][x]
                break
        for ax in range(x + 1, 8):
            if not self.is_empty(y, ax) and (y, ax) not in not_considered:
                neighbours["e"] = self.board[y][ax]
                break
        for ax in range(x - 1, -1, -1):
            if not self.is_empty(y, ax) and (y, ax) not in not_considered:
                neighbours["o"] = self.board[y][ax]
                break
        # UL
        for dt in range(1, 1 + min(x, y)):
            if not self.is_empty(y - dt, x - dt) and (y - dt, x - dt) not in not_considered:
                neighbours["no"] = self.board[y - dt][x - dt]
                break
        # UR
        for dt in range(1, 1 + min(7 - x, y)):
            if not self.is_empty(y - dt, x + dt) and (y - dt, x + dt) not in not_considered:
                neighbours["ne"] = self.board[y - dt][x + dt]
                break
        # DL
        for dt in range(1, 1 + min(x, 15 - y)):
            if not self.is_empty(y + dt, x - dt) and (y + dt, x - dt) not in not_considered:
                neighbours["so"] = self.board[y + dt][x - dt]
                break
        # DR
        for dt in range(1, 1 + min(7 - x, 15 - y)):
            if not self.is_empty(y + dt, x + dt) and (y + dt, x + dt) not in not_considered:
                neighbours["se"] = self.board[y + dt][x + dt]
                break
        return neighbours

    def get_all_pairs_neighbours_id_with_directions(self, y, x, not_considered=None):
        if not_considered is None:
            not_considered = []
        
        # for direction in ["s", "n", "o", "e", "no", "ne", "so", "se"]:
        #   neighbours[direction] = (-1, -1, -1)
        first = None
        has_first = False
        for ay in range(y + 1, 16):
            if not self.is_empty(ay, x) and (ay, x) not in not_considered:
                first = self.board[ay][x]
                has_first = True
                break
        if has_first:
            for ay in range(y - 1, -1, -1):
                if not self.is_empty(ay, x) and (ay, x) not in not_considered:
                    yield (first, self.board[ay][x])
                    break
                
        has_first = False        
        for ax in range(x + 1, 8):
            if not self.is_empty(y, ax) and (y, ax) not in not_considered:
                first = self.board[y][ax]
                has_first = True
                break
        
        if has_first:
            for ax in range(x - 1, -1, -1):
                if not self.is_empty(y, ax) and (y, ax) not in not_considered:
                    yield (first, self.board[y][ax])
                    break
        # UL
        has_first = False
        for dt in range(1, 1 + min(x, y)):
            if not self.is_empty(y - dt, x - dt) and (y - dt, x - dt) not in not_considered:
                first = self.board[y - dt][x - dt]
                has_first = True
                break
        # UR        
        if has_first:
            for dt in range(1, 1 + min(7 - x, y)):
                if not self.is_empty(y - dt, x + dt) and (y - dt, x + dt) not in not_considered:
                    yield (first, self.board[y - dt][x + dt])
                    break
        # DL
        has_first = False
        for dt in range(1, 1 + min(x, 15 - y)):
            if not self.is_empty(y + dt, x - dt) and (y + dt, x - dt) not in not_considered:
                first = self.board[y + dt][x - dt]
                has_first = True
                break
        # DR
        if has_first:
            for dt in range(1, 1 + min(7 - x, 15 - y)):
                if not self.is_empty(y + dt, x + dt) and (y + dt, x + dt) not in not_considered:
                    yield (first, self.board[y + dt][x + dt])


    def check_end(self):
        for team in [0, 1]:
            pieces_in_opponent_site = self.pieces_in_opponent_site[team]
            if len(pieces_in_opponent_site) > 2:
                for piece in pieces_in_opponent_site:
                    # faire des triangles ou ligne qui ne sont pas en diagonal
                    (y, x) = self.locations[piece]
                    neighbours = self.get_all_neighbours_id_with_directions(y, x)
                    available_neighbours = []

                    for direction in ["n", "s", "o", "e"]:
                        if not direction in neighbours:
                            continue
                        neighbour = neighbours[direction]
                        if neighbour in pieces_in_opponent_site:
                            available_neighbours.append(neighbour)
                    # print("voisins gardés: ", neighbours)


                    #print("Actual: ", piece)
                    #print("DEBUG: nei, ava", neighbours, available_neighbours)
                    #print("will test", self.couple_develop_pyramid(available_neighbours))

                    n = len(neighbours)
                    if n < 2:
                        continue
                    # print("ici")
                    value_piece = self.value_by_id[piece]
                    for ally1, ally2 in self.couple_develop_pyramid(available_neighbours):
                        # Toutes les combinaisons
                        value_ally1 = self.value_by_id[ally1]
                        value_ally2 = self.value_by_id[ally2]
                        #if self.winner != -1:
                            #print("test: ", ally1, ally2, ":", value_piece, value_ally1, value_ally2)

                        if get_progression(value_piece, value_ally1, value_ally2) > 0:
                            #print("NEWWWWWW Gagnant:", team, value_piece, value_ally1, value_ally2)
                            #print("Actual: ", piece)
                            #print("DEBUG: nei, ava", neighbours, available_neighbours)
                            #print("will test", self.couple_develop_pyramid(available_neighbours))
                            self.set_win(team, 0)
                            return

                    # En diagonale
                    for dir1, dir2 in [("no", "se"), ("ne", "so")]:
                        if not(dir1 in neighbours and dir2 in neighbours and neighbours[dir1] in pieces_in_opponent_site and neighbours[dir2] in pieces_in_opponent_site):
                            continue
                        #print("test diag", dir1, dir2, self.couple_develop_pyramid([neighbours[dir1], neighbours[dir2]]))
                        for ally1, ally2 in self.couple_develop_pyramid([neighbours[dir1], neighbours[dir2]]):
                            # Toutes les combinaisons
                            value_ally1 = self.value_by_id[ally1]
                            value_ally2 = self.value_by_id[ally2]
                            if get_progression(value_piece, value_ally1, value_ally2) > 0:
                                # print("NEWWWWWW Gagnant diagonal :", team, value_piece, value_ally1, value_ally2)
                                self.set_win(team, 1)
                                return

    def set_aim(self, nid: int, melee: list, ranged: list):
        self.aim[nid] = [melee, ranged]

    def reset_aim(self, nid):
        self.aim[nid] = [[], []]

    def add_melee_aim(self, nid: int, melee_id: int):
        self.aim[nid][0].append(melee_id)

    def add_ranged_aim(self, nid: int, ranged_id: int):
        self.aim[nid][1].append(ranged_id)

    def get_all_aim(self, nid: int):
        return self.aim[nid][0] + self.aim[nid][1]

    def get_melee_aim(self, nid: int):
        return self.aim[nid][0]

    def get_ranged_aim(self, nid: int):
        return self.aim[nid][1]

    def set_shooter(self, nid: int, melee: list, ranged: list):
        self.shooter[nid] = [melee, ranged]

    def reset_shooter(self, nid):
        self.shooter[nid] = [[], []]

    def add_melee_shooter(self, nid: int, melee_id: int):
        self.shooter[nid][0].append(melee_id)

    def add_ranged_shooter(self, nid: int, ranged_id: int):
        self.shooter[nid][1].append(ranged_id)

    def get_all_shooter(self, nid):
        # print("get all shooter:")
        # print(self.shooter[nid][0])
        # print(self.shooter[nid][1])
        # print(self.shooter[nid][0] + self.shooter[nid][1])
        return self.shooter[nid][0] + self.shooter[nid][1]

    def get_melee_shooter(self, nid):
        return self.shooter[nid][0]

    def get_ranged_shooter(self, nid):
        return self.shooter[nid][1]

    def remove_nid_from_mid_aim(self, nid, mid):
        # retire nid de la visée de mid
        if nid in self.aim[mid][0]:
            # print("remove ", nid, " from ", mid, " aim melee")
            self.aim[mid][0].remove(nid)
        if nid in self.aim[mid][1]:
            # print("remove ", nid, " from ", mid, " aim ranged")
            self.aim[mid][1].remove(nid)

    def remove_nid_from_mid_shooter(self, nid, mid):
        # retire nid comme attaquant mid
        if nid in self.shooter[mid][0]:
            # print("remove ", nid, " from ", mid, " shooter melee")
            self.shooter[mid][0].remove(nid)
        if nid in self.shooter[mid][1]:
            # print("remove ", nid, " from ", mid, " shooter ranged")
            self.shooter[mid][1].remove(nid)

    def set_attack_defense(self):
        # initialise le dictionnaire
        self.aim = {0: [[], []], 1: [[], []], 2: [[], []], 3: [[], []], 4: [[], []], 5: [[], []], 6: [[], []],
                    7: [[], []], 8: [[], []], 9: [[], []], 10: [[], []], 11: [[], []], 12: [[], []], 13: [[], [29]],
                    14: [[], []], 15: [[], []], 16: [[], []], 17: [[], []], 18: [[], []], 19: [[], []], 20: [[], []],
                    21: [[], []], 22: [[], []], 23: [[], []], 24: [[], []], 25: [[], []], 26: [[], []], 27: [[], []],
                    28: [[], []], 29: [[], [13]], 30: [[], []], 31: [[], []], 32: [[], []], 33: [[], []], 34: [[], []],
                    35: [[], []], 36: [[], []], 37: [[], []], 38: [[], []], 39: [[], []], 40: [[], []], 41: [[], []],
                    42: [[], []], 43: [[], []], 44: [[], []], 45: [[], []], 46: [[], []], 47: [[], []], 48: [[], []],
                    49: [[], []], 50: [[], []], 51: [[], []], 52: [[], []], 53: [[], []], 54: [[], []], 55: [[], []],
                    56: [[], []], 57: [[], []], 58: [[], []]}
        self.shooter = {0: [[], []], 1: [[], []], 2: [[], []], 3: [[], []], 4: [[], []], 5: [[], []], 6: [[], []],
                        7: [[], []], 8: [[], []], 9: [[], []], 10: [[], []], 11: [[], []], 12: [[], []], 13: [[], [29]],
                        14: [[], []], 15: [[], []], 16: [[], []], 17: [[], []], 18: [[], []], 19: [[], []],
                        20: [[], []], 21: [[], []], 22: [[], []], 23: [[], []], 24: [[], []], 25: [[], []],
                        26: [[], []], 27: [[], []], 28: [[], []], 29: [[], [13]], 30: [[], []], 31: [[], []],
                        32: [[], []], 33: [[], []], 34: [[], []], 35: [[], []], 36: [[], []], 37: [[], []],
                        38: [[], []], 39: [[], []], 40: [[], []], 41: [[], []], 42: [[], []], 43: [[], []],
                        44: [[], []], 45: [[], []], 46: [[], []], 47: [[], []], 48: [[], []], 49: [[], []],
                        50: [[], []], 51: [[], []], 52: [[], []], 53: [[], []], 54: [[], []], 55: [[], []],
                        56: [[], []], 57: [[], []], 58: [[], []]}

    def set_moves_by_id(self):
        for i in range(self.initial_number_of_real_pieces):
            self.moves_by_id[i] = {-1: self.locations[i]}

    def reset_links_of_pawn(self, nid):
        # doit modifier aim et targeted_by
        for aim in self.get_all_aim(nid):
            # n tire sur aim
            # donc aim est visé par n, ie n est un shooter de aim
            self.remove_nid_from_mid_shooter(nid, aim)
        # print("reset aim ", nid)
        self.reset_aim(nid)

        for shooter in self.get_all_shooter(nid):
            # print("reset shooter", nid, shooter, self.get_all_shooter(nid))
            # shooter tire sur n, du moins tirait
            self.remove_nid_from_mid_aim(nid, shooter)
        # print("reset shooter ", nid)
        self.reset_shooter(nid)

    def add_line(self, nid, mid):
        # c’est une ligne d’attaque, deux pièces vont maintenant "se voir"

        if self.team_by_id[nid] == self.team_by_id[mid]:
            return  # deux pièces d’une même équipe ne veulent pas se tuer

        (ny, nx) = self.locations[nid]
        (my, mx) = self.locations[mid]
        nvalue = self.value_by_id[nid]
        mvalue = self.value_by_id[mid]
        # print("continue add_line")
        dist = max(abs(ny - my), abs(nx - mx)) - 1  # espace entre les deux
        # print("dist ", dist, ny, nx, my, mx)
        if dist >= 2 and a_is_equation(mvalue, dist, nvalue):
            # print("attaque de loin", self.turn)
            # n attaque m de loin
            self.add_ranged_aim(nid, mid)
            self.add_ranged_shooter(mid, nid)

            # Donc m attaque n de loin
            self.add_ranged_aim(mid, nid)
            self.add_ranged_shooter(nid, mid)

        same_line_or_column = min(abs(ny - my), abs(nx - mx)) == 0
        # print("turn", self.turn, same_line_or_column)
        # on regarde si n attaque m en mêlée, puis si m attaque n en mêlée
        for aid, bid in [(nid, mid), (mid, nid)]:
            if self.has_movement_of(nid, 1):  # c’est un rond
                if (not same_line_or_column) and dist == 0:  # s’il attaque en vertical juste à côté de lui
                    self.add_melee_aim(aid, bid)
                    self.add_melee_shooter(bid, aid)
                    # print("melee ", aid, bid)

            if self.has_movement_of(nid, 2):
                if same_line_or_column and dist == 1:
                    self.add_melee_aim(aid, bid)
                    self.add_melee_shooter(bid, aid)
                    # print("melee ", aid, bid)

            if self.has_movement_of(nid, 3):
                if same_line_or_column and dist == 2:
                    self.add_melee_aim(aid, bid)
                    self.add_melee_shooter(bid, aid)
                    # print("melee ", aid, bid)

    def update_aim_shooter(self):
        #même fonctio nque update_aim_shooter, mais si il n'y a personne au nord, il ne va pas chercher ce qu'il y a au sud
        (old_y, old_x), (current_y, current_x) = self.last_move
        nid = self.board[current_y][current_x] # identifiant de la pièce déplacée
        # print("------------------------------------------")
        # print("Tour: ", self.turn)
        # print(self.aim)
        # print(self.shooter)
        # print("Début tour, pièce: ", nid)

        # !!! Dans toute cette partie de code, la pièce est déjà posée au nouvel endroit !!!

        # on considère la disparition de la pièce
        # elle n’est plus attaquée et n’attaque plus
        # print("-- 1 --")
        for floor_n in self.develop_pyramid(nid):
            self.reset_links_of_pawn(floor_n) #1000: + 1 sec

        # print("-- 2 --")
        # Puis, on ajoute les nouveaux voisins causés par la disparition de la pièce
        
        neighbours = self.get_all_pairs_neighbours_id_with_directions(old_y, old_x, not_considered=[(current_y, current_x)])

        # print(neighbours)
        for (a_id, b_id) in neighbours:
            
                # a et b peuvent être des pyramides
                for floor_a in self.develop_pyramid(a_id):
                    for floor_b in self.develop_pyramid(b_id):
                        self.add_line(floor_a, floor_b)
        # On considère l’arrivée de la pièce
        # les pièces nord-sud ne se touchent plus, etc...

        # print("-- 3 --")
        neighbours = self.get_all_neighbours_id_with_directions(current_y, current_x)
        for (d1, d2) in [("n", "s"), ("ne", "so"), ("e", "o"), ("se", "no")]:
            if d1 in neighbours and d2 in neighbours:
                aid = neighbours[d1]
                bid = neighbours[d2]
                for floor_a in self.develop_pyramid(aid):
                    for floor_b in self.develop_pyramid(bid):
                        self.remove_nid_from_mid_aim(floor_a, floor_b)
                        self.remove_nid_from_mid_aim(floor_b, floor_a)
                        self.remove_nid_from_mid_shooter(floor_a, floor_b)
                        self.remove_nid_from_mid_shooter(floor_b, floor_a)

        # Mais la pièce va toucher ses voisins

        # print("-- 4 --")
        for direction in ["n", "s", "e", "o", "ne", "no", "se", "so"]:
            if direction in neighbours:
                bid = neighbours[direction]

                for floor_n in self.develop_pyramid(nid):
                    for floor_b in self.develop_pyramid(bid):
                        self.add_line(floor_n, floor_b)

    def old_update_aim_shooter(self):
        (old_y, old_x), (current_y, current_x) = self.last_move
        nid = self.board[current_y][current_x] # identifiant de la pièce déplacée
        # print("------------------------------------------")
        # print("Tour: ", self.turn)
        # print(self.aim)
        # print(self.shooter)
        # print("Début tour, pièce: ", nid)

        # !!! Dans toute cette partie de code, la pièce est déjà posée au nouvel endroit !!!

        # on considère la disparition de la pièce
        # elle n’est plus attaquée et n’attaque plus
        # print("-- 1 --")
        for floor_n in self.develop_pyramid(nid):
            self.reset_links_of_pawn(floor_n) #1000: + 1 sec

        # print("-- 2 --")
        # Puis, on ajoute les nouveaux voisins causés par la disparition de la pièce
        
        neighbours = self.get_all_neighbours_id_with_directions(old_y, old_x, not_considered=[(current_y, current_x)])
        # print(neighbours)
        for (d1, d2) in [("n", "s"), ("ne", "so"), ("e", "o"), ("se", "no")]:
            if d1 in neighbours and d2 in neighbours:
                a_id = neighbours[d1]
                b_id = neighbours[d2]
                # a et b peuvent être des pyramides
                for floor_a in self.develop_pyramid(a_id):
                    for floor_b in self.develop_pyramid(b_id):
                        self.add_line(floor_a, floor_b)
        # On considère l’arrivée de la pièce
        # les pièces nord-sud ne se touchent plus, etc...

        # print("-- 3 --")
        neighbours = self.get_all_neighbours_id_with_directions(current_y, current_x)
        for (d1, d2) in [("n", "s"), ("ne", "so"), ("e", "o"), ("se", "no")]:
            if d1 in neighbours and d2 in neighbours:
                aid = neighbours[d1]
                bid = neighbours[d2]
                for floor_a in self.develop_pyramid(aid):
                    for floor_b in self.develop_pyramid(bid):
                        self.remove_nid_from_mid_aim(floor_a, floor_b)
                        self.remove_nid_from_mid_aim(floor_b, floor_a)
                        self.remove_nid_from_mid_shooter(floor_a, floor_b)
                        self.remove_nid_from_mid_shooter(floor_b, floor_a)

        # Mais la pièce va toucher ses voisins

        # print("-- 4 --")
        for direction in ["n", "s", "e", "o", "ne", "no", "se", "so"]:
            if direction in neighbours:
                bid = neighbours[direction]

                for floor_n in self.develop_pyramid(nid):
                    for floor_b in self.develop_pyramid(bid):
                        self.add_line(floor_n, floor_b)

    def set_locations(self):
        for y in range(16):
            for x in range(8):
                if not self.is_empty(y, x):
                    self.locations[self.board[y][x]] = (y, x)
        for i in FAKE_ID_BLACK:
            self.locations[i] = self.locations[ID_BLACK_PYRAMID]
        for i in FAKE_ID_WHITE:
            self.locations[i] = self.locations[ID_WHITE_PYRAMID]
        # print(self.locations)

    # en fait c’est nul ça, si la pyramide attaque ça ne veut pas dire que toutes les pièces attaquent
    def develop_pyramid(self, nid):
        # Argument : des identifiants
        # Sortie : les identifiants, et tous les identifiants de la pyramide si elle y est
        res = [nid]
        if ID_WHITE_PYRAMID == nid:
            for i in FAKE_ID_WHITE:
                if self.is_alive(i):
                    res.append(i)
        if ID_BLACK_PYRAMID == nid:
            for i in FAKE_ID_BLACK:
                if self.is_alive(i):
                    res.append(i)

        return res
    
    
    
    def develop_list_pyramid(self, pieces):
        res = []
        for piece in pieces:
            res += self.develop_pyramid(piece)
        return res    

    # à revoir, idée bonne mais même problème que la fonction au dessus
    def couple_develop_pyramid(self, id_pieces: list[int]):
        #if self.winner!=-1:
            # print("id_picees", id_pieces, self.develop_list_pyramid(id_pieces))
        id_pieces = self.develop_list_pyramid(id_pieces)  # on ne récupère que les étages dans le jeu
        for i in range(len(id_pieces)):
            for j in range(i):
                # il faut que ce soit deux pièces différentes (i!=j) ok
                # et que si i est une pyramide, j ne peut pas faire partie de la pyramide, si i est une partie de pyramide, j ne peut pas l’être
                # Rappel : ce sont des combinaisons ok
                piece_i = id_pieces[i]
                piece_j = id_pieces[j]
                if piece_i == ID_WHITE_PYRAMID and piece_j in FAKE_ID_WHITE:
                    continue
                if piece_j == ID_WHITE_PYRAMID and piece_i in FAKE_ID_WHITE:
                    continue
                if piece_i == ID_BLACK_PYRAMID and piece_j in FAKE_ID_BLACK:
                    continue
                if piece_j == ID_BLACK_PYRAMID and piece_i in FAKE_ID_BLACK:
                    continue
                if piece_j in FAKE_ID_BLACK and piece_i in FAKE_ID_BLACK:
                    continue
                if piece_j in FAKE_ID_WHITE and piece_i in FAKE_ID_WHITE:
                    continue
                yield (piece_i, piece_j)


    def get_attacks_with_aim_shooter(self): 
        #! Pas possible de yield ni set car il y a des listes à l'intérieur
        attacks = []
        # attaque de mêlée
        # attaque MEET et GALLOWS
        for n_piece in range(self.initial_number_of_pieces):
            if self.team_by_id[n_piece] == self.player_turn:
                continue
            # pour toutes les pièces et partie de pyramide
            if self.locations[n_piece] == -1:  # Si cette pièce est encore en jeu
                continue
            n_value = self.value_by_id[n_piece]
            melee_shooters = self.get_melee_shooter(n_piece)

            # MEET/GALLOWS
            for s in melee_shooters:
                s_value = self.value_by_id[s]
                if n_value == s_value:
                    attacks.append((TypeAttack.MEET, [s], n_piece))

                elif is_power_or_root(n_value, s_value):
                    attacks.append((TypeAttack.GALLOWS, [s], n_piece))

            # AMBUSH, PROGRESSION on prend tous les 2 parmis n
            for shooter_i, shooter_j in self.couple_develop_pyramid(melee_shooters):
                attack = a_is_equation(self.value_by_id[n_piece], self.value_by_id[shooter_i],
                                       self.value_by_id[shooter_j])
                if attack:
                    attacks.append((TypeAttack.AMBUSH, [shooter_i, shooter_j], n_piece))

                pro = get_progression(self.value_by_id[n_piece], self.value_by_id[shooter_i],
                                      self.value_by_id[shooter_j])
                if pro > 0:
                    if pro == 1:
                        attacks.append(
                            (TypeAttack.PROGRESSION_A, [shooter_i, shooter_j], n_piece))
                    if pro == 2:
                        attacks.append(
                            (TypeAttack.PROGRESSION_G, [shooter_i, shooter_j], n_piece))
                    if pro == 3:
                        attacks.append(
                            (TypeAttack.PROGRESSION_H, [shooter_i, shooter_j], n_piece))
            # ASSAULT
            for shooter_i in self.get_ranged_shooter(n_piece):
                attacks.append((TypeAttack.ASSAULT, [shooter_i], n_piece))
        return attacks
    
    

    def check_pyramid_has_form(self, nid, required_form):
        if nid == ID_WHITE_PYRAMID:
            first = FIRST_FAKE_ID_WHITE + required_form * 2
            second = first + 1
            return self.is_alive(first) or self.is_alive(second)

        if nid == ID_BLACK_PYRAMID:
            if required_form == 0:
                return self.is_alive(FIRST_FAKE_ID_BLACK)
            else:
                first = FIRST_FAKE_ID_WHITE + required_form * 2 - 1
                second = first + 1
                return self.is_alive(first) or self.is_alive(second)

    def has_movement_of(self, nid, required_form):
        form = self.form_by_id[nid]
        return form == required_form or (form == 4 and self.check_pyramid_has_form(nid, required_form))

    def get_pieces_to_check_for_siege(self, y, x):
            
            # for direction in ["s", "n", "o", "e", "no", "ne", "so", "se"]:
            #   neighbours[direction] = (-1, -1, -1)
            for ay in range(y + 1, min(y + 3 + 1, 16)):
                if not self.is_empty(ay, x):
                    # il y a une pièce
                    check_id = self.board[ay][x]
                    if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                        yield check_id
                    break
            for ay in range(y - 1, max(y - 3 - 1, -1), -1):
                if not self.is_empty(ay, x):
                    check_id = self.board[ay][x]
                    if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                        yield check_id
                    break
            for ax in range(x + 1, min(x + 3 + 1, 8)):
                if not self.is_empty(y, ax):
                    check_id = self.board[y][ax]
                    if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                        yield check_id
                    break
            for ax in range(x - 1, max(x - 3 - 1, -1), -1):
                if not self.is_empty(y, ax):
                    check_id = self.board[y][ax]
                    if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                        yield check_id
                    break
            # diag
            for dt in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
                dy, dx = dt
                if self.in_board(y + dy, x + dx) and not self.is_empty(y + dy, x + dx):
                    check_id = self.board[y + dy][x + dx]
                    if self.has_movement_of(check_id, 1):
                        yield check_id
    
    def detect_siege(self):
        attacks = []
        (_, _), (current_y, current_x) = self.last_move
        neighbours = self.get_pieces_to_check_for_siege(current_y, current_x)
        center_id = self.get_id_by_pos(current_y, current_x)
        team = self.team_by_id[center_id]

        for nid in neighbours:

            if team != self.team_by_id[nid] and not self.has_pawn_available_regular_moves(nid):
                attacks.append((TypeAttack.SIEGE, [center_id], nid))
        return attacks



    def __init__(self, view=False, auto = False):
        with objmode():
            self.start_time = time.time()
        self.board = []  #id
        self.init_board()

        self.turn = 0  # numéro du tour
        self.player_turn = 0  # numéro de celui à jouer
        self.width = 8
        self.height = 16
        # fake id: blanche: 37 on rajoute 48--53, noire: 11 on rajoute 54-58
        self.stop = False
        self.last_move = ((-1, -1), (-1, -1))
        self.view = view
        self.save_game = True
        self.move_history = []
        # game_attacks est toujours sauvegardé
        with objmode():
            self.game_attacks = []  # l’élément i représente l’ensemble des attaques après le coup i, une attaque est sous

        self.locations = {}  # Permet de connaître la position d’une pièce, -1 si elle n’existe plus
        self.aim = {}  # Optimisation, attack, pièce qu’elle attaque
        self.shooter = {}  # Optimisation, defense, pièce qui l’attaque

        self.value_by_id = np.array([49, 121, 225, 163, 28, 66, 36, 30, 59, 64, 120, 190, 16, 12, 9, 25, 49, 81, 90, 100, 3, 5, 7, 9, 8, 6, 4, 2,
         81, 72, 64, 36, 16, 4, 6, 9, 153, 91, 49, 42, 20, 25, 45, 15, 289, 169, 81, 25, 1, 4, 9, 16, 25, 36, 16, 25,
         36, 49, 64])
        self.form_by_id = np.array([3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 3, 4, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 3,
         4, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 1, 1, 2, 2, 3, 3, 1, 2, 2, 3, 3])
        self.team_by_id = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
        self.moves_by_id = {}
        self.pieces_in_opponent_site = [[], []]

        # print("direction", self.get_all_neighbours_with_directions(7, 4))

        # Ne considère que les mêlées
        self.initial_number_of_real_pieces = 48
        self.initial_number_of_pieces = 59
        self.set_locations()
        self.set_attack_defense()
        self.set_moves_by_id()
        # print(self.moves_by_id)
        # print(self.aim)
        # print(self.shooter)
        # la forme ([liste attaquant sous forme (ay, ax)], (y, x))
        self.iview = -1
        self.winner = -1
        # self.test_new_board()

        if SHOW_PRINT:
            print("Temps d\'initialisation :", time.time() - self.start_time)
        nbr_coups = 0

        #self.fast_moves = {}
        #self.init_fast_moves()
        if not auto:
            return
        self.max_turn = 2000
        for _ in range(0, self.max_turn):  # ne sert à rien de dépasser 2000
            if self.stop:
                break      
            
            coups =  self.get_game_available_moves()
            if len(coups) == 0:
                break
            coup = coups[random.randint(0, len(coups)-1)]
            self.play_move(coup)
            # print_board(self.board)
        self.is_finished = self.turn == self.max_turn
        if SHOW_PRINT:
            print(self.turn, self.max_turn)
            print(f"Finished: {self.is_finished}")
        if SHOW_PRINT:
            print("Fin en", self.turn, "tours")
        self.time_exe = time.time() - self.start_time
        
        print("Temps d\'exécution :", self.time_exe)
        if SHOW_PRINT:
            print("Coups joués ", self.turn)
            print("nbr_coups", nbr_coups / self.turn)
        if view:
            self.show_game()

    def play_move(self, move):
        #for i in range(1000):
        pre_aim_attacks = self.get_attacks_with_aim_shooter() # 1000 + 13s
        
        # print(j, len(coups))

        #value_fast_move = self.get_value_fast_moves()
        #if len(coups) != len(value_fast_move):
        #    print("ERROR", len(coups), len(value_fast_move))
        
        self.move_piece(move)
        #self.update_fast_moves()
        #for i in range(1000):
        self.update_aim_shooter()  # 1000 + 100 secondes (?)
        # self.detect_siege 1000 + 20s
        aim_attacks = self.get_attacks_with_aim_shooter() + self.detect_siege()

        available_aim_attacks = aim_attacks
        for no in pre_aim_attacks:
            if no in aim_attacks:
                available_aim_attacks.remove(no)
            
        # for i in available_aim_attacks:
        #    print("AIMSHOOTER detects ", self.turn, ": ", str(i))

        with objmode():
            self.game_attacks.append([])
            self.game_attacks[self.turn] = available_aim_attacks
        self.execute_all_attacks(available_aim_attacks)

        
        #for i in range(1000):
        self.check_end() # moyen, +100sec/1000 exe par boucle
        self.end_turn()


def find_win():
    while True:
        game = Game()
        if game.winner != -1:
            game.show_game()
            i = input("Another ?")
            if len(i) > 0:
                break


def launch_games(number, must_be_completed = False):
    c = 0
    for i in range(number):
        game = Game(auto=True)
        
        if must_be_completed:
            while not game.is_finished:
                game = Game(auto=True)
        c+=game.time_exe
    c/=number
    print(f"FINAL TIME: {c:.3}s")

if __name__ == "__main__":
    print("main.py")
    Game(auto=True).show_game()
    Game(auto=True).show_game()