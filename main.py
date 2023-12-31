import math
import tkinter as tk

import numpy as np
import json
import random
import time

from functools import partial
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from enums.type_attack import TypeAttack

width, height = (8, 16)

length_of_data_pawn = 1
ID_WHITE_PYRAMID = 37
ID_BLACK_PYRAMID = 11
FAKE_ID_WHITE = list(range(48, 53 + 1))
FIRST_FAKE_ID_WHITE = FAKE_ID_WHITE[0]
FAKE_ID_BLACK = list(range(54, 58 + 1))
FIRST_FAKE_ID_BLACK = FAKE_ID_BLACK[0]


def clear_file(f: str):
    with open(f + ".txt", "w"):
        pass


def print_file(f: str, args):
    arg = ""
    for a in args:
        arg += " " + str(a)
    with open(f + ".txt", "a") as file:
        file.write(arg + "\n")


def is_power_or_root(a, b):
    if a <= 0 or b <= 0:
        print("IS POWER OR ROOT ERROR", a, b)
        return
    if a == b:
        return True
    elif a == 1 or b == 1:
        return False
    return (math.log(b) / math.log(a)).is_integer() or (math.log(a) / math.log(b)).is_integer()


def a_is_equation(a, b, c):
    return a + b == c \
        or abs(a - b) == c \
        or a * b == c \
        or a / b == c \
        or b / a == c


def get_progression(a, b, c):
    t = [a, b, c]
    t.sort()
    u, v, w = t
    if 2 * v == u + w:
        print(f"aide: 2*{v} = {u}+{w}")
        return 1  # arithmétique
    if v * v == u * w:
        print(f"aide: {v}*{v} = {u}*{w}")
        return 2  # géométrique
    if v * (u + w) == 2 * u * w:
        print(f"aide: {v}*({u}+{w}) = 2*{u}*{w}")
        return 3  # harmonique
    return 0


