def a(l: list):
    l.append("a")

liste = []
a(liste)
print(liste)

dico = {}
dico[1] = ["a","b"]
dico[1].remove("b")

print(dico)
print(dico[3])