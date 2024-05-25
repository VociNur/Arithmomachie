import time
from evaluation import Evaluation
from enums.TypeMessage import TypeMessage

class Match:
    def __init__(self, p1:int, ev1:Evaluation, p2:int, ev2:Evaluation, result:int = -1, date_creation = None) -> None:
        self.date_creation = date_creation
        if self.date_creation == None:
            self.date_creation = time.time()
        self.p1 = p1
        self.ev1 = ev1
        self.p2 = p2
        self.ev2 = ev2
        self.result = result # 0 pour le joueur p1, 1 pour le joueur p2, -1 si pas défini

    def to_string(self):
        encoding_character = "'"
        return f"{self.p1}{encoding_character}{self.ev1.to_string()}{encoding_character}{self.p2}{encoding_character}{self.ev2.to_string()}{encoding_character}{self.result}{encoding_character}{self.date_creation}"

    def __str__(self) -> str:
        encoding_character = "'"
        return f"{self.p1}{encoding_character}{self.ev1.to_string()}{encoding_character}{self.p2}{encoding_character}{self.ev2.to_string()}{encoding_character}{self.result}{encoding_character}{self.date_creation}"

    @classmethod
    def from_string(self, s:str):
        decoding_character = "'"
        ss = s.split(decoding_character)
        if len(ss) != 6:
            raise Exception
        return Match(int(ss[0]), Evaluation.from_string(ss[1]), int(ss[2]), Evaluation.from_string(ss[3]), result=ss[4], date_creation=ss[5])
    
    def __eq__(self, value: object) -> bool:
        eps = 10e-6
        if type(value) is Match:

            #print(self.date_creation)
            #print(value.date_creation)
            return self.p1 == value.p1 and self.p2 == value.p2 and (abs(float(self.date_creation) - float(value.date_creation)) < eps)
        return False

    def to_packet(self):
        self_str = self.to_string()
        return TypeMessage.encode_package(TypeMessage.MATCH, self_str)

def test_class_methom_string(self, s:str): # old function, not updated
        decoding_character = "'"
        ss = s.split(decoding_character)
        if len(ss) != 5:
            raise Exception
        return Match(int(ss[0]), Evaluation.from_string(ss[1]), int(ss[2]), Evaluation.from_string(ss[3]), float(result=ss[4]))

def test_class_method():
    eval = Evaluation(1, 2, 3, 4, 5, 6)
    eval2 = Evaluation(1, 1, 3, 3, 5, 5)
    m = Match(0, eval, 3, eval2, 1)
    time.sleep(1)
    mdiff = Match(0, eval, 3, eval2, 1)
    to_str = m.to_string()
    m2 = Match.from_string(to_str)
    print(m)
    print(m2)
    print(m == m2)
    m.result = -1
    print(m == m2)
    print("faux:", m == mdiff)
    l = [m]
    l.remove(m2)
    print(l)
    print(m.to_packet())

if __name__ == "__main__":
    #ai1 = Evaluation(1, 0, 0, 0, 0, 0)
    #ai2 = Evaluation(-1, 0, 0, 0, 0, 0)
    #win, game = ai1.battle(ai2)
    #game.show_game()
    test_class_method()