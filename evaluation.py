

from random import randint
from typing import List
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
    
      

    
    def get_genomes_from(self, eval):
        """_summary_

        Args:
            ai (Evaluation): _description_
        """
        print("---")
        print(self.to_string())
        print("+")
        print(eval.to_string())
        print("=")
        self.pieces_rate_coef = mean([self.pieces_rate_coef, eval.pieces_rate_coef])
        self.y_dispersion_coef = mean([self.y_dispersion_coef, eval.y_dispersion_coef])
        self.x_dispersion_coef = mean([self.x_dispersion_coef, eval.x_dispersion_coef])
        self.y_center_coef = mean([self.y_center_coef, eval.y_center_coef])
        self.x_center_coef = mean([self.x_center_coef, eval.x_center_coef])
        self.progress_coef = mean([self.progress_coef, eval.progress_coef])
        print(self.to_string())

    def mutate(self):
        mini = -100
        maxi = 100
        self.pieces_rate_coef = self.pieces_rate_coef + randint(mini, maxi) / 1000
        self.y_dispersion_coef = self.y_dispersion_coef + randint(mini, maxi) / 1000
        self.x_dispersion_coef = self.x_dispersion_coef + randint(mini, maxi) / 1000
        self.y_center_coef = self.y_center_coef + randint(mini, maxi) / 1000
        self.x_center_coef = self.x_center_coef + randint(mini, maxi) / 1000
        self.progress_coef = self.progress_coef + randint(mini, maxi) / 1000


        limit = 1000
        if self.pieces_rate_coef > limit:
            self.pieces_rate_coef = limit
            print("Range !!!")
        if self.pieces_rate_coef < -limit:
            self.pieces_rate_coef = -limit
            print("Range !!!")
        if self.y_dispersion_coef > limit:
            self.y_dispersion_coef = limit
            print("Range !!!")
        if self.y_dispersion_coef < -limit:
            self.y_dispersion_coef = -limit
            print("Range !!!")
        if self.x_dispersion_coef > limit:
            self.x_dispersion_coef = limit
            print("Range !!!")
        if self.x_dispersion_coef < -limit:
            self.x_dispersion_coef = -limit
            print("Range !!!")
        if self.y_center_coef > limit:
            self.y_center_coef = limit
            print("Range !!!")
        if self.y_center_coef < -limit:
            self.y_center_coef = -limit
            print("Range !!!")
        if self.x_center_coef > limit:
            self.x_center_coef = limit
            print("Range !!!")
        if self.x_center_coef < -limit:
            self.x_center_coef = -limit
            print("Range !!!")
        if self.progress_coef > limit:
            self.progress_coef = limit
            print("Range !!!")
        if self.progress_coef < -limit:
            self.progress_coef = -limit
            print("Range !!!")
        


    def round(self): # round les flottants
        nbr = 3
        self.pieces_rate_coef = round(self.pieces_rate_coef, nbr)
        self.y_dispersion_coef = round(self.y_dispersion_coef, nbr)
        self.x_dispersion_coef = round(self.x_dispersion_coef, nbr)
        self.y_center_coef = round(self.y_center_coef, nbr)
        self.x_center_coef = round(self.x_center_coef, nbr)
        self.progress_coef = round(self.progress_coef, nbr)


    def to_string(self):
        encoding_character = "/"
        return f"{self.pieces_rate_coef}{encoding_character}{self.y_dispersion_coef}{encoding_character}{self.x_dispersion_coef}{encoding_character}{self.y_center_coef}{encoding_character}{self.x_center_coef}{encoding_character}{self.progress_coef}"
    
    @classmethod
    def from_average(self, evs):
        pieces_rate_coef = mean([eval.pieces_rate_coef for eval in evs])
        y_dispersion_coef = mean([eval.y_dispersion_coef for eval in evs])
        x_dispersion_coef = mean([eval.x_dispersion_coef for eval in evs])
        y_center_coef = mean([eval.y_center_coef for eval in evs])
        x_center_coef = mean([eval.x_center_coef for eval in evs])
        progress_coef = mean([eval.progress_coef for eval in evs])
        return Evaluation(pieces_rate_coef, y_dispersion_coef, x_dispersion_coef, y_center_coef, x_center_coef, progress_coef)
    
    @classmethod
    def from_parent(self, ev1, ev2):
        return Evaluation.from_average([ev1, ev2])


    @classmethod
    def from_string(self, s:str):
        decoding_character = "/"
        ss = s.split(decoding_character)
        if len(ss) != 6:
            raise Exception
        return Evaluation(float(ss[0]),float(ss[1]),float(ss[2]),float(ss[3]),float(ss[4]),float(ss[5]))

    def __str__(self) -> str:
        return f"Eval: {self.pieces_rate_coef} {self.y_dispersion_coef} {self.x_dispersion_coef} {self.y_center_coef} {self.x_center_coef} {self.progress_coef}"
    
    def __eq__(self, value: object) -> bool:
        eps = 10e-6
        if type(value) is Evaluation:

            #print(self.date_creation)
            #print(value.date_creation)
            self.round()
            value.round() #au cas où 
            return self.pieces_rate_coef == value.pieces_rate_coef and self.y_dispersion_coef == value.y_dispersion_coef and self.x_dispersion_coef == value.x_dispersion_coef and self.y_center_coef == value.y_center_coef and self.x_center_coef == value.x_center_coef and self.progress_coef == value.progress_coef
        return False

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