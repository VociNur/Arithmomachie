from json import loads
import time
from numba.experimental import jitclass
from numba import int32, float32, objmode
import numba

import numpy as np

t_dic = numba.typed.Dict.empty(
            key_type=int32,
            value_type=int32
        )

spec = [
    ("test", int32),
    ("ti", float32),
    ("np", int32[:]),
    ("str", numba.typeof(np.array([2]))),
    ("rl", numba.typeof(np.full((1, 1), 1))),
    ("board", numba.typeof(np.full((1, 1), 1)))
]
@jitclass(spec)
class Test():
    def func(self) -> None:
        print("lol")
        self.test = 2


    def test_file(self):
        with objmode():
            f = open("./ex_module/id_board.json", "r")
            data = loads(f.read())
            f.close()
            print(data)
 
            self.board = np.array(data)

    def __init__(self) -> None:
        self.test = 2
        with objmode():
            self.ti = time.time()
        
        print(self.test, self.ti)
        self.np = np.array([2, 2], dtype=int32) # cannot be in objmode
        print(self.np)
        self.func()
        self.str = np.array([2])
        self.rl = np.full((3, 3), 1)
        print(self.rl)
        self.board = np.full((1, 1), 1)
        np.equal(self.np, -1).all()

           
        print("test")
        self.test_file()
        

        
        


if __name__ == "__main__":
    Test()