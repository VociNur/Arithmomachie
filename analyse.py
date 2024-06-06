from math import log
import tkinter as tk

import numpy as np
from json import loads
import random
import time
from timeit import timeit

from functools import partial
from  pynput import keyboard
from pynput.keyboard import Key, KeyCode
from minmax import Minmax
from enums.type_attack import TypeAttack
from copy import copy
from main import Game
import random
import matplotlib.pyplot as plt


turns = 10000
games = 1

x = [i for i in range(turns)]
tab = np.zeros(turns)

for i in range(games):
    game = Game()
    for i in range(turns):
        coups = game.get_game_available_moves()
        if len(coups) == 0 or game.winner != -1:
            for j in range(i, turns):
                tab[j] = tab[i-1]
            break
        game.play_move(coups[random.randint(0, len(coups)-1)])
        tab[i] = (np.sum(game.piece_number()[0:2])) + tab[i]

plt.plot(x, tab/games, "green")

color = ["", "red", "orange"]
for prof in [1, 2]:
    x = [i for i in range(turns)]
    tab = np.zeros(turns)

    game = Game()

    for i in range(turns):
        #print(i)
        coups = game.get_game_available_moves()
        if len(coups) == 0  or game.winner != -1:
            for j in range(i, turns):
                tab[j] = tab[i-1]
            break
        #game.play_move(coups[random.randint(0, len(coups)-1)])
        points, moves = Minmax().min_max(game, prof)
        best_move = moves[-1]
        game.play_move(best_move)
        tab[i] = np.sum(game.piece_number()[0:2])

    plt.plot(x, tab, color[prof])
    print("prof", prof)
    if prof == 2:
        game.show_game()

plt.show()
