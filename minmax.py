
from math import log
import tkinter as tk

import numpy as np
from json import loads
from timeit import timeit
import math

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

    def basic_evaluate(self, game: Game):
        rates = game.piece_rate()
        progress = [game.progress(0), game.progress(1)]
        
        return self.dif(rates, 0)*1000 + self.dif(progress, 0) #le second paramètre de dif servait avant

    def evaluate(self, game:Game, eval_function, player_turn):
        multiplier = 1 if player_turn == 0 else -1
        if game.winner != -1:
            winner = 1 if player_turn == game.winner else -1
            print("Detects win")
            return winner * 100000000
        return eval_function(game) * multiplier
    
    #min max    
    def minmax_min(self, game:Game, root_player_turn, eval_function, profondeur, alpha, beta):

        if profondeur == 0 :
            eval = self.evaluate(game, eval_function, root_player_turn)
            return (eval, [])
        moves = game.get_game_available_moves()
        if moves == []:
            eval = self.evaluate(game, eval_function, root_player_turn)
            return (eval, [])

        worst_sub_point, worst_moves_to_go_sub_game = None, None
        for index, m in enumerate(moves):
            sub_game = deepcopy(game)
            sub_game.play_move(moves[index])
            sub_point, moves_to_go_sub_game = self.minmax_max(sub_game, root_player_turn, eval_function, profondeur-1, alpha, beta)

            if sub_point <= alpha: #elagage alpha
                return (-math.inf, []) # pour ne pas qu'il soit considéré par le max
            
            moves_to_go_sub_game.append(m)
            if index == 0 or worst_sub_point > sub_point:
                worst_sub_point = sub_point
                beta = min(beta, sub_point)
                #on pourrait le modifier avant, ça revient au même
                worst_moves_to_go_sub_game = moves_to_go_sub_game
        return worst_sub_point, worst_moves_to_go_sub_game    


    def minmax_max(self, game:Game, root_player_turn, eval_function, profondeur, alpha, beta):
        if profondeur == 0 :
            eval = self.evaluate(game, eval_function, root_player_turn)
            return (eval, []) #un max ne modifie que beta
        moves = game.get_game_available_moves()
        if moves == []:
            eval = self.evaluate(game, eval_function, root_player_turn)
            return (eval, [])

        best_sub_point, best_moves_to_go_sub_game = None, None
        for index in range(len(moves)):
            sub_game = deepcopy(game)
            sub_game.play_move(moves[index])
            sub_point, moves_to_go_sub_game = self.minmax_min(sub_game, root_player_turn, eval_function, profondeur-1, alpha, beta)

            if sub_point >= beta:
                return (math.inf, [])

            moves_to_go_sub_game.append(moves[index])
            #print(sub_point, best_sub_point)
            if index == 0 or best_sub_point < sub_point:
                best_sub_point = sub_point
                alpha = max(alpha, sub_point) #vient d'un min donc alpha est modifié
                #on pourrait modifier le alpha avant
                best_moves_to_go_sub_game = moves_to_go_sub_game
        return best_sub_point, best_moves_to_go_sub_game    

    
    def min_max(self, game:Game, profondeur, eval_function = None):
        if eval_function == None:
            eval_function = self.basic_evaluate
        points, moves = self.minmax_max(game, game.player_turn, eval_function, profondeur, -math.inf, math.inf)
        return (points, moves, moves[-1])
    
    


if __name__ == "__main__":
    minmax = Minmax()
    game = Game()
    for i in range(20):

        _,_, bm = minmax.min_max(game, 1, eval_function=None)
        game.play_move(bm)
    
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



