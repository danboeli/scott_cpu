import numpy as np
from bytes import *


def decode4x16(in_bits):
    decode_size = 4
    in_p = np.zeros((decode_size, 2), dtype=np.bool)
    for y in np.arange(decode_size):
        in_p[y][0] = in_bits.byte[y].state
        in_p[y][1] = s_not(in_bits.byte[y].state)

    c_out = np.zeros(2 ** decode_size, dtype=np.bool)

    c_out[0] = s_and4(in_p[0][1], in_p[1][1], in_p[2][1], in_p[3][1])  # 0/0/0/0
    c_out[1] = s_and4(in_p[0][1], in_p[1][1], in_p[2][1], in_p[3][0])  # 0/0/0/1
    c_out[2] = s_and4(in_p[0][1], in_p[1][1], in_p[2][0], in_p[3][1])  # 0/0/1/0
    c_out[3] = s_and4(in_p[0][1], in_p[1][1], in_p[2][0], in_p[3][0])  # 0/0/1/1
    c_out[4] = s_and4(in_p[0][1], in_p[1][0], in_p[2][1], in_p[3][1])  # 0/1/0/0
    c_out[5] = s_and4(in_p[0][1], in_p[1][0], in_p[2][1], in_p[3][0])  # 0/1/0/1
    c_out[6] = s_and4(in_p[0][1], in_p[1][0], in_p[2][0], in_p[3][1])  # 0/1/1/0
    c_out[7] = s_and4(in_p[0][1], in_p[1][0], in_p[2][0], in_p[3][0])  # 0/1/1/1
    c_out[8] = s_and4(in_p[0][0], in_p[1][1], in_p[2][1], in_p[3][1])  # 1/0/0/0
    c_out[9] = s_and4(in_p[0][0], in_p[1][1], in_p[2][1], in_p[3][0])  # 1/0/0/1
    c_out[10] = s_and4(in_p[0][0], in_p[1][1], in_p[2][0], in_p[3][1])  # 1/0/1/0
    c_out[11] = s_and4(in_p[0][0], in_p[1][1], in_p[2][0], in_p[3][0])  # 1/0/1/1
    c_out[12] = s_and4(in_p[0][0], in_p[1][0], in_p[2][1], in_p[3][1])  # 1/1/0/0
    c_out[13] = s_and4(in_p[0][0], in_p[1][0], in_p[2][1], in_p[3][0])  # 1/1/0/1
    c_out[14] = s_and4(in_p[0][0], in_p[1][0], in_p[2][0], in_p[3][1])  # 1/1/1/0
    c_out[15] = s_and4(in_p[0][0], in_p[1][0], in_p[2][0], in_p[3][0])  # 1/1/1/1

    return c_out


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
