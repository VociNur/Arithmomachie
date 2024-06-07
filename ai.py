


from datetime import datetime
import os
import time
from enums.TypeMessage import TypeMessage
from typing import Dict, List
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
        self.save_actual_gen(0, list(self.evaluations.values()))


    def __init__(self) -> None:
        
        self.evaluations : Dict[int, Evaluation] = {}
        #self.init_gen_0() #init
        #return
        self.server = MyServer(50)
        try:
            self.do_AI()
        except Exception as e:
            print(e.with_traceback())
        finally:
            #self.server.stop_server()
            pass
    
    def do_AI(self):
        
        for _ in range(5):
            gen, pop = self.get_population()
            self.evaluations = pop
            print(f"Doing gen {gen}")
            print(f"génération {gen}")
            print(self.evaluations)
            self.do_matches(gen)
            print(self.server.running)
            if not self.server.running:
                return
            
            points = {}
            for i in range(self.get_population_count()):
                points[i] = 0
            
            for m in self.server.registered_result:
                print(m.result)
                if m.result == 0:
                    points[m.p1] += 1
                    continue
                if m.result == 1:
                    points[m.p2] += 1
                    continue
                #print(type(m.result))
                if m.result != -1:
                    raise Exception(f"Match  with result {m.result} !")
            print(points)
            m = max(points.values())
            bests = []
            for key in points.keys():
                if points[key] == m:
                    bests.append(key)

            print(m, bests)
            avg = Evaluation.from_average([self.evaluations[i] for i in bests])
            print(avg)
            for i in range(self.get_population_count()):
                if not i in bests:
                    self.evaluations[i].get_genomes_from(avg)
                #self.evaluations[i].mutate()
                self.evaluations[i].round()
            self.save_actual_gen(gen+1, list(self.evaluations.values()))
            time.sleep(1)
        print("FINITO")

    def get_matches_with_result(self, gen):
        i=-1
        print("avant")
        for path, dirs, files in os.walk("./match_save/"):
            
            for file in files:
                i=i+1
            

        pre = "gen"
        if i != gen:
            print(f"Not good gen {gen}")
            return -1, []
        
        matches = []
        #print(type(matches))
        print("Last gen: ", i)
        with open(f"./match_save/{pre}{i}.txt", "r") as f:
            for line in f.readlines():
                matches.append(Match.from_string(line))
        print("Matches of last gen:")
        for m in matches:
            print(m.to_string())
            print(m.result)
        print("---------------------")
        print(i, matches)
        return i, matches
    
    def save_actual_match(self, gen, m:Match):

        pre = "gen"
        
        with open(f"./match_save/{pre}{gen}.txt", "a") as f:
            f.write(m.to_string() + "\n")
        print("Saved match", m.to_string())
        
    def get_population(self):
        gen=-1
        for path, dirs, files in os.walk("./gen_save/"):
            
            
            for file in files:
                gen=gen+1

        pre = "gen"
        if gen == -1:
            return -1, ()
        pop = {}
        print("Last gen: ", gen)
        with open(f"./gen_save/{pre}{gen}.txt", "r") as f:
            for i, line in enumerate(f.readlines()):
                pop[i] = (Evaluation.from_string(line))
        return gen, pop
    
    def save_actual_gen(self, n_gen, gen:List[Evaluation]):
        pre = "gen"
        
        with open(f"./gen_save/{pre}{n_gen}.txt", "w") as f:
            for g in gen:
                f.write(g.to_string() + "\n")
        print("Saved gen", n_gen)

    #def save_population(self, gen):
    #    dos = "./save_AI/"
    #    now = datetime.now()
    #    f = open(dos + str(now) + " gen " + str(gen) + ".txt", "w")
    #    for i in range(self.population_count):
    #        f.write(self.evaluations[i].to_string() + "\n")
    #    f.close()

    def get_population_count(self):
        return len(self.evaluations)

    def do_matches(self, gen):
        self.server.match_to_play = []
        self.server.result = []
        
        _, matches = self.get_matches_with_result(gen)
        #print("1", matches, type(matches))
        self.server.registered_result = matches
        #print(self.server.registered_result, type(self.server.registered_result))
        print("registered:", self.server.registered_result)
        for i in range(self.get_population_count()):
            for j in range(i):
                match = Match(j, self.evaluations[j], i, self.evaluations[i])
                if match in self.server.registered_result:
                    print("Game already done", match.to_string(), "don't consider the result")
                else:
                    print("Added game", match.to_string(), "dont consider the result")
                    self.server.match_to_play.append(match) #1<=j<i<=n-1

        self.server.nbr_parties = len(self.server.match_to_play)
        print(f"Nombre de joueurs {self.get_population_count()}")
        print(f"Nombre de game totales à recevoir: {self.get_population_count()*(self.get_population_count()-1)/2}")
        
        while self.get_population_count()*(self.get_population_count()-1)/2 != len(self.server.registered_result):
            if not self.server.running:
                return

            print(f"{len(self.server.registered_result)}/{self.server.nbr_parties} finished game")
            print(f"{len(self.server.get_current_matches())}/{self.server.nbr_parties} current game")
            if len(self.server.match_to_play) > 0:
                for c in self.server.connected_computers:
                    
                    if not c.is_connected:
                        self.server.match_to_play += c.actual_games
                        if c in self.server.connected_computers:
                            self.server.connected_computers.remove(c)
                    
                    for g in c.actual_games:
                        if time.time() - g.date_creation > 3600:
                            
                            c.conn.send(TypeMessage.encode_package(TypeMessage.END_CONNECTION, ""))
                            c.is_connected = False
                            time.sleep(1)
                            print("Stopping connection by match undone", g.to_string())

                    if not c.is_connected:
                        self.server.match_to_play += c.actual_games
                        if c in self.server.connected_computers:
                            self.server.connected_computers.remove(c)
                    

                    #for i in range(int(max(2, int(c.cores)/6) - len(c.actual_games))):
                    for i in range(1-len(c.actual_games)): # pas d'autres choix pour l'instant, seul le proc est en PLS
                        try:
                            
                            self.server.give_match_to(c)
                        except Exception as e:
                            print(e.with_traceback())
            for m in self.server.result:
                if not m in self.server.registered_result:
                    #print("type:", type(self.server.registered_result))
                    self.server.registered_result.append(m)
                    self.save_actual_match(gen, m)

            time.sleep(10)

        print("Generation effectue")


if __name__ == '__main__':
    AI()