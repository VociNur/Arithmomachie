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

board = np.full((16, 8, 4), 0)
nid = 0
for y in range(16):
    for x in range(8):
        if values[y][x] != n:
            if 2 <= y < 6:
                board[y][x] = np.array((values[y][x], black_forms[5 - y][7 - x], 1, nid))
            elif 10 <= y < 14:
                board[y][x] = np.array((values[y][x], white_forms[y - 10][x], 0, nid))
            nid+=1
        else:
            board[y][x] = n

print(board)

b = board.tolist()
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
for i in range(8):
    board[0, i] = (i + 1, 1, 0)
for i in range(8):
    board[1, i] = (i + 1, 1, 1)
board[3, 3] = (3, 1, 0)
board[4, 4] = (4, 2, 0)
board[5, 5] = (5, 3, 0)
board[6, 6] = (6, 3, 0)
board[8, 4] = (36, 3, 1)
board[11, 2] = (24 * 3, 3, 0)
board[11, 6] = (24, 3, 1)
board[10, 6] = (18, 3, 1)

f = open("basics1.json", "w")
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

f = open("basics2.json", "w")
f.write(json.dumps(board.tolist()))
f.close()

board = np.full((16, 8, 3), 0)
for y in range(16):
    for x in range(8):
        board[y][x] = n

j, i = 3, 3
board[j, i] = (100, 1, 1)
board[j + 1, i + 1] = (1, 1, 0)
board[j - 1, i + 1] = (1, 1, 0)
board[j + 1, i - 1] = (1, 1, 0)
board[j - 1, i - 1] = (1, 1, 0)

j, i = 8, 3

board[j, i] = (100, 1, 1)
board[j + 1, i + 1] = (1, 1, 0)
board[j - 1, i + 1] = (1, 1, 0)
board[j + 1, i - 1] = (1, 1, 0)
board[j - 1, i - 1] = (1, 1, 0)

f = open("basics3.json", "w")
f.write(json.dumps(board.tolist()))
f.close()

value_by_id = {}
form_by_id = {}
team_by_id = {}

i = 0
# tab value ok
forms = np.concatenate((bord, np.flip(black_forms), mid, white_forms, bord))

for y in range(16):
    for x in range(8):
        if values[y][x] == n:
            continue
        value_by_id[i] = values[y][x]
        form_by_id[i] = forms[y][x]
        team_by_id[i] = 1 if i < 24 else 0
        i = i + 1

for j in range(1, 6+1):
    value_by_id[j+47] = j*j
    form_by_id[j+47] = (j-1)//2+1
    team_by_id[j+47] = 0

for j in range(2, 5+2):
    value_by_id[j+52] = (j+2)*(j+2)
    form_by_id[j+52] = (j-1)//2+1
    team_by_id[j+52] = 1

print(value_by_id)
print(form_by_id)
print(team_by_id)
