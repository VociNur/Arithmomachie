import numpy as np

array = np.array([0,0,-1,1,2,3,-1,0])

nonzero_indx = np.argwhere((array==-1)|(array==1)).squeeze()
print(array)
print(nonzero_indx)