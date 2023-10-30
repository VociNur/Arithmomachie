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
                    (point, form, team) = board[j][i]
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
                        self.canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point))
                    else:
                        self.canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point), fill=color)
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

    def add_piece(self, y, x, side, form, value):
        self.board[y][x] = (side, form, value)

    def init_board(self):
        pre = "./boards/"
        f = open(pre + "game.json", "r")
        self.board = np.array(json.loads(f.read()))
        f.close()

    # Vérifie si la position est bien dans le jeu
    def in_board(self, j, i):
        return 0 <= j < self.height and 0 <= i < self.width

    # Vérifie si une case est libre, sans pion
    def is_empty(self, j, i):
        return np.equal(self.board[j][i], [-1, -1, -1]).all()

    @staticmethod
    def is_empty_specific_board(board, j, i):
        return np.equal(board[j][i], [-1, -1, -1]).all()

    # On récupère les mouvements réguliers, on doit vérifier que tout le trajet est libre
    def get_pawn_available_regular_moves(self, pawn, j, i):
        available_moves = []
        (value, form, team) = pawn
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
            if self.in_board(j + r, i) and np.equal(self.board[j + 1:j + r + 1, i], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (r, 0))]
            if self.in_board(j - r, i) and np.equal(self.board[j - r:j, i], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (-r, 0))]
            if self.in_board(j, i + r) and np.equal(self.board[j, i + 1:i + r + 1], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (0, r))]
            if self.in_board(j, i - r) and np.equal(self.board[j, i - r:i], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (0, -r))]

        if form == 3 or (form == 4 and self.check_pyramid_form(team, 3)):
            r = 3
            if self.in_board(j + r, i) and np.equal(self.board[j + 1:j + r + 1, i], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (r, 0))]
            if self.in_board(j - r, i) and np.equal(self.board[j - r:j, i], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (-r, 0))]
            if self.in_board(j, i + r) and np.equal(self.board[j, i + 1:i + r + 1], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (0, r))]
            if self.in_board(j, i - r) and np.equal(self.board[j, i - r:i], np.full((r, 3), -1)).all():
                available_moves += [((j, i), (0, -r))]

        return available_moves

    # On récupère les mouvements irréguliers, juste à vérifier que la case finale est libre
    def get_pawn_available_irregular_moves(self, pawn, j, i):
        available_moves = []
        (value, form, team) = pawn
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
                (value, form, team) = self.board[y][x]
                if team == self.player_turn:
                    available_moves += self.get_pawn_available_regular_moves((value, form, team), y, x)
                    available_moves += self.get_pawn_available_irregular_moves((value, form, team), y, x)
        return available_moves

    # permet de déplacer une pièce
    def move(self, move):
        ((y, x), (dy, dx)) = move
        self.board[y + dy][x + dx] = self.board[y][x]
        self.board[y][x] = (-1, -1, -1)
        self.last_move = (y + dy, x + dx)
        if self.view:
            self.move_history.append(((y, x), (y + dy, x + dx)))

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
                    and np.equal(self.board[j + 1:j + space + 1, i], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j + range, i)) \
                    and self.board[j + range][i][2] != self.player_turn:
                available_attacks += [(j + range, i)]

            if self.in_board(j - range, i) \
                    and np.equal(self.board[j - space:j, i], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j - range, i)) \
                    and self.board[j - range][i][2] != self.player_turn:
                available_attacks += [(j - range, i)]

            if self.in_board(j, i + range) \
                    and np.equal(self.board[j, i + 1:i + space + 1], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j, i + range)) \
                    and self.board[j][i + range][2] != self.player_turn:
                available_attacks += [(j, i + range)]

            if self.in_board(j, i - range) \
                    and np.equal(self.board[j, i - space:i], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j, i - range)) \
                    and self.board[j][i - range][2] != self.player_turn:
                available_attacks += [(j, i - range)]

        if form == 3 or (form == 4 and (self.pyramid[team][4] != -1 or self.pyramid[team][5] != -1)):
            range = 3
            space = range - 1
            if self.in_board(j + range, i) \
                    and np.equal(self.board[j + 1:j + space + 1, i], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j + range, i)) \
                    and self.board[j + range][i][2] != self.player_turn:
                available_attacks += [(j + range, i)]

            if self.in_board(j - range, i) \
                    and np.equal(self.board[j - space:j, i], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j - range, i)) \
                    and self.board[j - range][i][2] != self.player_turn:
                available_attacks += [(j - range, i)]

            if self.in_board(j, i + range) \
                    and np.equal(self.board[j, i + 1:i + space + 1], np.full((space, 3), -1)).all() \
                    and (not self.is_empty(j, i + range)) \
                    and self.board[j][i + range][2] != self.player_turn:
                available_attacks += [(j, i + range)]

            if self.in_board(j, i - range) \
                    and np.equal(self.board[j, i - space:i], np.full((space, 3), -1)).all() \
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
                (value, form, team) = self.board[y][x]
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

    def progression_attacks(self, y, x, a: int, b: int):  # même idée que précédent
        attacks = []
        progression = get_progression(self.board[y][x][0], a, b)
        if progression > 0:
            ##print("PROGRESSION", self.board[y][x][0], a, b, self.turn)
            attacks.append((y, x, self.board[y][x][0], progression))
        if self.board[y][x][1] == 4:  # le retour de l’ennui
            for n in self.pyramid[1 - self.player_turn]:  # si elle appartient à l’ennemi
                if n == -1:
                    continue
                pro = get_progression(n, a, b)
                if pro > 0:
                    ##print("PROGRESSION", pro, n, a, b, self.turn)
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
            for x in range(8):
                if self.is_empty(y, x):
                    espace += 1
                    continue
                if np.equal(last_piece, none).all():
                    last_piece = self.board[y][x]
                    last_y = y
                    last_x = x
                    espace = 0
                    continue
                # Dans ce cas, les deux pieces peuvent se toucher, de longueur i
                # On vérifie si un de l’équipe qui joue, peut battre l’autre
                # on l’attaque avec la pièce à nous et la distance qui les sépare
                if espace > 1:
                    if last_piece[2] == self.player_turn and self.board[y][x][2] != self.player_turn:
                        equation_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        for ea in equation_attacks:
                            # print("Append assault:", str((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea)))
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equation_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, last_piece[0])], ea))
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0
        # 2. en colonne (*on échange juste l’initialisation de x et y*)
        for x in range(8):
            none = [-1, -1, -1]
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
                        equation_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equation_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, last_piece[0])], ea))
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0

        # 3 diagonale descendante
        for debut_ligne in range(-6, 15):
            none = [-1, -1, -1]
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
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equation_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, last_piece[0])], ea))
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0
        # 4 diagonale ascendante
        for debut_ligne in range(1, 22):
            none = [-1, -1, -1]
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
                            attacks.append((TypeAttack.ASSAULT, [(last_y, last_x, last_piece[0])], ea))

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equation_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        for ea in equation_attacks:
                            attacks.append((TypeAttack.ASSAULT, [(y, x, last_piece[0])], ea))
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
        (value, form, team) = self.board[y][x]
        last_y, last_x = self.last_move
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
        last_y, last_x = self.last_move
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

    def kill(self, attacks):

        for a in attacks:
            (type_attack, attackers, attacked) = a
            (y, x, n) = attacked
            if self.is_empty(y, x):
                continue
            if n == self.board[y][x][0]:  # c’est une attaque totale
                self.board[y][x] = (-1, -1, -1)
                continue
            # print("vérif", attacked, self.board[y][x])
            # A partir de là c’est une pyramide
            # on attaque celle de l’adversaire donc 1-player_turn
            # print("partial attack", self.turn)
            # print("partial attack", y, x, n)
            # print("pyramide de l’autre", self.pyramid[1 - self.player_turn])
            # print("where:", np.where(self.pyramid[1 - self.player_turn] == n))
            # print("where 0", np.where(self.pyramid[1 - self.player_turn] == n)[0])
            where = np.where(self.pyramid[1 - self.player_turn] == n)[0]
            if len(where) == 0:
                continue
            i = where[0]
            # print("i:", i)
            # print_file("paf",[self.board[y][x], p])
            self.pyramid[1 - self.player_turn][i] = -1
            self.board[y][x][0] -= n

            if np.equal(self.pyramid[1 - self.player_turn], [-1, -1, -1, -1, -1, -1]).all():
                self.board[y][x] = [-1, -1, -1]

            # print_file("paf", ["-->",  self.board[y][x], self.pyramid[1-self.player_turn]])

    def set_win(self, n):
        print("GAGNE", n)
        self.stop = True
        self.winner = n

    # ** get_pawn_neigbours
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

        for y in range(8):
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

    def __init__(self, view=False):
        self.start_time = time.time()
        self.board = []  # valeur forme, équipe
        self.init_board()
        self.turn = 0  # numéro du tour
        self.player_turn = 0  # numéro de celui à jouer
        self.width = 8
        self.height = 16
        self.pyramid = np.array([[1, 4, 9, 16, 25, 36], [-1, 16, 25, 36, 49, 64]])
        self.stop = False
        self.last_move = (-1, -1)
        self.view = view
        self.game_history = []
        self.move_history = []
        # game_attacks est toujours sauvegardé
        self.game_attacks = []  # l’élément i représente l’ensemble des attaques après le coup i, une attaque est sous
        # la forme ([liste attaquant sous forme (ay, ax)], (y, x))
        self.iview = -1
        if self.view:
            self.game_history.append(self.board.copy())
        self.winner = -1
        print("test")

        for j in range(1, 1501):  # ne sert à rien de dépasser 2000
            if self.stop:
                break
            preattacks = self.get_game_attacks()
            coups = self.get_game_available_moves()
            # print(j, len(coups))
            if len(coups) == 0:
                break
            coup = coups[random.randint(0, len(coups) - 1)]
            self.move(coup)
            attacks = self.get_game_attacks()

            available_attacks = attacks
            for no in preattacks:
                if no in attacks:
                    available_attacks.remove(no)

            self.game_attacks.append([])
            self.game_attacks[self.turn] = available_attacks

            self.kill(available_attacks)
            self.check_end()
            self.end_turn()

        # print_board(self.board)
        print("Fin en", self.turn, "tours")
        print(f'Temps d\'exécution : {time.time() - self.start_time:.3}s')
        print_file("tabview", self.game_history)
        print("Coups enregistré ", len(self.game_history))
        self.show_game()


game = Game(view=True)
