import math
from tkinter import *
import numpy as np
import json
import random

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


def add_attacks(l1: list, l2: list, p: (list, list)):
    p1, p2 = p
    return l1 + p1, l2 + p2


class Game:
    # Permet de visualiser le jeu à la fin de la partie
    def show_game(self):
        tk = Tk()
        tk.config(width=400, height=800)
        tk.title('Grid')

        canvas = Canvas(tk, width=400, height=800, bg='#FFFFFF')
        canvas.grid(row=0, column=0, columnspan=1)
        for i in range(self.width):
            for j in range(self.height):
                if not self.is_empty(j, i):
                    (point, form, team) = self.board[j][i]
                    color = "Blue" if team == 0 else "Red"
                    if form == 1:
                        canvas.create_oval(i * 50 + 5, j * 50 + 5, (i + 1) * 50 - 5, (j + 1) * 50 - 5, outline=color,
                                           fill="WHITE", width=2)
                    if form == 2:
                        dp = np.array([(-20, 20), (20, 20), (0, -20)])
                        points = (i * 50 + 25, j * 50 + 25) + dp
                        canvas.create_polygon(points.flatten().tolist(), outline=color, fill="WHITE", width=2)
                    if form == 3:
                        canvas.create_rectangle(i * 50 + 5, j * 50 + 5, (i + 1) * 50 - 5, (j + 1) * 50 - 5,
                                                outline=color, fill="WHITE", width=2)

                    canvas.create_text(i * 50 + 25, j * 50 + 25, text=str(point))

        canvas.pack()

        mainloop()

    def add_piece(self, y, x, side, form, value):
        self.board[y][x] = (side, form, value)

    def init_board(self):
        pre = "./boards/"
        f = open(pre + "basics3.json", "r")
        self.board = np.array(json.loads(f.read()))
        f.close()

    # Vérifie si la position est bien dans le jeu
    def in_board(self, j, i):
        return 0 <= j < self.height and 0 <= i < self.width

    # Vérifie si une case est libre, sans pion
    def is_empty(self, j, i):
        return np.equal(self.board[j][i], [-1, -1, -1]).all()

    # On récupère les mouvements réguliers, on doit vérifier que tout le trajet est libre
    def get_pawn_available_regular_moves(self, pawn, j, i):
        available_moves = []
        (value, form, team) = pawn
        if form == 1 or (form == 4 and (self.pyramid[team][0] != -1 or self.pyramid[team][1] != -1)):  # c’est un rond
            relative_moves_circle = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for rm in relative_moves_circle:
                dj, di = rm
                if self.in_board(j + dj, i + di) and self.is_empty(j + dj, i + di):
                    available_moves += [((j, i), (dj, di))]

        if form == 2 or (form == 4 and (self.pyramid[team][2] != -1 or self.pyramid[team][3] != -1)):
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

        if form == 3 or (form == 4 and (self.pyramid[team][4] != -1 or self.pyramid[team][5] != -1)):
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
            if form == 2 or form == 4:
                r = 2
                if self.in_board(j + r, i + u) and self.is_empty(j + r, i + u):
                    available_moves += [((j, i), (r, u))]
                if self.in_board(j - r, i + u) and self.is_empty(j - r, i + u):
                    available_moves += [((j, i), (-r, u))]
                if self.in_board(j + u, i + r) and self.is_empty(j + u, i + r):
                    available_moves += [((j, i), (u, r))]
                if self.in_board(j + u, i - r) and self.is_empty(j + u, i - r):
                    available_moves += [((j, i), (u, -r))]

            if form == 3 or form == 4:
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
        # pour toutes les cases non vide, on ajoute ses coups possibles dans la liste des coups
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

    def end_turn(self):
        self.turn += 1
        self.player_turn = (self.player_turn + 1) % 2

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
                    attack_board[attack[0]][attack[1]].append(value)

        return attack_board

    # Gère les attaques et attaques partielles sur une pyramide
    def equations_attacks(self, y, x, a: int,
                          b: int):  # a et b sont des pseudos-attaquants, utilisé lors d’attaque en assaut
        total_attacks = []
        partial_attacks = []
        if a_is_equation(self.board[y][x][0], a, b):
            total_attacks.append((y, x))
        if self.board[y][x][1] == 4:  # le retour de l’ennui
            for n in self.pyramid[1 - self.player_turn]:  # si elle appartient à l’ennemi
                if a_is_equation(n, a, b):
                    partial_attacks.append((y, x, n))
        return total_attacks, partial_attacks

    def get_melee_attacks(self):
        total_attacks = []
        partial_attacks = []
        attack_board = self.get_melee_attack_board()
        for y in range(16):
            for x in range(8):
                attackers = attack_board[y][x]
                # Rencontre et puissance
                for a in attackers:
                    # print("-->", self.board[y][x][0], a)
                    if is_power_or_root(self.board[y][x][0], a):
                        total_attacks.append((y, x))
                # Embuscade
                for i in range(len(attackers)):
                    for j in range(i):
                        equa_attacks = self.equations_attacks(y, x, attackers[i], attackers[j])
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks, equa_attacks)
        return total_attacks, partial_attacks

    def get_assault_attacks(self): #Il y aurait moyen de réduire un peu la taille avec fonction auxiliaire, pas sûr...
        # en ligne, en colonne, ou en diagonale
        #print("-------------------")
        total_attacks = []
        partial_attacks = []
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
                        equa_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks, equa_attacks)

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equa_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks, equa_attacks)
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
                        equa_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks,
                                                                     equa_attacks)

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equa_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks,
                                                                     equa_attacks)
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0

        #3 diagonale descendante
        for debut_ligne in range(-6, 15):
            none = [-1, -1, -1]
            last_piece = none
            last_x, last_y = -1, -1
            espace = 0
            for i in range(8):
                y= debut_ligne + i
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
                        equa_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks, equa_attacks)

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equa_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks, equa_attacks)
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
                        equa_attacks = self.equations_attacks(y, x, last_piece[0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks,
                                                                     equa_attacks)

                    if last_piece[2] != self.player_turn and self.board[y][x][2] == self.player_turn:
                        equa_attacks = self.equations_attacks(last_y, last_x, self.board[y][x][0], espace)
                        total_attacks, partial_attacks = add_attacks(total_attacks, partial_attacks,
                                                                     equa_attacks)
                last_piece = self.board[y][x]
                last_y = y
                last_x = x
                espace = 0
        return total_attacks, partial_attacks

    def get_siege_attacks(self):
        total_attacks = []
        for y in range(16):
            for x in range(8):
                if self.is_empty(y, x):
                    continue
                moves = self.get_pawn_available_regular_moves(self.board[y][x], y, x)
                if len(moves) == 0:
                    total_attacks.append((y, x))
        return total_attacks
    def get_game_attacks(self):
        melee_attacks, partial_melee_attacks = self.get_melee_attacks()
        assault_attacks, partial_assault_attacks = self.get_assault_attacks()
        siege_attacks = self.get_siege_attacks()

        attacks = melee_attacks + assault_attacks + siege_attacks
        partial_attacks = partial_melee_attacks + partial_assault_attacks
        return attacks, partial_attacks

    def kill(self, attack, partial_attack):
        for a in attack:
            (y, x) = a
            self.board[y][x] = (-1, -1, -1)
            # print("paf")
        for p in partial_attack:  # on attaque celle de l’adversaire donc 1-player_turn
            (y, x, n) = p
            i = np.where(self.pyramid[1 - self.player_turn] == n)[0]
            # print_file("paf",[self.board[y][x], p])
            self.pyramid[1 - self.player_turn][i] = -1
            self.board[y][x][0] -= n

            if np.equal(self.pyramid[1 - self.player_turn], [-1, -1, -1, -1, -1, -1]).all():
                self.board[y][x] = [-1, -1, -1]

            # print_file("paf", ["-->",  self.board[y][x], self.pyramid[1-self.player_turn]])

    def __init__(self):
        self.board = []  # valeur forme, équipe
        self.init_board()
        self.turn = 0  # numéro du tour
        self.player_turn = 0  # numéro de celui à jouer
        self.width = 8
        self.height = 16
        self.pyramid = np.array([[1, 4, 9, 16, 25, 36], [-1, 16, 25, 36, 49, 64]])
        self.stop = False
        print("test")
        clear_file("paf")

        i = 0
        for j in range(1):
            if self.stop:
                break
            coups = self.get_game_available_moves()
            # print(j, len(coups))
            if len(coups) == 0:
                break
            coup = coups[random.randint(0, len(coups) - 1)]
            self.move(coup)
            attack, partial_attack = self.get_game_attacks()
            self.kill(attack, partial_attack)
            self.end_turn()

            i += 1

        print_board(self.board)
        print("Fin en", i, "tours")
        self.show_game()


game = Game()
