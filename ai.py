

from main import Game
from minmax import Minmax


class AI:
    def __init__(self, pieces_rate_coef, y_dispersion_coef, x_dispersion_coef, y_center_coef, x_center_coef, progress_coef) -> None:
        self.pieces_rate_coef = pieces_rate_coef
        self.y_dispersion_coef = y_dispersion_coef
        self.x_dispersion_coef = x_dispersion_coef
        self.y_center_coef = y_center_coef
        self.x_center_coef = x_center_coef
        self.progress_coef = progress_coef

    def evaluate(self, game: Game):
        pieces_rate_delta, y_dispersion_delta, x_dispersion_delta, y_center_delta, x_center_delta, progress_delta = game.get_delta_stats()
        return (self.pieces_rate_coef * pieces_rate_delta 
                + self.y_dispersion_coef * y_dispersion_delta
                + self.x_dispersion_coef * x_dispersion_delta
                + self.y_center_coef * y_center_delta
                + self.x_center_coef * x_center_delta
                + self.progress_coef * progress_delta)
    
    def battle(self, ai, depth = 2, turns = 500):
        
        game = Game()
        for i in range(turns):
            coups = game.get_game_available_moves()
            if len(coups) == 0 or game.winner != -1:
                break
            eval_fct = self.evaluate if i % 2 == 0 else ai.evaluate
            points, moves, move = Minmax().min_max(game, depth, eval_fct)
            game.play_move(move)
        return (game.winner, game)

if __name__ == "__main__":
    ai1 = AI(1, 0, 0, 0, 0, 0)
    ai2 = AI(-1, 0, 0, 0, 0, 0)
    win, game = ai1.battle(ai2)
    game.show_game()




