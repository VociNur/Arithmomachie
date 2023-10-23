import numpy as np
import json
n = -1
bord = np.array([[n for _ in range(8)] for _ in range(2)])
black = np.array([
    [49, 121, n, n, n, n, 225, 163],
    [28, 66, 36, 30, 59, 64, 120, 190],
    [16, 12, 9, 25, 49, 81, 90, 100],
    [n, n, 3, 5, 7, 9, n, n]
])
mid = np.array([[n for _ in range(8)] for _ in range(4)])
white = np.array([
    [n, n, 8, 6, 4, 2, n, n],
    [81, 72, 64, 36, 16, 4, 6, 9],
    [153, 91, 49, 42, 20, 25, 45, 15],
    [289, 169, n, n, n, n, 81, 25]
])
values = np.concatenate((bord, black, mid, white, bord))

# rond = 1, triangle = 2, carré = 3, pyramide = 4
forms = np.array([
    [n, n, 1, 1, 1, 1, n, n],
    [2, 2, 1, 1, 1, 1, 2, 2],
    [3, 4, 2, 2, 2, 2, 3, 3],
    [3, 3, n, n, n, n, 3, 3]
])

print(values)
print(white)
print(black)
print(values[0, 0])

print("-----")
print(values)




board = np.full((16, 8, 3), 0)
for y in range(16):
    for x in range(8):
        if values[y][x] != n:
            if 2 <= y < 6:
                board[y][x] = np.array((values[y][x], forms[5-y][7-x], 1))
            elif 10 <= y < 14:
                board[y][x] = np.array((values[y][x], forms[y-10][x], 0))

        else:
            board[y][x] = n


print(board)

b=board.tolist()
np.set_printoptions()
def print_board(board):
    for y in range(16):
        print(y, board[y], ",")

print_board(b)

f = open("game.json", "w")
f.write(json.dumps(board.tolist()))
f.close()
####################################################$$
board = np.full((16, 8, 3), 0)

for y in range(16):
    for x in range(8):
        board[y][x] = n
board[0, 0] = (1, 1, 0)
board[3, 3] = (3, 1, 0)
board[4, 4] = (4, 2, 0)
board[5, 5] = (5, 3, 0)
board[6, 6] = (6, 3, 0)


f = open("basic.json", "w")
f.write(json.dumps(board.tolist()))
f.close()