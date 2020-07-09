class Bit:

    def __init__(self, init_state=0):
        self.state = init_state

    def __repr__(self):
        return '{}'.format(self.state)

    def __add__(self, other):
        return '{}{}'.format(self.state, other)

    def __radd__(self, other):
        return '{}{}'.format(other, self.state)

    def __call__(self, in_bit):
        self.state = in_bit.state

    def update(self, in_bit):
        self.state = in_bit.state


# Transistor
class NANDBit(Bit):
    transistor_count = 0

    def __init__(self, init_state=0):
        super().__init__(init_state)
        NANDBit.transistor_count = NANDBit.transistor_count + 1

    def __call__(self, a, b):
        self.state = int(not (a.state & b.state))


class NOTBit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.Transistor = NANDBit()

    def __call__(self, a):
        self.Transistor(a, a)
        self.update(self.Transistor)


class ANDBit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.Transistor = NANDBit()
        self.Noter = NOTBit()

    def __call__(self, a, b):
        self.Transistor(a, b)
        self.Noter(self.Transistor)
        self.update(self.Noter)


class AND3Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.And1 = ANDBit()
        self.And2 = ANDBit()

    def __call__(self, a, b, c):
        self.And1(a, b)
        self.And2(self.And1, c)
        self.update(self.And2)


class AND4Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.And1 = AND3Bit()
        self.And2 = ANDBit()

    def __call__(self, a, b, c, d):
        self.And1(a, b, c)
        self.And2(self.And1, d)
        self.update(self.And2)


class ORBit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.Transistor = NANDBit()
        self.Not1 = NOTBit()
        self.Not2 = NOTBit()

    def __call__(self, a, b):
        self.Not1(a)
        self.Not2(b)
        self.Transistor(self.Not1, self.Not2)
        self.update(self.Transistor)


class OR3Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.OR1 = ORBit()
        self.OR2 = ORBit()

    def __call__(self, a, b, c):
        self.OR1(a, b)
        self.OR2(self.OR1, c)
        self.update(self.OR2)


class OR4Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.OR1 = OR3Bit()
        self.OR2 = ORBit()

    def __call__(self, a, b, c, d):
        self.OR1(a, b, c)
        self.OR2(self.OR1, d)
        self.update(self.OR2)


class OR5Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.OR1 = OR4Bit()
        self.OR2 = ORBit()

    def __call__(self, a, b, c, d, e):
        self.OR1(a, b, c, d)
        self.OR2(self.OR1, e)
        self.update(self.OR2)


class OR6Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.OR1 = OR5Bit()
        self.OR2 = ORBit()

    def __call__(self, a, b, c, d, e, f):
        self.OR1(a, b, c, d, e)
        self.OR2(self.OR1, f)
        self.update(self.OR2)


class OR8Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.OR1 = OR6Bit()
        self.OR2 = OR3Bit()

    def __call__(self, a1, a2, a3, a4, a5, a6, a7, a8):
        self.OR1(a1, a2, a3, a4, a5, a6)
        self.OR2(self.OR1, a7, a8)
        self.update(self.OR2)


class OR16Bit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.OR0 = OR8Bit()
        self.OR1 = OR8Bit()
        self.OR2 = OR8Bit()

    def __call__(self, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16):
        self.OR0(a1, a2, a3, a4, a5, a6, a7, a8)
        self.OR1(a9, a10, a11, a12, a13, a14, a15, a16)
        self.OR2(self.OR0, self.OR1)
        self.update(self.OR2)


class XORBit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.Trans_in1 = NANDBit()
        self.Trans_in2 = NANDBit()
        self.Trans_Out = NANDBit()
        self.NOT1 = NOTBit()
        self.NOT2 = NOTBit()

    def __call__(self, a, b):
        self.NOT1(a)
        self.Trans_in1(self.NOT1, b)
        self.NOT2(b)
        self.Trans_in2(a, self.NOT2)
        self.Trans_Out(self.Trans_in1, self.Trans_in2)
        self.update(self.Trans_Out)


class MemoryBit(Bit):
    def __init__(self, init_state=0):
        super().__init__(init_state)
        self.Transistor = [NANDBit() for i in range(4)]

    def __call__(self, set_bit, input_bit):
        self.Transistor[0](set_bit, input_bit)
        self.Transistor[1](set_bit, self.Transistor[0])
        self.Transistor[2](self.Transistor[1], self)
        self.Transistor[3](self.Transistor[0], self.Transistor[2])
        self.update(self.Transistor[3])


class AddBit(Bit):
    def __init__(self):
        super().__init__()
        self.XOR_in = XORBit()
        self.XOR_out = XORBit()
        self.AND1 = ANDBit()
        self.AND2 = ANDBit()
        self.carry_out = ORBit()

    def __call__(self, carry_in, input_bit_a, input_bit_b):
        self.XOR_in(input_bit_a, input_bit_b)
        self.XOR_out(carry_in, self.XOR_in)
        self.update(self.XOR_out)

        self.AND1(input_bit_a, input_bit_b)
        self.AND2(carry_in, self.XOR_in)
        self.carry_out(self.AND1, self.AND2)


class CompareBit(Bit):
    def __init__(self):
        super().__init__()
        self.larger = ORBit()
        self.equal = ANDBit()
        self.XOR = XORBit()
        self.NOT = NOTBit()
        self.AND3 = AND3Bit()

    def __call__(self, in_equal, in_larger, input_bit_a, input_bit_b):
        self.XOR(input_bit_a, input_bit_b)
        self.update(self.XOR)

        self.NOT(self)
        self.equal(self.NOT, in_equal)

        self.AND3(input_bit_a, in_equal, self)
        self.larger(in_larger, self.AND3)


class Compare0(Bit):
    def __init__(self, init_state=1):
        super().__init__(init_state)
        self.NOT = NOTBit()
        self.OR = OR8Bit()

    def __call__(self, in_byte):
        self.OR(in_byte.byte[0], in_byte.byte[1], in_byte.byte[2], in_byte.byte[3],
                in_byte.byte[4], in_byte.byte[5], in_byte.byte[6], in_byte.byte[7])
        self.NOT(self.OR)
        self.update(self.NOT)


class EnablerBit(Bit):
    def __init__(self):
        super().__init__()
        self.and_bit = ANDBit()

    def __call__(self, input_bit, enable_bit):
        self.and_bit(input_bit, enable_bit)
        self.state = self.and_bit.state


class RegisterBit(Bit):
    def __init__(self):
        super().__init__()
        self.Enabler = EnablerBit()
        self.Memory = MemoryBit()

    def __call__(self, set_bit, enable_bit, input_bit):
        self.Memory(set_bit, input_bit)
        self.Enabler(self.Memory, enable_bit)
        self.state = self.Enabler.state
