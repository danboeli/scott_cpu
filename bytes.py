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
        for y in range(self.size):
            self.byte[y](input_byte.byte[y])

    def initial_set(self, data_input):
        for y in range(self.size):
            self.byte[y].state = data_input[
                self.size - 1 - y]  # Invert to allow to enter in reading order (last bit first)

    def get_data(self):
        return [self.byte[i].state for i in range(self.size)]


class MemoryByte(Byte):
    def __init__(self):
        self.byte = [MemoryBit() for i in range(self.size)]

    def __call__(self, set_bit, input_byte):
        for y in range(self.size):
            self.byte[y](set_bit, input_byte.byte[y])


class Register(Byte):
    def __init__(self):
        super().__init__()
        self.Enabler = Enabler()
        self.Memory = MemoryByte()

    def __call__(self, set_bit, enable_bit, input_byte):
        self.Memory(set_bit, input_byte)
        self.Enabler(self.Memory, enable_bit)

        for y in range(self.size):
            self.byte[y](self.Enabler.byte[y])


class Nibble(Byte):
    size = 4

    def byte2nibble(self, in_byte, pos='front'):
        if pos == 'back':
            for i in range(4):
                self.byte[i](in_byte.byte[i + 4])
        else:
            for i in range(4):
                self.byte[i](in_byte.byte[i])


class Decoder3x8(Byte):
    def __init__(self):
        super().__init__()
        self.NOT = [NOTBit() for i in range(3)]
        self.AND = [AND3Bit() for i in range(8)]

    def __call__(self, op0, op1, op2):
        self.NOT[0](op0)
        self.NOT[1](op1)
        self.NOT[2](op2)
        self.AND[0](self.NOT[0], self.NOT[1], self.NOT[2])  # 0/0/0
        self.AND[1](self.NOT[0], self.NOT[1], op2)  # 0/0/1
        self.AND[2](self.NOT[0], op1, self.NOT[2])  # 0/1/0
        self.AND[3](self.NOT[0], op1, op2)  # 0/1/1
        self.AND[4](op0, self.NOT[1], self.NOT[2])  # 1/0/0
        self.AND[5](op0, self.NOT[1], op2)  # 1/0/1
        self.AND[6](op0, op1, self.NOT[2])  # 1/1/0
        self.AND[7](op0, op1, op2)  # 1/1/1

        self.byte[0](self.AND[0])  # 0/0/0
        self.byte[1](self.AND[1])  # 0/0/0
        self.byte[2](self.AND[2])  # 0/0/0
        self.byte[3](self.AND[3])  # 0/0/0
        self.byte[4](self.AND[4])  # 0/0/0
        self.byte[5](self.AND[5])  # 0/0/0
        self.byte[6](self.AND[6])  # 0/0/0
        self.byte[7](self.AND[7])  # 0/0/0


class Decoder2x4(Nibble):
    def __init__(self):
        super().__init__()
        self.NOT = [NOTBit() for i in range(2)]
        self.AND = [ANDBit() for i in range(4)]

    def __call__(self, op0, op1):
        self.NOT[0](op0)
        self.NOT[1](op1)

        self.AND[0](self.NOT[0], self.NOT[1])  # 0/0
        self.AND[1](self.NOT[0], op1)  # 0/1
        self.AND[2](op0, self.NOT[1])  # 1/0
        self.AND[3](op0, op1)  # 1/1

        self.byte[0](self.AND[0])  # 0/0/0
        self.byte[1](self.AND[1])  # 0/0/0
        self.byte[2](self.AND[2])  # 0/0/0
        self.byte[3](self.AND[3])  # 0/0/0


class Decoder4x16(Byte):
    size = 16

    def __init__(self):
        super().__init__()
        self.NOT = [NOTBit() for i in range(4)]
        self.AND = [AND4Bit() for i in range(16)]

    def __call__(self, in_bits):
        for i in range(4):
            self.NOT[i](in_bits.byte[i])

        self.AND[0](self.NOT[0], self.NOT[1], self.NOT[2], self.NOT[3])  # 0/0/0/0
        self.AND[1](self.NOT[0], self.NOT[1], self.NOT[2], in_bits.byte[3])  # 0/0/0/1
        self.AND[2](self.NOT[0], self.NOT[1], in_bits.byte[2], self.NOT[3])  # 0/0/1/0
        self.AND[3](self.NOT[0], self.NOT[1], in_bits.byte[2], in_bits.byte[3])  # 0/0/1/1
        self.AND[4](self.NOT[0], in_bits.byte[1], self.NOT[2], self.NOT[3])  # 0/1/0/0
        self.AND[5](self.NOT[0], in_bits.byte[1], self.NOT[2], in_bits.byte[3])  # 0/1/0/1
        self.AND[6](self.NOT[0], in_bits.byte[1], in_bits.byte[2], self.NOT[3])  # 0/1/1/0
        self.AND[7](self.NOT[0], in_bits.byte[1], in_bits.byte[2], in_bits.byte[3])  # 0/1/1/1
        self.AND[8](in_bits.byte[0], self.NOT[1], self.NOT[2], self.NOT[3])  # 1/0/0/0
        self.AND[9](in_bits.byte[0], self.NOT[1], self.NOT[2], in_bits.byte[3])  # 1/0/0/1
        self.AND[10](in_bits.byte[0], self.NOT[1], in_bits.byte[2], self.NOT[3])  # 1/0/1/0
        self.AND[11](in_bits.byte[0], self.NOT[1], in_bits.byte[2], in_bits.byte[3])  # 1/0/1/1
        self.AND[12](in_bits.byte[0], in_bits.byte[1], self.NOT[2], self.NOT[3])  # 1/1/0/0
        self.AND[13](in_bits.byte[0], in_bits.byte[1], self.NOT[2], in_bits.byte[3])  # 1/1/0/1
        self.AND[14](in_bits.byte[0], in_bits.byte[1], in_bits.byte[2], self.NOT[3])  # 1/1/1/0
        self.AND[15](in_bits.byte[0], in_bits.byte[1], in_bits.byte[2], in_bits.byte[3])  # 1/1/1/1

        for i in range(16):
            self.byte[i](self.AND[i])


