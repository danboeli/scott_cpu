
from bytes import *








def s_xor_byte(a, b):
    b_out = Byte()
    for x in range(8):
        b_out.byte[x].state = s_xor(a.byte[x].state, b.byte[x].state)
    return b_out
