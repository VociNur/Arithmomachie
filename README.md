# Arithmomachie

## Règles
Règles : https://drive.google.com/file/d/1rz2AM8FDiBt7dB0C5X6SQ7fvUQAURm1B\
En simplifiée : https://drive.google.com/file/d/1SgY8qkFf8sJHgbqr3B12VM-TsnSlt0Nh/view\
venant de https://rithmomachiaucv.blogspot.com/\

## Représentation
pion : (valeur, forme, équipe, identifiant)\
pack de pion : (y, x, pion)\
-1 = aucun\
Chaque pion a un identifiant, qui peut être utile pour :\
-Le localiser avec "self.location[id]", qui vaut -1 s’il n’est plus en jeu
-Connaître s’il est encore en partie avec "self.is_alive(nid)", qui vérifie si sa location vaut -1
-Connaître sa valeur avec self.value_by_id[id]
-Connaître sa forme avec self.form_by_id[id]
-Connaître son équipe avec self.team_by_id[id]

### formes
- 1 : cercle
- 2 : triangle
- 3 : carré
- 4 : pyramide

### équipes
- 0 : blanche
- 1 : noire

### Attaque
- (y,x) pour normale\
- (y,x,n) pour attaque d’un étage de pyramide\
forme: (TypeAttack, [(y, x, value_of_attack),… ], (y, x, value_attacked))


### Pyramide
blanche :[1, 4, 9, 16, 25, 36]
noire : [-1, 16, 25, 36, 49, 64]

### Type_attack
MEET : bleu foncé - lorsqu’un pion touche un autre pion et qu’ils ont même valeur\
GALLOWS : violet - puissance / racine\
AMBUSH : orange - lorsque deux pions touchent un troisième et +-*/\
ASSAULT : rose - attaque de loin\
PROGRESSION_A/G/H: ? - attaque par progression\
SIEGE : marron - lorsqu’une pièce n’a plus de mouvement régulier\   

### aim/shooter
-Deux dictionnaires qui donnent, pour un identifiant, les identifiants de ceux qui pourraient être attaqué, et de ceux 
qui pourraient l’attaquer\
-plus exactement, chaque élément est associé à deux tableaux :\
+un tableau mêlée, qui considère tous les pions qui sont à une place ou le pion peut attaquer\
+un tableau distance, on ne considère uniquement les pions qui peuvent être tué par assaut


### Neighbours
-les voisins d’un point M est la pièce du Nord, Nord-Est, Est, Sud-Est, Sud, Sud-Ouest, Ouest, Nord-Ouest


### Fausses pièces
La pyramide est composée de pièce qui sont empilées\
Les pyramides ont pour identifiant : blanche id 37, noire id 11\
Et chacune des pièces reçoit aussi un identifiant, allant de 48 à 53 pour la blanche, 54 à 58 pour la noire\
59 pièces au total

