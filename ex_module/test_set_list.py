from timeit import timeit

n = 50
nbr_test = 100000
li = list(range(n))
se = set(range(n))

list_time = timeit(f'{n//10} in li', number=nbr_test, globals=globals())
print(f'List: {list_time:.6} seconds')

list_time = timeit(f'{n//10} in se', number=nbr_test, globals=globals())
print(f'Set: {list_time:.6} seconds')