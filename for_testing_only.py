import numpy as np
pointer_bin = np.zeros(8)
print(pointer_bin)
pointer_bin = np.array([int(x) for x in list('{0:0b}'.format(0))])
print(pointer_bin)
pointer = np.array([0, 0, 0, 0, 0, 0, 0, 0])
for i in range(8-len(pointer_bin), 8):
    pointer[i] = pointer_bin[i-8+len(pointer_bin)]