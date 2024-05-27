from evaluation import Evaluation
from main import Game
from minmax import Minmax
from threading import Thread

if False:

    minmax = Minmax()
    game = Game()
    eval = Evaluation(1, 0, 0, 0 ,0 ,10)
    for i in range(1):

        _,_, bm = minmax.min_max(game, 3, eval_function=eval.evaluate)
        game.play_move(bm)
    
    game.show_game()
    
    if False:
        minmax = Minmax()
        game = Game()
        for i in range(20):

            _,_, bm = minmax.min_max(game, 1, eval_function=minmax.basic_evaluate)
            game.play_move(bm)
        
        game.show_game()


def play():
    minmax = Minmax()
    game = Game()
    eval = Evaluation(1, 0, 0, 0 ,0 ,0)
    for i in range(50):

        _,_, bm = minmax.min_max(game, 1, eval_function=eval.evaluate)
        game.play_move(bm)
    
    game.show_game()

if __name__ == "__main__":
    n = 2
    threads = []
    for i in range(n):
        t = Thread(target = play)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    