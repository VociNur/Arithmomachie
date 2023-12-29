import numpy as np

def a(l: list):
    l.append("a")

liste = []
a(liste)
print(liste)

dico = {}
dico[1] = ["a","b"]
dico[1].remove("b")

print(dico)

app = [1]
app.append([2])
print(app)

num = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

print(num[0][0])
print(num[(0, 0)])

def testappend(l):
    l.append(5)


l = []
testappend(l)
print(l)