


from datetime import datetime
import time
from typing import Dict
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
        self.evaluations : Dict[int, Evaluation] = {}
        self.population_count = 0
        self.server = MyServer(3)
        try:
            self.do_AI()
        except Exception as e:
            print(e.format_exc())
        finally:
            self.server.stop_server()
    
    def do_AI(self):
        self.init_gen_0()
        for gen in range(5):
            print(f"génération {gen}")
            self.do_matches()
            if not self.server.running:
                return
            
            points = {}
            for i in range(self.population_count):
                points[i] = 0
            
            for m in self.server.result:
                if m.result == 0:
                    points[m.p1] += 1
                    continue
                if m.result == 1:
                    points[m.p2] += 1
                    continue
                print(type(m.result))
                raise Exception(f"Match  with result {m.result} !")
            m = max(points.values())
            bests = []
            for key in points.keys():
                if points[key] == m:
                    bests.append(key)

            print(m, bests)
            avg = Evaluation.from_average([self.evaluations[i] for i in bests])
            print(avg)
            for i in range(self.population_count):
                if not i in bests:
                    self.evaluations[i].get_genomes_from(avg)
                #self.evaluations[i].mutate()
                self.evaluations[i].round()
            self.save_population(gen)
        print("FINITO")

    def save_population(self, gen):
        dos = "./save_AI/"
        now = datetime.now()
        f = open(dos + str(now) + " gen " + str(gen) + ".txt", "w")
        for i in range(self.population_count):
            f.write(self.evaluations[i].to_string() + "\n")
        f.close()

    def do_matches(self):
        self.server.match_to_play = []
        self.server.result = []
        for i in range(self.population_count):
            for j in range(i):
                match = Match(j, self.evaluations[j], i, self.evaluations[i])
                self.server.match_to_play.append(match) #1<=j<i<=n-1
        self.server.nbr_parties = len(self.server.match_to_play)
        print(f"Nombre de parties à jouer: {self.server.match_to_play }")

        while self.server.nbr_parties != len(self.server.result):
            if not self.server.running:
                return

            print(f"{len(self.server.result)}/{self.server.nbr_parties} finished game")
            print(f"{len(self.server.get_current_matches())}/{self.server.nbr_parties} current game")
            if len(self.server.match_to_play) > 0:
                for c in self.server.connected_computers:
                    if not c.is_connected:
                        self.server.match_to_play += c.actual_games
                        self.server.connected_computers.remove(c)
                    #for i in range(int(max(2, int(c.cores)/6) - len(c.actual_games))):
                    for i in range(1-len(c.actual_games)): # pas d'autres choix pour l'instant, seul le proc est en PLS
                        self.server.give_match_to(c)
            time.sleep(2)

        print("Generation effectue")


if __name__ == '__main__':
    AI()