class Game:

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
        if not self.view:
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
        self.canvas.delete("all")
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
                                        fill="WHITE", width=2)
            if form == 2:
                dp = np.array([(-20, 20), (20, 20), (0, -20)])
                points = (i * 50 + 25, j * 50 + 25) + dp
                self.canvas.create_polygon(points.flatten().tolist(), outline=color, fill="WHITE", width=2)
            if form == 3:
                self.canvas.create_rectangle(i * 50 + 5, j * 50 + 5, (i + 1) * 50 - 5, (j + 1) * 50 - 5,
                                             outline=color, fill="WHITE", width=2)

            if form <= 3:
                self.canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point) + "(" + str(nid) + ")")
            else:
                self.canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point) + "(" + str(nid) + ")",
                                        fill=color)
        # ligne
        for j in range(1, self.height):
            self.canvas.create_line(0, j * 50, self.width * 50, j * 50, fill="grey")
        for i in range(1, self.width):
            self.canvas.create_line(i * 50, 0, i * 50, self.height * 50, fill="grey")

        if time > 0:
            (y, x), (y2, x2) = self.move_history[time - 1]
            self.canvas.create_line(x * 50 + 25, y * 50 + 25, x2 * 50 + 25, y2 * 50 + 25, arrow=tk.LAST,
                                    fill="GREEN", width=2)
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
                print(attacks)
                for attacker in attackers:
                    n = attacker
                    (y, x) = self.get_location_at_time(n, time)
                    self.canvas.create_line(x * 50 + 25, y * 50 + 25, x2 * 50 + 25, y2 * 50 + 25, arrow=tk.LAST,
                                            fill=color_attack, width=2)

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
        if not self.view:
            return
        self.iview = self.turn

        self.display = tk.Tk()
        self.display.config(width=500, height=800)
        self.display.geometry("500x800")
        self.display.title('Grid')
        self.display.columnconfigure(0, weight=5)
        # self.display.columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(self.display, width=400, height=800, bg='#FFFFFF')
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
        pre = "./boards/"
        f = open(pre + "id_board.json", "r")
        self.board = np.array(json.loads(f.read()))
        f.close()

    # Vérifie si la position est bien dans le jeu
    def in_board(self, j, i):
        return 0 <= j < self.height and 0 <= i < self.width

    def set_board_empty(self, j, i):
        self.board[j][i] = -1

    def get_id_by_pos(self, y, x):
        return self.board[y][x]

    # Vérifie si une case est libre, sans pion
    def is_empty(self, j, i):
        return np.equal(self.board[j][i], -1).all()


    # On récupère les mouvements réguliers, on doit vérifier que tout le trajet est libre
    def get_pawn_available_regular_moves(self, pawn, j, i):
        available_moves = []
        (value, form, team, nid) = pawn
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
        form = self.form_by_id[nid]
        team = self.team_by_id[nid]
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
    def get_pawn_available_irregular_moves(self, pawn, j, i):
        available_moves = []
        (value, form, team, nid) = pawn
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

    # récupère tous les mouvements possibles dans un état
    # Pour chaque case, si elle n’est pas vide, on récupère les mouvements régulier et irrégulier
    def get_game_available_moves(self):
        available_moves = []  # 1 move = 2 couples (y, x)
        # pour toutes les cases non vides, on ajoute ses coups possibles dans la liste des coups
        for i in range(self.initial_number_of_real_pieces):
            if not self.is_alive(i):
                continue
            value = self.value_by_id[i]
            form = self.form_by_id[i]
            team = self.team_by_id[i]
            (y, x) = self.locations[i]
            if team == self.player_turn:
                available_moves += self.get_pawn_available_regular_moves((value, form, team, i), y, x)
                available_moves += self.get_pawn_available_irregular_moves((value, form, team, i), y, x)
        return available_moves

    def update_fast_move(self, i):
        value = self.value_by_id[i]
        form = self.form_by_id[i]
        team = self.team_by_id[i]
        (y, x) = self.locations[i]
        if team == self.player_turn:
            self.fast_moves[i] = self.get_pawn_available_regular_moves((value, form, team, i), y, x) + self.get_pawn_available_irregular_moves((value, form, team, i), y, x)

    def init_fast_moves(self):
        for i in range(self.initial_number_of_pieces):
            self.update_fast_move(i)

    def is_alive(self, nid):
        return self.locations[nid] != -1

    # permet de déplacer une pièce
    def move(self, rel_move):
        ((y, x), (dy, dx)) = rel_move
        nid = self.board[y][x]

        # Déplace la pièce
        self.board[y + dy][x + dx] = self.board[y][x]
        self.board[y][x] = -1
        # Enregistre le coup
        self.last_move = ((y, x), (y + dy, x + dx))
        if self.view:
            self.move_history.append(((y, x), (y + dy, x + dx)))

        # Met à jour pour aim/shooter
        self.locations[self.board[y + dy][x + dx]] = (y + dy, x + dx)  # je trouve ça fun comme ligne
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
            form = self.form_by_id[aid]
            team = self.team_by_id[aid]
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
            self.reset_links_of_pawn(floor_n)

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
        res = []
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
                res.append((piece_i, piece_j))
        return res

    def get_attacks_with_aim_shooter(self):
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
        pieces = []
        # for direction in ["s", "n", "o", "e", "no", "ne", "so", "se"]:
        #   neighbours[direction] = (-1, -1, -1)

        for ay in range(y + 1, min(y + 3 + 1, 16)):
            if not self.is_empty(ay, x):
                # il y a une pièce
                check_id = self.board[ay][x]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        for ay in range(y - 1, max(y - 3 - 1, -1), -1):
            if not self.is_empty(ay, x):
                check_id = self.board[ay][x]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        for ax in range(x + 1, min(x + 3 + 1, 8)):
            if not self.is_empty(y, ax):
                check_id = self.board[y][ax]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        for ax in range(x - 1, max(x - 3 - 1, -1), -1):
            if not self.is_empty(y, ax):
                check_id = self.board[y][ax]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        # diag
        for dt in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
            dy, dx = dt
            if self.in_board(y + dy, x + dx) and not self.is_empty(y + dy, x + dx):
                check_id = self.board[y + dy][x + dx]
                if self.has_movement_of(check_id, 1):
                    pieces.append(check_id)
        return pieces

    def detect_siege(self):
        attacks = []
        (old_y, old_x), (current_y, current_x) = self.last_move
        neighbours = self.get_pieces_to_check_for_siege(current_y, current_x)
        center_id = self.get_id_by_pos(current_y, current_x)
        team = self.team_by_id[center_id]

        for nid in neighbours:

            if team != self.team_by_id[nid] and not self.has_pawn_available_regular_moves(nid):
                attacks.append((TypeAttack.SIEGE, [center_id], nid))
        return attacks

    def __init__(self, view=False):
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
        self.move_history = []
        # game_attacks est toujours sauvegardé
        self.game_attacks = []  # l’élément i représente l’ensemble des attaques après le coup i, une attaque est sous

        self.locations = {}  # Permet de connaître la position d’une pièce, -1 si elle n’existe plus
        self.aim = {}  # Optimisation, attack, pièce qu’elle attaque
        self.shooter = {}  # Optimisation, defense, pièce qui l’attaque
        self.value_by_id = {0: 49, 1: 121, 2: 225, 3: 163, 4: 28, 5: 66, 6: 36, 7: 30, 8: 59, 9: 64, 10: 120, 11: 190,
                            12: 16, 13: 12,
                            14: 9, 15: 25, 16: 49, 17: 81, 18: 90, 19: 100, 20: 3, 21: 5, 22: 7, 23: 9, 24: 8, 25: 6,
                            26: 4, 27: 2, 28: 81,
                            29: 72, 30: 64, 31: 36, 32: 16, 33: 4, 34: 6, 35: 9, 36: 153, 37: 91, 38: 49, 39: 42,
                            40: 20, 41: 25, 42: 45,
                            43: 15, 44: 289, 45: 169, 46: 81, 47: 25, 48: 1, 49: 4, 50: 9, 51: 16, 52: 25, 53: 36,
                            54: 16, 55: 25, 56: 36,
                            57: 49, 58: 64}
        self.form_by_id = {0: 3, 1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 4, 12: 2, 13: 2,
                           14: 1, 15: 1, 16: 1,
                           17: 1, 18: 2, 19: 2, 20: 1, 21: 1, 22: 1, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 2, 29: 2,
                           30: 1, 31: 1, 32: 1,
                           33: 1, 34: 2, 35: 2, 36: 3, 37: 4, 38: 2, 39: 2, 40: 2, 41: 2, 42: 3, 43: 3, 44: 3, 45: 3,
                           46: 3, 47: 3, 48: 1,
                           49: 1, 50: 2, 51: 2, 52: 3, 53: 3, 54: 1, 55: 2, 56: 2, 57: 3, 58: 3}
        self.team_by_id = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1,
                           14: 1, 15: 1, 16: 1,
                           17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1, 23: 1, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0,
                           30: 0, 31: 0, 32: 0,
                           33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0,
                           46: 0, 47: 0, 48: 0,
                           49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 1, 55: 1, 56: 1, 57: 1, 58: 1}
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

        print(f'Temps d\'initialisation : {time.time() - self.start_time:.3}s')
        nbr_coups = 0

        self.fast_moves = {}
        self.init_fast_moves()
        for j in range(1, 1000):  # ne sert à rien de dépasser 2000
            if self.stop:
                break

            pre_aim_attacks = self.get_attacks_with_aim_shooter()  # assez rapide (100 execution par boucle, +1.5 sec)
            coups = self.get_game_available_moves()  # lent (100 execution par boucle, +110 sec) devenu moyen + 25 sec

            # print(j, len(coups))
            nbr_coups += len(coups)
            if len(coups) == 0:
                break
            coup = coups[random.randint(0, len(coups) - 1)]
            self.move(coup)

            self.update_aim_shooter()  # moyen (100 execution par boucle, +15 sec)
            # self.detect_siege assez apide (100 exectuions par boucle, +3 sec)
            aim_attacks = self.get_attacks_with_aim_shooter() + self.detect_siege()


            available_aim_attacks = aim_attacks
            for no in pre_aim_attacks:
                if no in aim_attacks:
                    available_aim_attacks.remove(no)
            # for i in available_aim_attacks:
            #    print("AIMSHOOTER detects ", self.turn, ": ", str(i))

            self.game_attacks.append([])
            self.game_attacks[self.turn] = available_aim_attacks
            self.execute_all_attacks(available_aim_attacks)


            self.check_end() # moyen, +10 sec/100 exe par boucle
            self.end_turn()

        # print_board(self.board)
        print("Fin en", self.turn, "tours")
        self.time_exe = time.time() - self.start_time
        print(f'Temps d\'exécution : {self.time_exe:.3}s')
        print("Coups joués ", j)
        print("nbr_coups", nbr_coups / self.turn)
        if view:
            self.show_game()


def find_win():
    while True:
        game = Game()
        if game.winner != -1:
            game.show_game()
            i = input("Another ?")
            if len(i) > 0:
                break


def launch_games(number):
    c = 0
    for i in range(number):
        game = Game()
        c+=game.time_exe
    c/=number
    print(f"FINAL TIME: {c:.3}s")


launch_games(1)