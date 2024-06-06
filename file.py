import os

from match import Match

def get_actual_matches():
    i=-1
    for path, dirs, files in os.walk("./match_save/"):
        i=i+1

    pre = "gen"
    if i == -1:
        return -1, ()
    matches = []
    print("Last gen: ", i)
    with open(f"./match_save/{pre}{i}.txt") as f:
        for line in f.readlines():
            matches.append(Match.from_string(line))
    print("Matches of last gen:")
    for m in matches:
        print(m.to_string())
        print(m.result)
    print("---------------------")
    return i, matches
    

def save_actual_match(gen, m:Match):
    i=-1
    for path, dirs, files in os.walk("./match_save/"):
        i=i+1

    pre = "gen"
    
    print("Last gen: ", i)
    with open(f"./match_save/{pre}{i}.txt", "a+") as f:
        f.write(m.to_string() + "\n")
    print("Saved match", m.to_string())

m = Match.from_string("0'0.0/0.0/0.0/0.0/0.0/0.0'1'1.0/0.0/0.0/0.0/0.0/0.0'0'1717501197.1094863")
#i, matches = get_actual_matches()
save_actual_match(0, m)
