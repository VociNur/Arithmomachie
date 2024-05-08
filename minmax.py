
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

from enums.type_attack import TypeAttack
from copy import deepcopy, copy
from main import Game
import random

class Minmax():


    def avance(self):
        game = Game()
        for i in range(1000):
            coups = game.get_game_available_moves()     
            if len(coups) == 0 or game.winner != -1:
                break
            coup_choisi = None
            if game.player_turn == 0:
                for coup in coups:
                    (y,x),(dy, dx) = coup
                    if dy < 0:
                        coup_choisi = coup
                        break
            if game.player_turn == 1:
                for coup in coups:
                    (y, x),(dy, dx) = coup
                    if dy > 0:
                        coup_choisi = coup
                        break
            if not coup_choisi:
                break
            game.play_move(coup_choisi)
            
        game.show_game()

    def play_game(self) -> None:
        self.game = Game()
        for i in range(2000):
            #print(i)
            coups = self.game.get_game_available_moves()
            if len(coups) == 0:
                break
            #game.play_move(coups[random.randint(0, len(coups)-1)])
            points, moves = self.min_max(self.game, 1)
            best_move = moves[-1]
            self.game.play_move(best_move)

    def dif(self, tab, index):
        return tab[index] - tab[1-index]

    def evaluate(self, game: Game, root_player_turn):
        rates = game.piece_rate()
        progress = [game.progress(0), game.progress(1)]

        return self.dif(rates, root_player_turn)*1000 + self.dif(progress, root_player_turn)

    #min max    
    def min(self, game:Game, root_player_turn, profondeur):

        if profondeur == 0 :
            return (self.evaluate(game, root_player_turn), [])
        moves = game.get_game_available_moves()
        if moves == []:
            (self.evaluate(game, root_player_turn), [])

        worst_sub_point, worst_moves_to_go_sub_game = None, None
        for index, m in enumerate(moves):
            sub_game = deepcopy(game)
            sub_game.play_move(moves[index])
            sub_point, moves_to_go_sub_game = self.max(sub_game, root_player_turn, profondeur-1)
            moves_to_go_sub_game.append(m)
            if index == 0 or worst_sub_point > sub_point:
                worst_sub_point = sub_point
                worst_moves_to_go_sub_game = moves_to_go_sub_game
        return worst_sub_point, worst_moves_to_go_sub_game    


    def max(self, game:Game, root_player_turn, profondeur):
        if profondeur == 0 :
            return (self.evaluate(game, root_player_turn), [])
        moves = game.get_game_available_moves()
        if moves == []:
            (self.evaluate(game, root_player_turn), [])

        best_sub_point, best_moves_to_go_sub_game = None, None
        for index in range(len(moves)):
            sub_game = deepcopy(game)
            sub_game.play_move(moves[index])
            sub_point, moves_to_go_sub_game = self.min(sub_game, root_player_turn, profondeur-1)
            moves_to_go_sub_game.append(moves[index])
            #print(sub_point, best_sub_point)
            if index == 0 or best_sub_point < sub_point:
                best_sub_point = sub_point
                
                best_moves_to_go_sub_game = moves_to_go_sub_game
        return best_sub_point, best_moves_to_go_sub_game    


    
    def min_max(self, game:Game, profondeur):
        return self.max(game, game.player_turn, profondeur)
    
    

if __name__ == "__main__":
    min = Minmax()
    game = min.game
    print("ah")
    print(game.piece_number())
    print(game.piece_rate())
    print(game.isobarycenter(0))
    print(game.isobarycenter(1))
    print(game.dispersion(0))
    print(game.dispersion(1))
    print(game.progress(0))
    print(game.progress(1))
    game.show_game()




