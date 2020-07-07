# from logic_functions import *
from bits import *
import numpy as np


class Byte:
    size = 8

    def __init__(self):
        self.byte = [Bit() for i in range(self.size)]

    def __repr__(self, order='number'):
        bytestring = ''
        count = 0
        if order == 'byte':
            for i in range(self.size):
                count = count + 1
                bytestring = bytestring + '{}'.format(self.byte[i])
                if (count % 4 == 0) & (i < self.size - 1):
                    bytestring = bytestring + ' '
        else:
            for i in range(self.size - 1, -1, -1):
                count = count + 1
                bytestring = bytestring + '{}'.format(self.byte[i])
                if (count % 4 == 0) & (i > 0):
                    bytestring = bytestring + ' '
        return bytestring

    def __add__(self, other, order='number'):
        return self.__repr__(order) + other

    def __radd__(self, other, order='number'):
        return other + self.__repr__(order)

    def __call__(self, input_byte):
        for y in np.arange(self.size):
            self.byte[y](input_byte.byte[y])

    def initial_set(self, data_input):
        for y in np.arange(self.size):
            self.byte[y].state = data_input[self.size-1-y]  # Invert to allow to enter in reading order (last bit first)

    def get_data(self):
        return [self.byte[i].state for i in range(self.size)]


class MemoryByte(Byte):
    def __init__(self):
        self.byte = [MemoryBit() for i in range(self.size)]

    def __call__(self, set_bit, input_byte):
        for y in np.arange(self.size):
            self.byte[y](set_bit, input_byte.byte[y])


class Register(Byte):
    def __init__(self):
        super().__init__()
        self.Enabler = Enabler()
        self.Memory = MemoryByte()

    def __call__(self, set_bit, enable_bit, input_byte):
        self.Memory(set_bit, input_byte)
        self.Enabler(self.Memory, enable_bit)

        for y in np.arange(self.size):
            self.byte[y](self.Enabler.byte[y])


class Nibble(Byte):
    size = 4

    def byte2nibble(self, in_byte, pos='front'):
        if pos == 'back':
            for i in range(4):
                self.byte[i](in_byte.byte[i+4])
        else:
            for i in range(4):
                self.byte[i](in_byte.byte[i])


class Decoder3x8(Byte):
    def __call__(self, op1, op2, op3):
        self.byte[0].state = s_and3(s_not(op1.state), s_not(op2.state), s_not(op3.state))  # 0/0/0
        self.byte[1].state = s_and3(s_not(op1.state), s_not(op2.state), op3.state)  # 0/0/1
        self.byte[2].state = s_and3(s_not(op1.state), op2.state, s_not(op3.state))  # 0/1/0
        self.byte[3].state = s_and3(s_not(op1.state), op2.state, op3.state)  # 0/1/1
        self.byte[4].state = s_and3(op1.state, s_not(op2.state), s_not(op3.state))  # 1/0/0
        self.byte[5].state = s_and3(op1.state, s_not(op2.state), op3.state)  # 1/0/1
        self.byte[6].state = s_and3(op1.state, op2.state, s_not(op3.state))  # 1/1/0
        self.byte[7].state = s_and3(op1.state, op2.state, op3.state)  # 1/1/1


class Decoder2x4(Nibble):
    def __call__(self, op1, op2):
        self.byte[0].state = s_and(s_not(op1.state), s_not(op2.state))  # 0/0
        self.byte[1].state = s_and(s_not(op1.state), op2.state)  # 0/1
        self.byte[2].state = s_and(op1.state, s_not(op2.state))  # 1/0
        self.byte[3].state = s_and(op1.state, op2.state)  # 1/1


