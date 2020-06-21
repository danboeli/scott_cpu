from logic_functions import *
from bits import *
import numpy as np


class Byte:
    size = 8

    def __init__(self):
        self.byte = [Bit() for i in range(self.size)]

    def initial_set(self, data_input):
        for y in np.arange(self.size):
            self.byte[y].state = data_input[self.size-1-y]  # Invert to allow to enter in reading order (last bit first)

    def update(self, input_byte):
        for y in np.arange(self.size):
            self.byte[y].update(input_byte.byte[y])

    def report(self):
        for y in range(self.size-1, -1, -1):
            self.byte[y].report(y)

    def report_byte(self):
        for y in range(self.size):
            self.byte[y].report(self.size-y-1)

    def get_data(self):
        # return self.byte
        return [self.byte[i].state for i in range(self.size)]


class MemoryByte(Byte):

    def __init__(self):
        self.byte = [MemoryBit() for i in range(self.size)]

    def update(self, set_bit, input_byte):
        for y in np.arange(self.size):
            self.byte[y].update(set_bit, input_byte.byte[y])


class Register(Byte):
    def __init__(self):
        super().__init__()
        self.Enabler = Enabler()
        self.Memory = MemoryByte()

    def update(self, set_bit, enable_bit, input_byte):
        self.Memory.update(set_bit, input_byte)
        self.Enabler.update(self.Memory, enable_bit)

        for y in np.arange(self.size):
            self.byte[y].update(self.Enabler.byte[y])


class Nibble(Byte):
    size = 4


class Decoder3x8(Byte):
    def update(self, op1, op2, op3):
        self.byte[0].state = s_and3(s_not(op1.state), s_not(op2.state), s_not(op3.state))  # 0/0/0
        self.byte[1].state = s_and3(s_not(op1.state), s_not(op2.state), op3.state)  # 0/0/1
        self.byte[2].state = s_and3(s_not(op1.state), op2.state, s_not(op3.state))  # 0/1/0
        self.byte[3].state = s_and3(s_not(op1.state), op2.state, op3.state)  # 0/1/1
        self.byte[4].state = s_and3(op1.state, s_not(op2.state), s_not(op3.state))  # 1/0/0
        self.byte[5].state = s_and3(op1.state, s_not(op2.state), op3.state)  # 1/0/1
        self.byte[6].state = s_and3(op1.state, op2.state, s_not(op3.state))  # 1/1/0
        self.byte[7].state = s_and3(op1.state, op2.state, op3.state)  # 1/1/1


class Decoder2x4(Nibble):
    def update(self, op1, op2):
        self.byte[0].state = s_and(s_not(op1.state), s_not(op2.state))  # 0/0
        self.byte[1].state = s_and(s_not(op1.state), op2.state)  # 0/1
        self.byte[2].state = s_and(op1.state, s_not(op2.state))  # 1/0
        self.byte[3].state = s_and(op1.state, op2.state)  # 1/1


class Enabler(Byte):

    def __init__(self):
        self.byte = [Bit() for i in range(self.size)]
        self.and_bit = ANDBit()

    def update(self, input_byte, enable_bit):
        for y in np.arange(self.size):
            self.and_bit.update(input_byte.byte[y], enable_bit)
            self.byte[y].update(self.and_bit)


class CompareByte(Byte):
    size = 8

    def __init__(self):
        self.byte = [CompareBit() for i in range(self.size)]
        self.initial_equal = Bit(1)
        self.initial_larger = Bit(0)
        self.equal = Bit()
        self.larger = Bit()

    def update(self, input_byte_a, input_byte_b):
        self.byte[7].update(self.initial_equal, self.initial_larger, input_byte_a.byte[7], input_byte_b.byte[7])
        self.equal.update(self.byte[7].equal)
        self.larger.update(self.byte[7].larger)
        for y in range(self.size-1-1, -1, -1):
            self.byte[y].update(self.equal, self.larger, input_byte_a.byte[y], input_byte_b.byte[y])
            self.equal.update(self.byte[y].equal)
            self.larger.update(self.byte[y].larger)



class RAMbyte(Byte):
    #  Address is [0-15]x[0-15]
    size = 8

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

    def update(self, set_bit, enable_bit, input_byte, addr_x, addr_y):
        self.Active.update(checkIfactive(addr_x, addr_y, self.x, self.y))
        self.EnableBit.update(self.Active, enable_bit)
        self.SetBit.update(self.Active, set_bit)
        self.Reg.update(self.SetBit, self.EnableBit, input_byte)

        for y in np.arange(self.size):
            self.byte[y].update(self.Reg.byte[y])


class ANDer(Byte):
    def update(self, a_byte, b_byte):
        for x in range(8):
            self.byte[x].state = s_and(a_byte.byte[x].state, b_byte.byte[x].state)


class ORer(Byte):
    def update(self, a_byte, b_byte):
        for x in range(8):
            self.byte[x].state = s_or(a_byte.byte[x].state, b_byte.byte[x].state)


class NOTer(Byte):
    def update(self, a_byte):
        for x in range(8):
            self.byte[x].state = s_not(a_byte.byte[x].state)


class AddByte(Byte):
    size = 8

    def __init__(self):
        self.byte = [AddBit() for i in range(self.size)]
        self.carry_out = Bit()

    def update(self, input_byte_a, input_byte_b, carry_in):
        self.carry_out.update(carry_in)
        for y in range(self.size):
            self.byte[y].update(self.carry_out, input_byte_a.byte[y], input_byte_b.byte[y])
            self.carry_out.update(self.byte[y].carry_out)


class Bus1(Byte):
    def update(self, in_byte, bus1_bit):
        self.byte[0].state = s_or(in_byte.byte[0].state, bus1_bit.state)
        for y in range(1, 8):
            self.byte[y].state=s_and(in_byte.byte[y].state, s_not(bus1_bit.state))


class Bus(Byte):
    def reset(self):
        for y in range(self.size):
            self.byte[y].state = 0

    def update(self, in_byte):

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
