import math
import tkinter as tk
from io import BytesIO

from PIL import Image, ImageGrab
import numpy as np
import json
import random
import time

from functools import partial
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from enums.type_attack import TypeAttack

width, height = (8, 16)

length_of_data_pawn = 4
ID_WHITE_PYRAMID = 37
ID_BLACK_PYRAMID = 11
FAKE_ID_WHITE = list(range(48, 53 + 1))
FIRST_FAKE_ID_WHITE = FAKE_ID_WHITE[0]
FAKE_ID_BLACK = list(range(54, 58 + 1))
FIRST_FAKE_ID_BLACK = FAKE_ID_BLACK[0]


def print_board(board):
    board = board.tolist()
    for y in range(16):
        print(y, board[y], ",")


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


def add_attacks(l1: list, l2: list, p: (list, list)):
    p1, p2 = p
    return l1 + p1, l2 + p2


class Game:

    def test_new_board(self):
        for y in range(16):
            for x in range(8):
                nid = self.board[y][x][3]
                if nid == -1:
                    continue

                print("Pièce:", nid)
                if self.board[y][x][0] == self.value_by_id[nid]:
                    print("value ok")
                else:
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                if self.board[y][x][1] == self.form_by_id[nid]:
                    print("form ok")
                else:
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                if self.board[y][x][2] == self.team_by_id[nid]:
                    print("team ok")
                else:
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")
                    print("NOOOOOOOOOOOOOOON")

    def update_view(self):
        self.init_view(self.game_history[self.iview])

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

    def old_take_photo(self):

        self.canvas.update()
        # Get the EPS corresponding to the canvas
        eps = self.canvas.postscript(colormode='color')

        # Save canvas as "in-memory" EPS and pass to PIL without writing to disk
        im = Image.open(BytesIO(bytes(eps, 'ascii')))
        im.save('result.png')

    def take_photo(self):
        ImageGrab.grab(bbox=(
            self.canvas.winfo_rootx(),
            self.canvas.winfo_rooty(),
            self.canvas.winfo_rootx() + self.canvas.winfo_width(),
            self.canvas.winfo_rooty() + self.canvas.winfo_height()
        )).save("TEST.png")

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

        # if key == KeyCode.from_char("z"):
        #   self.old_take_photo()

    def init_view(self, board):
        self.canvas.delete("all")
        for i in range(self.width):
            for j in range(self.height):
                if not self.is_empty_specific_board(board, j, i):
                    (point, form, team, nid) = board[j][i]
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

        if self.iview > 0:
            (y, x), (y2, x2) = self.move_history[self.iview - 1]
            self.canvas.create_line(x * 50 + 25, y * 50 + 25, x2 * 50 + 25, y2 * 50 + 25, arrow=tk.LAST,
                                    fill="GREEN", width=2)
            for attacks in self.game_attacks[self.iview - 1]:
                (type_attack, attackers, attacked) = attacks
                y2, x2, n2 = attacked
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
                for attacker in attackers:
                    y, x, n = attacker
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
                (y, x, n) = attacked
                # print("attaqué init_frame", i, attacked)
                # print("affiché", self.game_history[i-1][y][x])
                if self.game_history[i - 1][y][x][1] == 4:
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
        self.init_view(self.board)
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
        f = open(pre + "game.json", "r")
        self.board = np.array(json.loads(f.read()))
        f.close()

    # Vérifie si la position est bien dans le jeu
    def in_board(self, j, i):
        return 0 <= j < self.height and 0 <= i < self.width

    def set_board_empty(self, j, i):
        self.board[j][i] = [-1, -1, -1, -1]

    def get_id_by_pos(self, y, x):
        return self.board[y][x][3]

    # Vérifie si une case est libre, sans pion
    def is_empty(self, j, i):
        return np.equal(self.board[j][i], [-1, -1, -1, -1]).all()

    @staticmethod
    def is_empty_specific_board(board, j, i):
        return np.equal(board[j][i], [-1, -1, -1, -1]).all()

    # On récupère les mouvements réguliers, on doit vérifier que tout le trajet est libre
    def get_pawn_available_regular_moves(self, pawn, j, i):
        available_moves = []
        (value, form, team, nid) = pawn
        if form == 1 or (form == 4 and self.check_pyramid_form(team, 1)):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dj, di = rm
                if self.in_board(j + dj, i + di) and self.is_empty(j + dj, i + di):
                    available_moves += [((j, i), (dj, di))]

        if form == 2 or (form == 4 and self.check_pyramid_form(team, 2)):
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

        if form == 3 or (form == 4 and self.check_pyramid_form(team, 3)):
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
        if form == 1 or (form == 4 and self.check_pyramid_form(team, 1)):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dj, di = rm
                if self.in_board(j + dj, i + di) and self.is_empty(j + dj, i + di):
                    return True

        if form == 2 or (form == 4 and self.check_pyramid_form(team, 2)):
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

        if form == 3 or (form == 4 and self.check_pyramid_form(team, 3)):
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
            if form == 2 or (form == 4 and self.check_pyramid_form(team, 2)):
                r = 2
                if self.in_board(j + r, i + u) and self.is_empty(j + r, i + u):
                    available_moves += [((j, i), (r, u))]
                if self.in_board(j - r, i + u) and self.is_empty(j - r, i + u):
                    available_moves += [((j, i), (-r, u))]
                if self.in_board(j + u, i + r) and self.is_empty(j + u, i + r):
                    available_moves += [((j, i), (u, r))]
                if self.in_board(j + u, i - r) and self.is_empty(j + u, i - r):
                    available_moves += [((j, i), (u, -r))]

            if form == 3 or (form == 4 and self.check_pyramid_form(team, 3)):
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
        for y in range(16):
            for x in range(8):
                if self.is_empty(y, x):
                    continue
                (value, form, team, nid) = self.board[y][x]
                if team == self.player_turn:
                    available_moves += self.get_pawn_available_regular_moves((value, form, team, nid), y, x)
                    available_moves += self.get_pawn_available_irregular_moves((value, form, team, nid), y, x)
        return available_moves

    def is_alive(self, nid):
        return self.locations[nid] != -1

    # permet de déplacer une pièce
    def move(self, rel_move):
        ((y, x), (dy, dx)) = rel_move
        nid = self.board[y][x][3]
        self.board[y + dy][x + dx] = self.board[y][x]
        self.board[y][x] = (-1, -1, -1, -1)
        self.last_move = ((y, x), (y + dy, x + dx))
        if self.view:
            self.move_history.append(((y, x), (y + dy, x + dx)))

        self.locations[self.board[y + dy][x + dx][3]] = (y + dy, x + dx)  # je trouve ça fun comme ligne
        if nid == ID_WHITE_PYRAMID:
            for i in FAKE_ID_WHITE:
                if self.is_alive(i):
                    self.locations[i] = self.locations[ID_WHITE_PYRAMID]
        if nid == ID_BLACK_PYRAMID:
            for i in FAKE_ID_BLACK:
                if self.is_alive(i):
                    self.locations[i] = self.locations[ID_BLACK_PYRAMID]

    def end_turn(self):
        self.turn += 1
        self.player_turn = (self.player_turn + 1) % 2
        if self.view:
            self.game_history.append(self.board.copy())

    # copier-coller de get_pawn_available_moves mais on veut un pion dans les coins
    def get_pawn_melee_attacks(self, pawn, j, i):
        available_attacks = []
        (value, form, team) = pawn
        if form == 1 or (form == 4 and (self.pyramid[team][0] != -1 or self.pyramid[team][1] != -1)):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dj, di = rm
                if self.in_board(j + dj, i + di) and not self.is_empty(j + dj, i + di) \
                        and self.board[j + dj][i + di][2] != self.player_turn:  # ici on inverse
                    available_attacks += [(j + dj, i + di)]

        if form == 2 or (form == 4 and (self.pyramid[team][2] != -1 or self.pyramid[team][3] != -1)):
            range = 2
            space = range - 1  # j’enlève 1 à chaque fois et on vérifie qu’il y a bien quelque chose en "r+1"
            if self.in_board(j + range, i) \
                    and np.equal(self.board[j + 1:j + space + 1, i], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j + range, i)) \
                    and self.board[j + range][i][2] != self.player_turn:
                available_attacks += [(j + range, i)]

            if self.in_board(j - range, i) \
                    and np.equal(self.board[j - space:j, i], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j - range, i)) \
                    and self.board[j - range][i][2] != self.player_turn:
                available_attacks += [(j - range, i)]

            if self.in_board(j, i + range) \
                    and np.equal(self.board[j, i + 1:i + space + 1], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j, i + range)) \
                    and self.board[j][i + range][2] != self.player_turn:
                available_attacks += [(j, i + range)]

            if self.in_board(j, i - range) \
                    and np.equal(self.board[j, i - space:i], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j, i - range)) \
                    and self.board[j][i - range][2] != self.player_turn:
                available_attacks += [(j, i - range)]

        if form == 3 or (form == 4 and (self.pyramid[team][4] != -1 or self.pyramid[team][5] != -1)):
            range = 3
            space = range - 1
            if self.in_board(j + range, i) \
                    and np.equal(self.board[j + 1:j + space + 1, i], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j + range, i)) \
                    and self.board[j + range][i][2] != self.player_turn:
                available_attacks += [(j + range, i)]

            if self.in_board(j - range, i) \
                    and np.equal(self.board[j - space:j, i], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j - range, i)) \
                    and self.board[j - range][i][2] != self.player_turn:
                available_attacks += [(j - range, i)]

            if self.in_board(j, i + range) \
                    and np.equal(self.board[j, i + 1:i + space + 1], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j, i + range)) \
                    and self.board[j][i + range][2] != self.player_turn:
                available_attacks += [(j, i + range)]

            if self.in_board(j, i - range) \
                    and np.equal(self.board[j, i - space:i], np.full((space, length_of_data_pawn), -1)).all() \
                    and (not self.is_empty(j, i - range)) \
                    and self.board[j][i - range][2] != self.player_turn:
                available_attacks += [(j, i - range)]

        return available_attacks

    def get_melee_attack_board(self):
        attack_board = np.full((16, 8), list)
        for y in range(16):
            for x in range(8):
                attack_board[y][x] = []
        for y in range(16):
            for x in range(8):
                if self.is_empty(y, x):
                    continue
                (value, form, team, nid) = self.board[y][x]
                if team != self.player_turn:
                    continue
                for attack in self.get_pawn_melee_attacks((value, form, team), y, x):
                    # print("attack", attack, value)
                    attack_board[attack[0]][attack[1]].append((y, x, value))

        return attack_board

    # Gère les attaques et attaques partielles sur une pyramide
    # renvois les attaques de a et b sur la case de coordonnée (y, x)
    def equations_attacks(self, y, x, a: int,
                          b: int):  # a et b sont des pseudos-attaquants, utilisé lors d’attaque en assaut
        attacks = []
        if a_is_equation(self.board[y][x][0], a, b):
            attacks.append((y, x, self.board[y][x][0]))
        if self.board[y][x][1] == 4:  # le retour de l’ennui
            for n in self.pyramid[1 - self.player_turn]:  # si elle appartient à l’ennemi
                if n == -1:
                    continue
                if a_is_equation(n, a, b):
                    attacks.append((y, x, n))
        return attacks

    def equations_attacks_on(self, pos: (int, int), a: int,
                             b: int):  # a et b sont des pseudos-attaquants, utilisé lors d’attaque en assaut
        attacks = []
        y, x = pos
        if a_is_equation(self.board[y][x][0], a, b):
            attacks.append((y, x, self.board[y][x][0]))
        if self.board[y][x][1] == 4:  # le retour de l’ennui
            for n in self.pyramid[1 - self.player_turn]:  # si elle appartient à l’ennemi
                if n == -1:
                    continue
                if a_is_equation(n, a, b):
                    attacks.append((y, x, n))
        return attacks

    def progression_attacks(self, y, x, a: int, b: int):  # même idée que précédent
        attacks = []
        progression = get_progression(self.board[y][x][0], a, b)
        if progression > 0:
            # print("PROGRESSION", self.board[y][x][0], a, b, self.turn)
            attacks.append((y, x, self.board[y][x][0], progression))
        if self.board[y][x][1] == 4:  # le retour de l’ennui
            for n in self.pyramid[1 - self.player_turn]:  # si elle appartient à l’ennemi
                if n == -1:
                    continue
                pro = get_progression(n, a, b)
                if pro > 0:
                    # print("PROGRESSION", pro, n, a, b, self.turn)
                    attacks.append((y, x, n, pro))
        return attacks

    def get_melee_attacks(self, attacks):
        attack_board = self.get_melee_attack_board()

        for y in range(16):
            for x in range(8):
                attackers = attack_board[y][x]
                # Rencontre et puissance
                for a in attackers:
                    (ay, ax, an) = a
                    # print("wtf", an, self.board[y][x][0])
                    if self.board[y][x][0] == an:  # Rencontre
                        # print("Append met:", str((TypeAttack.MEET, [a], (y, x, self.board[y][x][0]))))
                        attacks.append((TypeAttack.MEET, [a], (y, x, self.board[y][x][0])))
                    elif is_power_or_root(self.board[y][x][0], an):  # Potence

                        # print("Append pot:", str((TypeAttack.MEET, [a], (y, x, self.board[y][x][0]))))
                        attacks.append((TypeAttack.GALLOWS, [a], (y, x, self.board[y][x][0])))

                # Embuscade et progression
                for i in range(len(attackers)):
                    for j in range(i):
                        ai = attackers[i]
                        aj = attackers[j]

                        equation_attacks = self.equations_attacks(y, x, ai[2], aj[2])
                        for ea in equation_attacks:
                            # print("Append emb:", str((TypeAttack.AMBUSH, [attackers[i], attackers[j]], ea)))
                            attacks.append((TypeAttack.AMBUSH, [attackers[i], attackers[j]], ea))

                        progression_attacks = self.progression_attacks(y, x, ai[2], aj[2])
                        for pa in progression_attacks:
                            (y, x, n, pro) = pa
                            if pro == 1:
                                attacks.append((TypeAttack.PROGRESSION_A, [attackers[i], attackers[j]], (y, x, n)))
                            if pro == 2:
                                attacks.append((TypeAttack.PROGRESSION_G, [attackers[i], attackers[j]], (y, x, n)))
                            if pro == 3:
                                attacks.append((TypeAttack.PROGRESSION_H, [attackers[i], attackers[j]], (y, x, n)))

    def get_assault_attacks(self, attacks):
        # Il y aurait moyen de réduire un peu la taille avec fonction auxiliaire, pas sûr...
        # en ligne, en colonne, ou en diagonale
        # print("-------------------")
        # 1. en ligne
        for y in range(16):
            none = [-1, -1, -1]
            last_piece = none
            last_x, last_y = -1, -1
            espace = 0
            # on note le dernier emplacement d’une pièce
            for x in range(8):
                if self.is_empty(y, x):
                    espace += 1
                    continue
                if np.equal(last_piece, none).all():  # si c’est la première, on initialise
                    last_y = y
                    last_x = x
                    espace = 0
                    continue
                # Dans ce cas, les deux pieces peuvent se toucher, de longueur i
                # On vérifie si un de l’équipe qui joue, peut battre l’autre
                # on l’attaque avec la pièce à nous et la distance qui les sépare
                if espace > 1:
                    if last_piece[2] == self.player_turn and self.board[y][x][2] != self.player_turn:
                        equation_attacks = self.equations_attacks_on((y, x), last_piece[0], espace)
                        for ea in equation_attacks:
                            # c’est la pièce actuelle qui est attaquée
                            # print("Append assault:", str((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea)))
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, self.board[last_y][last_x][0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        # c’est last_piece qui est attaqué
                        equation_attacks = self.equations_attacks_on((last_y, last_x), self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, self.board[y][x][0])], ea))
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0
        # 2. en colonne (*on échange juste l’initialisation de x et y*)
        for x in range(8):
            none = [-1, -1, -1, -1]
            last_piece = none
            last_x, last_y = -1, -1
            espace = 0
            for y in range(16):
                if self.is_empty(y, x):
                    espace += 1
                    continue
                if np.equal(last_piece, none).all():
                    last_piece = self.board[y][x]
                    last_y = y
                    last_x = x
                    espace = 0
                    continue
                if espace > 1:
                    if last_piece[2] == self.player_turn and self.board[y][x][2] != self.player_turn:
                        equation_attacks = self.equations_attacks_on((y, x), last_piece[0], espace)
                        for ea in equation_attacks:
                            # c’est la pièce actuelle qui est attaquée
                            # print("Append assault:", str((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea)))
                            # print("dif", self.board[last_y][last_x], last_piece)
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, self.board[last_y][last_x][0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        # c’est last_piece qui est attaqué
                        equation_attacks = self.equations_attacks_on((last_y, last_x), self.board[y][x][0], espace)
                        # print("dif", self.board[last_y][last_x], last_piece)
                        for ea in equation_attacks:
                            # print("2Append assault:", str((TypeAttack.ASSAULT, [(y, x, self.board[y][x][0])], ea)))
                            attacks.append((TypeAttack.ASSAULT, [(y, x, self.board[y][x][0])], ea))

                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0

        # 3 diagonale descendante
        for debut_ligne in range(-6, 15):
            none = [-1, -1, -1, -1]
            last_piece = none
            last_x, last_y = -1, -1
            espace = 0
            for i in range(8):
                y = debut_ligne + i
                x = i
                if not self.in_board(y, x):
                    continue
                if self.is_empty(y, x):
                    espace += 1
                    continue
                if np.equal(last_piece, none).all():
                    last_piece = self.board[y][x]
                    last_y = y
                    last_x = x
                    espace = 0
                    continue
                if espace > 1:
                    if last_piece[2] == self.player_turn and self.board[y][x][2] != self.player_turn:
                        equation_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, self.board[last_y][last_x][0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equation_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, self.board[y][x][0])], ea))
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0
        # 4 diagonale ascendante
        for debut_ligne in range(1, 22):
            none = [-1, -1, -1, -1]
            last_piece = none
            last_x, last_y = -1, -1
            espace = 0
            for i in range(8):
                y = debut_ligne - i
                x = i
                if not self.in_board(y, x):
                    continue
                if self.is_empty(y, x):
                    espace += 1
                    continue
                if np.equal(last_piece, none).all():
                    last_piece = self.board[y][x]
                    last_y = y
                    last_x = x
                    espace = 0
                    continue
                if espace > 1:
                    if last_piece[2] == self.player_turn and self.board[y][x][2] != self.player_turn:
                        equation_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, self.board[last_y][last_x][0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equation_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, self.board[y][x][0])], ea))
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0

    def check_pyramid_form(self, team, form):
        if form == 1:
            return self.pyramid[team][0] != -1 or self.pyramid[team][1] != -1
        if form == 2:
            return self.pyramid[team][2] != -1 or self.pyramid[team][3] != -1
        if form == 3:
            return self.pyramid[team][4] != -1 or self.pyramid[team][5] != -1

    def is_blocked_by_last_move(self, y, x):
        # print("test", y, x)
        (value, form, team, nid) = self.board[y][x]
        last_y, last_x = self.last_move[1]
        # print("last move", last_y, last_x)
        if form == 1 or (form == 4 and self.check_pyramid_form(team, 1)):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dy, dx = rm
                if y + dy == last_y and x + dx == last_x:
                    return True  # il a bien boucher un bout
        for r in range(2, 4):
            if form == r or (form == 4 and self.check_pyramid_form(team, r)):
                if last_y == y and abs(last_x - x) <= r:
                    # il pourrait boucher quelque chose
                    if x > last_x:
                        for delta in range(1, r + 1):
                            if not self.in_board(y, x - delta):
                                break
                            # print("-->test21", y, delta, last_y)
                            if self.is_empty(y, x - delta):
                                continue
                            if x - delta == last_x:
                                return True
                            # print("nop")
                            break
                    if x < last_x:
                        for delta in range(1, r + 1):
                            if not self.in_board(y, x + delta):
                                break

                            # print("-->test22", y, delta, last_y)
                            if self.is_empty(y, x + delta):
                                continue
                            if x + delta == last_x:
                                return True
                            # print("nop")
                            break
                if last_x == x and abs(last_y - y) <= r:
                    if y > last_y:
                        for delta in range(1, r + 1):

                            if not self.in_board(y - delta, x):
                                break
                            # print("-->test23", y, delta, last_y)
                            if self.is_empty(y - delta, x):
                                continue
                            if y - delta == last_y:
                                return True
                            # print("nop")
                            break
                    if y < last_y:
                        for delta in range(1, r + 1):
                            if not self.in_board(y + delta, x):
                                break
                            # print("-->test24", y, delta, last_y)
                            if self.is_empty(y + delta, x):
                                continue
                            if y + delta == last_y:
                                return True
                            # print("nop")
                            break
        return False

    def get_siege_attacks(self, attacks):
        last_y, last_x = self.last_move[1]
        team_last_move = self.board[last_y][last_x][2]
        for y in range(last_y - 3, last_y + 4):
            for x in range(last_x - 3, last_x + 4):
                if (not self.in_board(y, x)) or self.is_empty(y, x):
                    continue
                if self.board[y][x][2] == team_last_move:
                    continue  # deux pions d’une même équipe évitent de se buter
                moves = self.get_pawn_available_regular_moves(self.board[y][x], y, x)
                if len(moves) == 0:
                    if self.is_blocked_by_last_move(y, x):
                        attacks.append((TypeAttack.SIEGE, [(last_y, last_x, self.board[last_y][last_x][0])],
                                        (y, x, self.board[y][x][0])))

    def get_game_attacks(self):

        attacks = []
        self.get_melee_attacks(attacks)
        self.get_assault_attacks(attacks)
        self.get_siege_attacks(attacks)
        return attacks

    def kill(self, nid):
        if not self.is_alive(nid):
            return
        #si il est en vie
        if nid < FIRST_FAKE_ID_WHITE:
            #si c’est une attaque "totale"
            (y, x) = self.locations[nid]
            self.set_board_empty(y, x)
            for floor_n in self.develop_pyramid(nid):
                self.reset_links_of_pawn(floor_n)
                self.locations[floor_n] = -1
            return
        #si c’est une attaque partielle
        self.reset_links_of_pawn(nid)
        self.locations[nid] = -1

        if nid in FAKE_ID_WHITE:
            self.value_by_id[FAKE_ID_WHITE] -= self.value_by_id[nid]
            floor_pyramid_white = 0
            for i in FAKE_ID_WHITE:
                if self.is_alive(i):
                    floor_pyramid_white += 1
            if floor_pyramid_white == 0:
                self.kill(ID_WHITE_PYRAMID)
        if nid in FAKE_ID_BLACK:
            self.value_by_id[FAKE_ID_BLACK] -= self.value_by_id[FAKE_ID_BLACK]
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

    def set_win(self, n):
        print("GAGNE", n)
        self.stop = True
        self.winner = n

    # ** get_pawn_neighbours
    def get_line_and_column_pawn_neighbours(self, y, x):
        neighbours = []
        for ay in range(y + 1, 16):
            if not self.is_empty(ay, x):
                neighbours.append((ay, x, self.board[ay][x]))
                break
        for ay in range(y - 1, -1, -1):
            if not self.is_empty(ay, x):
                neighbours.append((ay, x, self.board[ay][x]))
                break
        for ax in range(x + 1, 8):
            if not self.is_empty(y, ax):
                neighbours.append((y, ax, self.board[y][ax]))
                break
        for ax in range(x - 1, -1, -1):
            if not self.is_empty(y, ax):
                neighbours.append((y, ax, self.board[y][ax]))
                break
        # print("voisins", y, x, neighbours)
        return neighbours

    # **get_diagonal_pawn_neighbours
    def get_diagonal_pawn_neighbours(self, y, x):
        neighbours = []
        # UL
        for dt in range(1, 1 + min(x, y)):
            if not self.is_empty(y - dt, x - dt):
                neighbours.append((y - dt, x - dt, self.board[y - dt][x - dt]))
                break
        # UR
        for dt in range(1, 1 + min(7 - x, y)):
            if not self.is_empty(y - dt, x + dt):
                neighbours.append((y - dt, x + dt, self.board[y - dt][x + dt]))
                break
        # DL
        for dt in range(1, 1 + min(x, 15 - y)):
            if not self.is_empty(y + dt, x - dt):
                neighbours.append((y + dt, x - dt, self.board[y + dt][x - dt]))
                break
        # DR
        for dt in range(1, 1 + min(7 - x, 15 - y)):
            if not self.is_empty(y + dt, x + dt):
                neighbours.append((y + dt, x + dt, self.board[y + dt][x + dt]))
                break
        return neighbours

    def get_all_neighbours_id_with_directions(self, y, x, not_considered=None):
        if not_considered is None:
            not_considered = []
        neighbours = {}
        # for direction in ["s", "n", "o", "e", "no", "ne", "so", "se"]:
        #   neighbours[direction] = (-1, -1, -1)
        for ay in range(y + 1, 16):
            if not self.is_empty(ay, x) and (ay, x) not in not_considered:
                neighbours["s"] = self.board[ay][x][3]
                break
        for ay in range(y - 1, -1, -1):
            if not self.is_empty(ay, x) and (ay, x) not in not_considered:
                neighbours["n"] = self.board[ay][x][3]
                break
        for ax in range(x + 1, 8):
            if not self.is_empty(y, ax) and (y, ax) not in not_considered:
                neighbours["e"] = self.board[y][ax][3]
                break
        for ax in range(x - 1, -1, -1):
            if not self.is_empty(y, ax) and (y, ax) not in not_considered:
                neighbours["o"] = self.board[y][ax][3]
                break
        # UL
        for dt in range(1, 1 + min(x, y)):
            if not self.is_empty(y - dt, x - dt) and (y - dt, x - dt) not in not_considered:
                neighbours["no"] = self.board[y - dt][x - dt][3]
                break
        # UR
        for dt in range(1, 1 + min(7 - x, y)):
            if not self.is_empty(y - dt, x + dt) and (y - dt, x + dt) not in not_considered:
                neighbours["ne"] = self.board[y - dt][x + dt][3]
                break
        # DL
        for dt in range(1, 1 + min(x, 15 - y)):
            if not self.is_empty(y + dt, x - dt) and (y + dt, x - dt) not in not_considered:
                neighbours["so"] = self.board[y + dt][x - dt][3]
                break
        # DR
        for dt in range(1, 1 + min(7 - x, 15 - y)):
            if not self.is_empty(y + dt, x + dt) and (y + dt, x + dt) not in not_considered:
                neighbours["se"] = self.board[y + dt][x + dt][3]
                break
        return neighbours

    # **
    def get_pawn_neighbours(self, y, x):
        return self.get_line_and_column_pawn_neighbours(y, x) + self.get_diagonal_pawn_neighbours(y, x)

    def check_end(self):
        for y in range(8):
            for x in range(8):
                if self.is_empty(y, x) or self.board[y][x][2] == 1:
                    continue

                neighbours = []
                for neighbour in self.get_pawn_neighbours(y, x):
                    (v, u, pawn) = neighbour
                    if pawn[2] == 0 and v < 8:
                        neighbours.append(list(pawn))
                # print("voisin gardé", neighbours)

                n = len(neighbours)
                if n < 2:
                    continue
                # print("ici")
                for j in range(1, n):
                    for i in range(j):  # 0<=i<j<=n-1
                        # Toutes les combinaisons
                        if get_progression(self.board[y][x][0], neighbours[i][0], neighbours[j][0]) > 0:
                            print("avant gagne1", self.board[y][x], neighbours[i], neighbours[j], "in", y, x)
                            self.set_win(0)
                            return

        for y in range(8, 16):
            for x in range(8):
                if self.is_empty(y, x) or self.board[y][x][2] == 0:
                    continue

                neighbours = []
                for neighbour in self.get_pawn_neighbours(y, x):
                    (v, u, pawn) = neighbour
                    if pawn[2] == 1 and v >= 8:
                        neighbours.append(list(pawn))
                # print("voisin gardé", neighbours)

                n = len(neighbours)
                if n < 2:
                    continue
                # print("ici")
                for j in range(1, n):
                    for i in range(j):  # 0<=i<j<=n-1
                        # Toutes les combinaisons
                        if get_progression(self.board[y][x][0], neighbours[i][0], neighbours[j][0]) > 0:
                            print("avant gagne2", self.board[y][x], neighbours[i], neighbours[j], "in", y, x)
                            self.set_win(1)
                            return

    def set_turn(self, n):
        self.turn = n
        self.player_turn = n % 2

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
        last_turn = self.turn

        # initialise le dictionnaire
        self.aim = {}
        self.shooter = {}
        for nid in range(self.initial_number_of_pieces):
            self.reset_aim(nid)
            self.reset_shooter(nid)

        print("[init]")
        for i in range(2):
            self.set_turn(i)
            print(i)
            for attack in self.get_game_attacks():
                (typeattack, attackers, attacked) = attack
                for ae in attackers:
                    self.add_ranged_aim(self.get_id_by_pos(ae[0], ae[1]), self.get_id_by_pos(attacked[0], attacked[1]))
                    self.add_ranged_shooter(self.get_id_by_pos(attacked[0], attacked[1]),
                                            self.get_id_by_pos(ae[0], ae[1]))

        self.set_turn(last_turn)
        print("[fin init]")

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

    def get_neighbour_with_direction(self, pos, direction):
        y, x = pos
        dy, dx = direction
        y, x = y + dy, x + dx
        while self.in_board(y, x):
            # tkt
            if not self.is_empty(y, x):
                return y, x
        return -1, -1

    def update_neighbours_attack_defense(self, y, x):
        for j in range(-1, 2):
            for i in range(-1, 2):
                if i == j:
                    continue
                self.get_neighbour_with_direction((y, x), (j, i))

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
            if form == 1 or (
                    form == 4 and (self.pyramid[team][0] != -1 or self.pyramid[team][1] != -1)):  # c’est un rond
                if (not same_line_or_column) and dist == 0:  # s’il attaque en vertical juste à côté de lui
                    self.add_melee_aim(aid, bid)
                    self.add_melee_shooter(bid, aid)
                    # print("melee ", aid, bid)

            if form == 2 or (form == 4 and (self.pyramid[team][2] != -1 or self.pyramid[team][3] != -1)):
                if same_line_or_column and dist == 1:
                    self.add_melee_aim(aid, bid)
                    self.add_melee_shooter(bid, aid)
                    # print("melee ", aid, bid)

            if form == 3 or (form == 4 and (self.pyramid[team][4] != -1 or self.pyramid[team][5] != -1)):
                if same_line_or_column and dist == 2:
                    self.add_melee_aim(aid, bid)
                    self.add_melee_shooter(bid, aid)
                    # print("melee ", aid, bid)

    def update_aim_shooter(self):
        (old_y, old_x), (current_y, current_x) = self.last_move
        n = self.board[current_y][current_x]
        nid = n[3]  # identifiant de la pièce déplacée
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
                    self.locations[self.board[y][x][3]] = (y, x)
        for i in FAKE_ID_BLACK:
            self.locations[i] = self.locations[ID_BLACK_PYRAMID]
        for i in FAKE_ID_WHITE:
            self.locations[i] = self.locations[ID_WHITE_PYRAMID]
        print(self.locations)

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

    # à revoir, idée bonne mais même problème que la fonction au dessus
    def couple_develop_pyramid(self, id_pieces: list[int]):
        res = []
        id_pieces = self.develop_pyramid(id_pieces)  # on ne récupère que les étages dans le jeu
        for i in range(len(id_pieces)):
            for j in range(i):
                # il faut que ce soit deux pièces différentes (i!=j) ok
                # et que si i est une pyramide, j ne peut pas faire partie de la pyramide, si i est une partie de pyramide, j ne peut pas l’être
                # Rappel: ce sont des combinaisons ok
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
                check_id = self.board[ay][x][3]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        for ay in range(y - 1, max(y - 3 - 1, -1), -1):
            if not self.is_empty(ay, x):
                check_id = self.board[ay][x][3]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        for ax in range(x + 1, min(x + 3 + 1, 8)):
            if not self.is_empty(y, ax):
                check_id = self.board[y][ax][3]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        for ax in range(x - 1, max(x - 3 - 1, -1), -1):
            if not self.is_empty(y, ax):
                check_id = self.board[y][ax][3]
                if self.has_movement_of(check_id, 2) or self.has_movement_of(check_id, 3):
                    pieces.append(check_id)
                break
        # diag
        for dt in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
            dy, dx = dt
            if self.in_board(y + dy, x + dx) and not self.is_empty(y + dy, x + dx):
                check_id = self.board[y + dy][x + dx][3]
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
                attacks.append((TypeAttack.SIEGE, nid, nid))
        return attacks

    def __init__(self, view=False):
        self.start_time = time.time()
        self.board = []  # valeur forme, équipe
        self.init_board()
        self.turn = 0  # numéro du tour
        self.player_turn = 0  # numéro de celui à jouer
        self.width = 8
        self.height = 16
        self.pyramid = np.array([[1, 4, 9, 16, 25, 36], [-1, 16, 25, 36, 49, 64]])
        # fake id: blanche: 37 on rajoute 48--53, noire: 11 on rajoute 54-58
        self.stop = False
        self.last_move = ((-1, -1), (-1, -1))
        self.view = view
        self.game_history = []
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

        # print("direction", self.get_all_neighbours_with_directions(7, 4))

        # Ne considère que les mêlées
        self.initial_number_of_pieces = 59
        self.set_locations()
        self.set_attack_defense()
        print(self.aim)
        print(self.shooter)
        # la forme ([liste attaquant sous forme (ay, ax)], (y, x))
        self.iview = -1
        if self.view:
            self.game_history.append(self.board.copy())
        self.winner = -1
        print("test")
        # self.test_new_board()
        for j in range(1, 1506):  # ne sert à rien de dépasser 2000
            if self.stop:
                break

            preattacks = self.get_game_attacks()
            pre_aim_attacks = self.get_attacks_with_aim_shooter()

            coups = self.get_game_available_moves()
            # print(j, len(coups))
            if len(coups) == 0:
                break
            coup = coups[random.randint(0, len(coups) - 1)]
            self.move(coup)

            self.update_aim_shooter()
            attacks = self.get_game_attacks()

            available_attacks = attacks
            for no in preattacks:
                if no in attacks:
                    available_attacks.remove(no)

            aim_attacks = self.get_attacks_with_aim_shooter() + self.detect_siege()
            available_aim_attacks = aim_attacks
            for no in pre_aim_attacks:
                if no in aim_attacks:
                    available_aim_attacks.remove(no)
            print(self.turn)
            for i in available_attacks:
                print("BRUTE detects ", self.turn, ": ", str(i))
            for i in available_aim_attacks:
                print("AIMSHOOTER detects ", self.turn, ": ", str(i))

            self.game_attacks.append([])
            self.game_attacks[self.turn] = available_attacks
            self.execute_all_attacks(available_aim_attacks)
            self.check_end()
            self.end_turn()

        # print_board(self.board)
        print("Fin en", self.turn, "tours")
        print(f'Temps d\'exécution : {time.time() - self.start_time:.3}s')
        print_file("tabview", self.game_history)
        print("Coups enregistré ", len(self.game_history))
        self.show_game()


game = Game(view=True)