class Decoder4x16(Byte):
    decode_size = 4
    size = 16

    def __call__(self, in_bits):
        in_p = np.zeros((Decoder4x16.decode_size, 2), dtype=np.bool)
        for y in np.arange(Decoder4x16.decode_size):
            in_p[y][0] = in_bits.byte[y].state
            in_p[y][1] = s_not(in_bits.byte[y].state)

        self.byte[0].state = s_and4(in_p[0][1], in_p[1][1], in_p[2][1], in_p[3][1])  # 0/0/0/0
        self.byte[1].state = s_and4(in_p[0][1], in_p[1][1], in_p[2][1], in_p[3][0])  # 0/0/0/1
        self.byte[2].state = s_and4(in_p[0][1], in_p[1][1], in_p[2][0], in_p[3][1])  # 0/0/1/0
        self.byte[3].state = s_and4(in_p[0][1], in_p[1][1], in_p[2][0], in_p[3][0])  # 0/0/1/1
        self.byte[4].state = s_and4(in_p[0][1], in_p[1][0], in_p[2][1], in_p[3][1])  # 0/1/0/0
        self.byte[5].state = s_and4(in_p[0][1], in_p[1][0], in_p[2][1], in_p[3][0])  # 0/1/0/1
        self.byte[6].state = s_and4(in_p[0][1], in_p[1][0], in_p[2][0], in_p[3][1])  # 0/1/1/0
        self.byte[7].state = s_and4(in_p[0][1], in_p[1][0], in_p[2][0], in_p[3][0])  # 0/1/1/1
        self.byte[8].state = s_and4(in_p[0][0], in_p[1][1], in_p[2][1], in_p[3][1])  # 1/0/0/0
        self.byte[9].state = s_and4(in_p[0][0], in_p[1][1], in_p[2][1], in_p[3][0])  # 1/0/0/1
        self.byte[10].state = s_and4(in_p[0][0], in_p[1][1], in_p[2][0], in_p[3][1])  # 1/0/1/0
        self.byte[11].state = s_and4(in_p[0][0], in_p[1][1], in_p[2][0], in_p[3][0])  # 1/0/1/1
        self.byte[12].state = s_and4(in_p[0][0], in_p[1][0], in_p[2][1], in_p[3][1])  # 1/1/0/0
        self.byte[13].state = s_and4(in_p[0][0], in_p[1][0], in_p[2][1], in_p[3][0])  # 1/1/0/1
        self.byte[14].state = s_and4(in_p[0][0], in_p[1][0], in_p[2][0], in_p[3][1])  # 1/1/1/0
        self.byte[15].state = s_and4(in_p[0][0], in_p[1][0], in_p[2][0], in_p[3][0])  # 1/1/1/1


class Enabler(Byte):
    def __init__(self):
        self.byte = [Bit() for i in range(self.size)]
        self.and_bit = ANDBit()

    def __call__(self, input_byte, enable_bit):
        for y in np.arange(self.size):
            self.and_bit(input_byte.byte[y], enable_bit)
            self.byte[y](self.and_bit)


class CompareByte(Byte):
    def __init__(self):
        self.byte = [CompareBit() for i in range(self.size)]
        self.initial_equal = Bit(1)
        self.initial_larger = Bit(0)
        self.equal = Bit()
        self.larger = Bit()

    def __call__(self, input_byte_a, input_byte_b):
        self.byte[7](self.initial_equal, self.initial_larger, input_byte_a.byte[7], input_byte_b.byte[7])
        self.equal(self.byte[7].equal)
        self.larger(self.byte[7].larger)
        for y in range(self.size-1-1, -1, -1):
            self.byte[y](self.equal, self.larger, input_byte_a.byte[y], input_byte_b.byte[y])
            self.equal(self.byte[y].equal)
            self.larger(self.byte[y].larger)



class RAMbyte(Byte):
    #  Address is [0-15]x[0-15]
    def __init__(self, create_addr_x, create_addr_y):
        super().__init__()
        self.Reg = Register()
        self.Active = Bit()
        self.SetBit = ANDBit()
        self.EnableBit = ANDBit()
        self.addr_x = create_addr_x  # x address 0-15
        self.addr_y = create_addr_y  # y address 0-15
        self.x = np.zeros(16, dtype=np.bool)
        self.x[self.addr_x] = True
        self.y = np.zeros(16, dtype=np.bool)
        self.y[self.addr_y] = True

    def __call__(self, set_bit, enable_bit, input_byte, addr_x, addr_y):
        self.Active(checkIfactive(decoder2array(addr_x), decoder2array(addr_y), self.x, self.y))
        self.EnableBit(self.Active, enable_bit)
        self.SetBit(self.Active, set_bit)
        self.Reg(self.SetBit, self.EnableBit, input_byte)

        for y in np.arange(self.size):
            self.byte[y](self.Reg.byte[y])


