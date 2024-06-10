import timeit


code = """
def test():
    print("lol")
test()
"""

def test():
    print("lol")

if __name__ == "__main__":
    t = timeit.timeit("test()", number=1000)

    t = timeit.Timer("test()", "from __main__ import fib")
    print(t.timeit(number=1000))