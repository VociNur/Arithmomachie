a = {"1": 2}

if a["1"]:
    print(a["1"])

if "1" in a:
    print("ok")

if "2" in a:
    print("non ok")

print(a.values())