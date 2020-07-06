
from bytes import *




def byte2nibble(in_byte):
    n_out = [Nibble() for i in range(2)]
    for y in range(4):
        n_out[0].byte[y](in_byte.byte[y])
        n_out[1].byte[y](in_byte.byte[y+4])
    return n_out



def s_xor_byte(a, b):
    b_out = Byte()
    for x in range(8):
        b_out.byte[x].state = s_xor(a.byte[x].state, b.byte[x].state)
    return b_out