class Enabler(Byte):
    def __init__(self):
        self.byte = [Bit() for i in range(self.size)]
        self.and_bit = ANDBit()

    def __call__(self, input_byte, enable_bit):
        for y in range(self.size):
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
        for y in range(self.size - 1 - 1, -1, -1):
            self.byte[y](self.equal, self.larger, input_byte_a.byte[y], input_byte_b.byte[y])
            self.equal(self.byte[y].equal)
            self.larger(self.byte[y].larger)


class RAMbyte(Byte):
    #  Address is [0-15]x[0-15]
    def __init__(self, create_addr_x, create_addr_y):
        super().__init__()
        self.Reg = Register()
        self.Active = RAMWiring()
        self.SetBit = ANDBit()
        self.EnableBit = ANDBit()
        self.addr_x = create_addr_x  # x address 0-15
        self.addr_y = create_addr_y  # y address 0-15
        self.x = np.zeros(16, dtype=np.bool)
        self.x[self.addr_x] = True
        self.y = np.zeros(16, dtype=np.bool)
        self.y[self.addr_y] = True

    def __call__(self, set_bit, enable_bit, input_byte, addr_x, addr_y):
        self.Active(decoder2array(addr_x), decoder2array(addr_y), self.x, self.y)
        self.EnableBit(self.Active, enable_bit)
        self.SetBit(self.Active, set_bit)
        self.Reg(self.SetBit, self.EnableBit, input_byte)

        for y in range(self.size):
            self.byte[y](self.Reg.byte[y])


class ANDer(Byte):
    def __init__(self):
        super().__init__()
        self.AND = [ANDBit() for i in range(self.size)]

    def __call__(self, a_byte, b_byte):
        for x in range(self.size):
            self.AND[x](a_byte.byte[x], b_byte.byte[x])
            self.byte[x](self.AND[x])


class ORer(Byte):
    def __init__(self):
        super().__init__()
        self.OR = [ORBit() for i in range(self.size)]

    def __call__(self, a_byte, b_byte):
        for x in range(self.size):
            self.OR[x](a_byte.byte[x], b_byte.byte[x])
            self.byte[x](self.OR[x])


class NOTer(Byte):
    def __init__(self):
        super().__init__()
        self.NOT = [NOTBit() for i in range(self.size)]

    def __call__(self, a_byte):
        for x in range(self.size):
            self.NOT[x](a_byte.byte[x])
            self.byte[x](self.NOT[x])


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
    def __init__(self):
        super().__init__()
        self.OR = ORBit()
        self.NOT = NOTBit()
        self.AND = [ANDBit() for i in range(self.size - 1)]

    def __call__(self, in_byte, bus1_bit):
        self.OR(in_byte.byte[0], bus1_bit)
        self.byte[0](self.OR)
        self.NOT(bus1_bit)
        for y in range(1, 8):
            self.AND[y - 1](self.NOT, in_byte.byte[y])
            self.byte[y](self.AND[y - 1])


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
            self.byte[y].state = in_byte.byte[y].state | self.byte[y].state
            # This is not an OR gate, but just wires
            # that are connected, therefore not modelled with transistors


def decoder2array(a):
    out = np.zeros(16, dtype=np.bool)
    for i in range(16):
        out[i] = a.byte[i].state
    return out


class RAMWiring(Bit):
    def __init__(self):
        super().__init__()
        self.RAM_AND = ANDBit()
        self.Left = Bit()
        self.Right = Bit()

    def __call__(self, a, b, x, y):
        self.Left.state = ((a[0] & x[0]) | (a[1] & x[1]) | (a[2] & x[2]) | (a[3] & x[3]) |
                           (a[4] & x[4]) | (a[5] & x[5]) | (a[6] & x[6]) | (a[7] & x[7]) |
                           (a[8] & x[8]) | (a[9] & x[9]) | (a[10] & x[10]) | (a[11] & x[11]) |
                           (a[12] & x[12]) | (a[13] & x[13]) | (a[14] & x[14]) | (a[15] & x[15]))
        self.Right.state = ((b[0] & y[0]) | (b[1] & y[1]) | (b[2] & y[2]) | (b[3] & y[3]) |
                            (b[4] & y[4]) | (b[5] & y[5]) | (b[6] & y[6]) | (b[7] & y[7]) |
                            (b[8] & y[8]) | (b[9] & y[9]) | (b[10] & y[10]) | (b[11] & y[11]) |
                            (b[12] & y[12]) | (b[13] & y[13]) | (b[14] & y[14]) | (b[15] & y[15]))
        self.RAM_AND(self.Left, self.Right)
        self.update(self.RAM_AND)
        # This class represents the grid wiring of RAMbytes from the decoders which are not actually
        # made of gates, but just connected wires. One one actual gate is used per RAMByte, which is the one
        # ANDing the correct x- and y-connection