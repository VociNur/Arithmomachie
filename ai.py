


import time
from evaluation import Evaluation
from match import Match
from server import MyServer


class AI:

    def init_gen_0(self):

        self.evaluations[0] = Evaluation(0, 0, 0, 0, 0, 0)
        self.evaluations[1] = Evaluation(1, 0, 0, 0, 0, 0)
        self.evaluations[2] = Evaluation(0, 1, 0, 0, 0, 0)
        self.evaluations[3] = Evaluation(0, 0, 1, 0, 0, 0)
        self.evaluations[4] = Evaluation(0, 0, 0, 1, 0, 0)
        self.evaluations[5] = Evaluation(0, 0, 0, 0, 1, 0)
        self.evaluations[6] = Evaluation(0, 0, 0, 0, 0, 1)
        self.evaluations[7] = Evaluation(1, 1, 1, 1, 1, 1)
        self.population_count = 8


    def __init__(self) -> None:
        self.evaluations = {}
        self.population_count = 0
        self.server = MyServer(3)

        self.init_gen_0()
        for i in range(5):
            self.do_generation()
        print("FINITO")


    def do_generation(self):
        self.server.match_to_play = []
        self.server.result = []
        for i in range(self.population_count):
            for j in range(i):
                match = Match(j, self.evaluations[j], i, self.evaluations[i])
                self.server.match_to_play.append(match) #1<=j<i<=n-1
        nbr_parties = len(self.server.match_to_play)
        print(f"Nombre de parties à jouer: {self.server.match_to_play }")

        while self.server.match_to_play  != len(self.server.result):
            print(f"{len(self.server.result)}/{nbr_parties} finished game")
            print(f"{len(self.server.get_current_matches())}/{nbr_parties} current game")
            if len(self.server.match_to_play) > 0:
                for c in self.server.connected_computers:
                    
                    for i in range(int(max(28, int(c.cores)/4) - len(c.actual_games))):
                        self.server.give_match_to(c)
            time.sleep(5)
        
        print("Generation effectue")


if __name__ == '__main__':
    AI()