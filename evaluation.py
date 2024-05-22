

from numpy import mean
from main import Game
from minmax import Minmax



class Evaluation:
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
    
    def get_genomes_from(self, eval):
        """_summary_

        Args:
            ai (Evaluation): _description_
        """
        self.pieces_rate_coef = mean([self.pieces_rate_coef, eval.pieces_rate_coef])
        self.y_dispersion_coef = mean([self.y_dispersion_coef, eval.y_dispersion_coef])
        self.x_dispersion_coef = mean([self.x_dispersion_coef, eval.x_dispersion_coef])
        self.y_center_coef = mean([self.y_center_coef, eval.y_center_coef])
        self.x_center_coef = mean([self.x_center_coef, eval.x_center_coef])
        self.progress_coef = mean([self.progress_coef, eval.progress_coef])

    def to_string(self):
        encoding_character = "/"
        return f"{self.pieces_rate_coef}{encoding_character}{self.y_dispersion_coef}{encoding_character}{self.x_dispersion_coef}{encoding_character}{self.y_center_coef}{encoding_character}{self.x_center_coef}{encoding_character}{self.progress_coef}"
    
    @classmethod
    def from_string(self, s:str):
        decoding_character = "/"
        ss = s.split(decoding_character)
        if len(ss) != 6:
            raise Exception
        return Evaluation(int(ss[0]),int(ss[1]),int(ss[2]),int(ss[3]),int(ss[4]),int(ss[5]))

    def __str__(self) -> str:
        return f"Eval: {self.pieces_rate_coef} {self.y_dispersion_coef} {self.x_dispersion_coef} {self.y_center_coef} {self.x_center_coef} {self.progress_coef}"
    

def test_class_method():
    eval = Evaluation(1, 2, 3, 4, 5, 6)
    to_str = eval.to_string()
    eval2 = Evaluation.from_string(to_str)
    print(eval)
    print(eval2)

if __name__ == "__main__":
    #ai1 = Evaluation(1, 0, 0, 0, 0, 0)
    #ai2 = Evaluation(-1, 0, 0, 0, 0, 0)
    #win, game = ai1.battle(ai2)
    #game.show_game()
    test_class_method()