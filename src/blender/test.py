import math
import numpy as np

x=1
y=1
w=180*np.arcsin(x/y)/np.pi
print(x,y,w)
for x in [-1, 1]:
    for y in [-1, 1]:
        w=180*np.arcsin(x/y)/np.pi
        print(x,y,w)