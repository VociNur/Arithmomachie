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
white_forms = np.array([
    [n, n, 1, 1, 1, 1, n, n],
    [2, 2, 1, 1, 1, 1, 2, 2],
    [3, 4, 2, 2, 2, 2, 3, 3],
    [3, 3, n, n, n, n, 3, 3]
])
black_forms = np.array([
    [n, n, 1, 1, 1, 1, n, n],
    [2, 2, 1, 1, 1, 1, 2, 2],
    [4, 3, 2, 2, 2, 2, 3, 3],
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
                board[y][x] = np.array((values[y][x], black_forms[5-y][7-x], 1))
            elif 10 <= y < 14:
                board[y][x] = np.array((values[y][x], white_forms[y-10][x], 0))

        else:
            board[y][x] = n


print(board)

b=board.tolist()
np.set_printoptions()
def print_board(board):
    for y in range(16):
        print(y, board[y], ",")

print_board(b)

f = open("boards/game.json", "w")
f.write(json.dumps(board.tolist()))
f.close()
####################################################$$
board = np.full((16, 8, 3), 0)

for y in range(16):
    for x in range(8):
        board[y][x] = n
for i in range(8):
    board[0, i] = (i+1, 1, 0)
for i in range(8):
    board[1, i] = (i+1, 1, 1)
board[3, 3] = (3, 1, 0)
board[4, 4] = (4, 2, 0)
board[5, 5] = (5, 3, 0)
board[6, 6] = (6, 3, 0)
board[8, 4] = (36, 3, 1)
board[11, 2] = (24*3, 3, 0)
board[11, 6] = (24, 3, 1)
board[10, 6] = (18, 3, 1)


f = open("./boards/basics1.json", "w")
f.write(json.dumps(board.tolist()))
f.close()

board = np.full((16, 8, 3), 0)
for y in range(16):
    for x in range(8):
        board[y][x] = n
board[3, 3] = (3, 1, 0)
board[4, 4] = (4, 2, 0)
board[5, 5] = (5, 3, 0)
board[6, 6] = (6, 3, 0)
board[4, 3] = (16, 1, 0)
board[1, 0] = (32, 1, 1)
board[1, 6] = (18, 1, 1)
board[7, 6] = (8, 2, 1)

board[12, 0] = (1, 1, 0)
board[15, 3] = (2, 1, 1)

f = open("./boards/basics2.json", "w")
f.write(json.dumps(board.tolist()))
f.close()