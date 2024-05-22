from evaluation import Evaluation


class Match:
    def __init__(self, p1:int, ev1:Evaluation, p2:int, ev2:Evaluation) -> None:
        self.p1 = p1
        self.ev1 = ev1
        self.p2 = p2
        self.ev2 = ev2

    def to_string(self):
        encoding_character = "'"
        return f"{self.p1}{encoding_character}{self.ev1.to_string()}{encoding_character}{self.p2}{encoding_character}{self.ev2.to_string()}"

    def __str__(self) -> str:
        encoding_character = "'"
        return f"{self.p1}{encoding_character}{self.ev1.to_string()}{encoding_character}{self.p2}{encoding_character}{self.ev2.to_string()}"

    @classmethod
    def from_string(self, s:str):
        decoding_character = "'"
        ss = s.split(decoding_character)
        if len(ss) != 4:
            raise Exception
        return Match(int(ss[0]), Evaluation.from_string(ss[1]), int(ss[2]), Evaluation.from_string(ss[3]))



def test_class_method():
    eval = Evaluation(1, 2, 3, 4, 5, 6)
    eval2 = Evaluation(1, 1, 3, 3, 5, 5)
    m = Match(0, eval, 3, eval2)
    to_str = m.to_string()
    m2 = Match.from_string(to_str)
    print(m)
    print(m2)
    

if __name__ == "__main__":
    #ai1 = Evaluation(1, 0, 0, 0, 0, 0)
    #ai2 = Evaluation(-1, 0, 0, 0, 0, 0)
    #win, game = ai1.battle(ai2)
    #game.show_game()
    test_class_method()