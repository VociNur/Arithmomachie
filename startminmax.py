import numpy as np
from main import Game
from minmax import Minmax
import time


print("start")
start = time.time()

turns = 2000


game = Game()

for i in range(turns):
    #print(i)
    coups = game.get_game_available_moves()
    if len(coups) == 0  or game.winner != -1:
        break
    #game.play_move(coups[random.randint(0, len(coups)-1)])
    points, moves = Minmax().min_max(game, 2)
    best_move = moves[-1]
    game.play_move(best_move)

end  = time.time()
print("time: ", end-start)
game.show_game()

#11 minutes, on va règler ce problème