class ANDer(Byte):
    def __call__(self, a_byte, b_byte):
        for x in range(8):
            self.byte[x].state = s_and(a_byte.byte[x].state, b_byte.byte[x].state)


class ORer(Byte):
    def __call__(self, a_byte, b_byte):
        for x in range(8):
            self.byte[x].state = s_or(a_byte.byte[x].state, b_byte.byte[x].state)


class NOTer(Byte):
    def __call__(self, a_byte):
        for x in range(8):
            self.byte[x].state = s_not(a_byte.byte[x].state)


class AddByte(Byte):
    def __init__(self):
        self.byte = [AddBit() for i in range(self.size)]
        self.carry_out = Bit()

    def __call__(self, input_byte_a, input_byte_b, carry_in):
        self.carry_out(carry_in)
        for y in range(self.size):
            self.byte[y](self.carry_out, input_byte_a.byte[y], input_byte_b.byte[y])
            self.carry_out(self.byte[y].carry_out)


class Bus1(Byte):
    def __call__(self, in_byte, bus1_bit):
        self.byte[0].state = s_or(in_byte.byte[0].state, bus1_bit.state)
        for y in range(1, 8):
            self.byte[y].state=s_and(in_byte.byte[y].state, s_not(bus1_bit.state))


class Bus(Byte):
    def reset(self):
        for y in range(self.size):
            self.byte[y].state = 0

    def __call__(self, in_byte):

        # Debug Section
        selfsum = 0
        testsum = 0
        compsum = 0
        for y in range(self.size):
            selfsum = selfsum + self.byte[y].state
            testsum = testsum + in_byte.byte[y].state
            if self.byte[y].state != in_byte.byte[y].state:
                compsum = compsum + 1
        if (selfsum > 0) & (testsum > 0) & (compsum > 0):
            print("Warning: Bus Override!")

        # Functional Section
        for y in range(self.size):
            self.byte[y].state = s_or(in_byte.byte[y].state, self.byte[y].state)


def decoder2array(a):
    out = np.zeros(16, dtype=np.bool)
    for i in range(16):
        out[i] = a.byte[i].state
    return out


def checkIfactive(a, b, x, y):
    active = Bit()
    active.state = s_and(
        s_or16(
            s_and(a[0], x[0]),
            s_and(a[1], x[1]),
            s_and(a[2], x[2]),
            s_and(a[3], x[3]),
            s_and(a[4], x[4]),
            s_and(a[5], x[5]),
            s_and(a[6], x[6]),
            s_and(a[7], x[7]),
            s_and(a[8], x[8]),
            s_and(a[9], x[9]),
            s_and(a[10], x[10]),
            s_and(a[11], x[11]),
            s_and(a[12], x[12]),
            s_and(a[13], x[13]),
            s_and(a[14], x[14]),
            s_and(a[15], x[15])
        ),
        s_or16(
            s_and(b[0], y[0]),
            s_and(b[1], y[1]),
            s_and(b[2], y[2]),
            s_and(b[3], y[3]),
            s_and(b[4], y[4]),
            s_and(b[5], y[5]),
            s_and(b[6], y[6]),
            s_and(b[7], y[7]),
            s_and(b[8], y[8]),
            s_and(b[9], y[9]),
            s_and(b[10], y[10]),
            s_and(b[11], y[11]),
            s_and(b[12], y[12]),
            s_and(b[13], y[13]),
            s_and(b[14], y[14]),
            s_and(b[15], y[15])
        )
    )
    return active
