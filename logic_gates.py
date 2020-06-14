from transistor import *


# DERIVED
def s_not(a):
    return s_nand(a, a)


def s_and(a, b):
    return s_not(s_nand(a, b))


def s_and3(a, b, c):
    return s_and(a, s_and(b, c))


def s_and4(a, b, c, d):
    return s_and(a, s_and3(b, c, d))


def s_or(a, b):
    return s_nand(s_not(a), s_not(b))


def s_or3(a, b, c):
    return s_or(a, s_or(b, c))


def s_or8(a1, a2, a3, a4, a5, a6, a7, a8):
    return s_or(
        a1,
        s_or(
            a2,
            s_or(
                a3,
                s_or(
                    a4,
                    s_or(
                        a5,
                        s_or(
                            a6,
                            s_or(a7, a8)
                        )
                    )
                )
            )
        )
    )


def s_or16(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16):
    return s_or(s_or8(a1, a2, a3, a4, a5, a6, a7, a8), s_or8(a9, a10, a11, a12, a13, a14, a15, a16))


def s_xor(a, b):
    return s_nand(s_nand(s_not(a), b), s_nand(a, s_not(b)))


