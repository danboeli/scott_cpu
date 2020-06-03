#Simulation of the Scott CPU / Scott Computer
import numpy as np


# FUNDAMENTAL
def s_nand(a, b):
    return int(not (a & b))


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


class Bit:
    def __init__(self, init_state=0):
        self.state = init_state

    def update(self, in_bit):
        self.state = in_bit.state

    def report(self, pos=0):
        print(self.state, end=(" " if pos == 4 else ""))
        if pos == 0:
            print("")


class MemoryBit(Bit):

    def update(self, set_bit, input_bit):
        # print("Updating bit state {} with set={} and input={}".format(self.state, set_bit, input_bit))
        one = s_nand(set_bit, input_bit)
        two = s_nand(set_bit, one)
        four = s_nand(two, self.state)
        three = s_nand(one, four)
        self.state = three


class Byte(Bit):
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

    def get_data(self):
        return self.byte


class MemoryByte:
    size = 8

    def __init__(self):
        self.byte = [MemoryBit() for i in range(self.size)]

    def report(self):
        for y in np.arange(self.size):
            print(int(self.byte[y].state), end=" ")
        print("")

    def update(self, set_bit, input_byte):
        for y in np.arange(self.size):
            self.byte[y].update(set_bit, int(input_byte.data[y]))

    def get_data(self):
        out = np.zeros(self.size, dtype=np.bool)
        for y in np.arange(self.size):
            out[y] = self.byte[y].state
        return out


class Register(MemoryByte):
    def get_data(self, enable_bit):
        out = np.zeros(self.size)
        for y in np.arange(self.size):
            out[y] = s_and(int(enable_bit), int(self.byte[y].state))
        return out


class Nibble(Byte):
    size = 4


def decode2x4(in_bits):
    decode_size = 2
    in_p = np.zeros((decode_size, 2), dtype=np.bool)
    for y in np.arange(decode_size):
        in_p[y][0] = in_bits[y]
        in_p[y][1] = s_not(in_bits[y])

    c_out = np.zeros(2 ** decode_size, dtype=np.bool)

    c_out[0] = s_and(in_p[0][1], in_p[1][1])  # 0/0
    c_out[1] = s_and(in_p[0][1], in_p[1][0])  # 0/1
    c_out[2] = s_and(in_p[0][0], in_p[1][1])  # 1/0
    c_out[3] = s_and(in_p[0][0], in_p[1][0])  # 1/1

    return c_out


def decode3x8(in_bits):
    decode_size = 3
    in_p = np.zeros((decode_size, 2), dtype=np.bool)
    for y in np.arange(decode_size):
        in_p[y][0] = in_bits[y]
        in_p[y][1] = s_not(in_bits[y])

    c_out = np.zeros(2 ** decode_size, dtype=np.bool)

    c_out[0] = s_and3(in_p[0][1], in_p[1][1], in_p[2][1])  # 0/0/0
    c_out[1] = s_and3(in_p[0][1], in_p[1][1], in_p[2][0])  # 0/0/1
    c_out[2] = s_and3(in_p[0][1], in_p[1][0], in_p[2][1])  # 0/1/0
    c_out[3] = s_and3(in_p[0][1], in_p[1][0], in_p[2][0])  # 0/1/1
    c_out[4] = s_and3(in_p[0][0], in_p[1][1], in_p[2][1])  # 1/0/0
    c_out[5] = s_and3(in_p[0][0], in_p[1][1], in_p[2][0])  # 1/0/1
    c_out[6] = s_and3(in_p[0][0], in_p[1][0], in_p[2][1])  # 1/1/0
    c_out[7] = s_and3(in_p[0][0], in_p[1][0], in_p[2][0])  # 1/1/1

    return c_out


class Decoder3x8(Byte):
    decode_size = 3

    def update(self, op1, op2, op3):
        self.byte[0].state = s_and3(s_not(op1.state), s_not(op2.state), s_not(op3.state))  # 0/0/0
        self.byte[1].state = s_and3(s_not(op1.state), s_not(op2.state), op3.state)  # 0/0/1
        self.byte[2].state = s_and3(s_not(op1.state), op2.state, s_not(op3.state))  # 0/1/0
        self.byte[3].state = s_and3(s_not(op1.state), op2.state, op3.state)  # 0/1/1
        self.byte[4].state = s_and3(op1.state, s_not(op2.state), s_not(op3.state))  # 1/0/0
        self.byte[5].state = s_and3(op1.state, s_not(op2.state), op3.state)  # 1/0/1
        self.byte[6].state = s_and3(op1.state, op2.state, s_not(op3.state))  # 1/1/0
        self.byte[7].state = s_and3(op1.state, op2.state, op3.state)  # 1/1/1


def decode4x16(in_bits):
    decode_size = 4
    in_p = np.zeros((decode_size, 2), dtype=np.bool)
    for y in np.arange(decode_size):
        in_p[y][0] = in_bits[y]
        in_p[y][1] = s_not(in_bits[y])

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


def byte2nibble(byte):
    n_out = [Nibble() for i in range(2)]
    n_out[0].update(byte.get_data()[:4])
    n_out[1].update(byte.get_data()[4:])
    return n_out


def checkIfactive(a,b,x,y):
    active = s_and(
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


class RAMbyte(Register):
    #  Address is [0-15]x[0-15]
    size = 8

    def __init__(self, create_addr_x, create_addr_y):
        self.byte = [MemoryBit() for i in range(self.size)]

        self.addr_x = create_addr_x
        self.addr_y = create_addr_y
        self.x = np.zeros(16, dtype=np.bool)
        self.x[self.addr_x] = True
        self.y = np.zeros(16, dtype=np.bool)
        self.y[self.addr_y] = True

        # nibbles = byte2nibble(address)
        # self.x = decode4x16(nibbles[0].get_data())  # unique 8-array
        # self.y = decode4x16(nibbles[1].get_data())  # unique 8-array

    def update(self, set_bit, input_byte, address):
        nibbles = byte2nibble(address)
        addr_x = decode4x16(nibbles[0].get_data())  # unique 8-array
        addr_y = decode4x16(nibbles[1].get_data())  # unique 8-array

        active = checkIfactive(addr_x, addr_y, self.x, self.y)

        for y in np.arange(self.size):
            self.byte[y].update(s_and(set_bit, active), int(input_byte.data[y]))

    def get_data(self, enable_bit, address):
        nibbles = byte2nibble(address)
        addr_x = decode4x16(nibbles[0].get_data())  # unique 8-array
        addr_y = decode4x16(nibbles[1].get_data())  # unique 8-array

        active = checkIfactive(addr_x, addr_y, self.x, self.y)

        self.out = Byte()

        for y in np.arange(self.size):
            self.out.byte[y].state = s_and(s_and(active, enable_bit), int(self.byte[y].state))
        return out


class ANDBit(Bit):
    def update(self, a_bit, b_bit):
        self.state = s_not(s_nand(a_bit.state, b_bit.state))


class ORBit(Bit):
    def update(self, a_bit, b_bit):
        self.state = s_or(a_bit.state, b_bit.state)


class OR3Bit(Bit):
    def update(self, a_bit, b_bit, c_bit):
        self.state = s_or3(a_bit.state, b_bit.state, c_bit.state)


def s_xor_byte(a, b):
    b_out = Byte()
    for x in range(8):
        b_out.data[x] = s_xor(a.data[x], b.data[x])
    return b_out


class RAM256byte:
    size = 16

    def __init__(self):
        self.RAM = [RAMbyte(x, y) for x, y in np.ndindex(self.size, self.size)]

    def update(self, set_bit, input_byte, address):
        for x in range(self.size ** 2):
            self.RAM[x].update(set_bit, input_byte, address)

    def get_data(self, enable_bit, address):
        # cum_out = Byte()
        cum_out = ORer()
        c_out = Byte()
        for x in range(self.size ** 2):
            c_out = self.RAM[x].get_data(enable_bit, address)
            cum_out.update(cum_out, c_out)
        #     cum_out = s_or_byte(cum_out, c_out)
        #
        # return cum_out


class RightShift(Byte):

    def __init__(self):
        super().__init__()
        self.shift_out = Bit()

    def update(self, in_byte, shift_in):
        self.shift_out.update(in_byte.byte[0])
        for i in range(0, 7):
            self.byte[i].update(in_byte.byte[i+1])
        self.byte[7].update(shift_in)


class LeftShift(Byte):

    def __init__(self):
        super().__init__()
        self.shift_out = Bit()

    def update(self, in_byte, shift_in):
        self.shift_out.update(in_byte.byte[7])
        for i in range(7, 0, -1):
            self.byte[i].update(in_byte.byte[i - 1])
        self.byte[0].update(shift_in)


class AddBit(Bit):

    def __init__(self):
        super().__init__()
        self.carry_out = Bit()

    def update(self, carry_in, input_bit_a, input_bit_b):
        self.state = s_xor(carry_in.state, s_xor(input_bit_a.state, input_bit_b.state))
        self.carry_out.state = s_or(
            s_and(input_bit_a.state,
                  input_bit_b.state
                  ),
            s_and(carry_in.state,
                  s_xor(input_bit_a.state, input_bit_b.state)
                  )
        )
        return self.carry_out


class CompareBit(Bit):

    def __init__(self):
        super().__init__()
        self.equal = Bit()
        self.larger = Bit()

    def update(self, in_equal, in_larger, input_bit_a, input_bit_b):
        self.state = s_xor(input_bit_a.state, input_bit_b.state)
        self.equal.state = s_and(in_equal.state, s_not(self.state))
        self.larger.state = s_or(in_larger.state, s_and3(input_bit_a.state, in_equal.state, self.state))
        return self.equal, self.larger


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
        for y in range(self.size):
            carry_in.update(self.byte[y].update(carry_in, input_byte_a.byte[y], input_byte_b.byte[y]))
        self.carry_out.update(carry_in)


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
        self.equal = Bit(1)
        self.larger = Bit(0)

    def update(self, input_byte_a, input_byte_b):
        for y in range(self.size-1, -1, -1):
            self.byte[y].update(self.equal, self.larger, input_byte_a.byte[y], input_byte_b.byte[y])
            self.equal.update(self.byte[y].equal)
            self.larger.update(self.byte[y].larger)
        return self.equal, self.larger


class Compare0(Bit):
    def __init__(self, init_state=1):
        self.state = init_state

    def update(self, in_byte):
        self.state = s_not(s_or8(
            in_byte.byte[0].state,
            in_byte.byte[1].state,
            in_byte.byte[2].state,
            in_byte.byte[3].state,
            in_byte.byte[4].state,
            in_byte.byte[5].state,
            in_byte.byte[6].state,
            in_byte.byte[7].state))


class ArithmeticAndLogicUnit(Byte):

    def __init__(self):
        super().__init__()
        self.Zero = Compare0()
        self.Comparer = CompareByte()
        self.Es = [Enabler() for i in range(8)]  # One more than needed, first is not used
        self.ANDs = [ANDBit() for i in range(3)]
        self.larger = Bit()
        self.equal = Bit()
        self.Orer = ORer()
        self.Ander = ANDer()
        self.Noter = NOTer()
        self.LeftShifter = LeftShift()
        self.RightShifter = RightShift()
        self.Adder = AddByte()
        self.Decoder = Decoder3x8()
        self.Carry_out = OR3Bit()

    def update(self, a_byte, b_byte, carry_bit, op1, op2, op3):
        self.Decoder.update(op1, op2, op3)

        self.Comparer.update(a_byte, b_byte)
        self.Es[6].update(self.Comparer, self.Decoder.byte[6])
        self.larger.update(self.Comparer.larger)
        self.equal.update(self.Comparer.equal)

        self.Orer.update(a_byte, b_byte)
        self.Es[5].update(self.Orer, self.Decoder.byte[5])

        self.Ander.update(a_byte, b_byte)
        self.Es[4].update(self.Ander, self.Decoder.byte[4])

        self.Noter.update(a_byte)
        self.Es[3].update(self.Noter, self.Decoder.byte[3])

        self.LeftShifter.update(a_byte, carry_bit)
        self.ANDs[2].update(self.LeftShifter.shift_out, self.Decoder.byte[2])
        self.Es[2].update(self.LeftShifter, self.Decoder.byte[2])

        self.RightShifter.update(a_byte, carry_bit)
        self.ANDs[1].update(self.RightShifter.shift_out, self.Decoder.byte[1])
        self.Es[1].update(self.RightShifter, self.Decoder.byte[1])

        self.Adder.update(a_byte, b_byte, carry_bit)
        self.ANDs[0].update(self.Adder.carry_out, self.Decoder.byte[0])
        self.Es[0].update(self.Adder, self.Decoder.byte[0])

        for y in np.arange(8):
            self.byte[y].state = s_or8(self.Es[0].byte[y].state, self.Es[1].byte[y].state, self.Es[2].byte[y].state,
                                       self.Es[3].byte[y].state, self.Es[4].byte[y].state, self.Es[5].byte[y].state,
                                       self.Es[6].byte[y].state, 0)

        self.Carry_out.update(self.ANDs[0], self.ANDs[1], self.ANDs[2])

        self.Zero.update(self)


class Bus1(Byte):

    def update(self, in_byte, bus1_bit):
        self.byte[0].state = s_or(in_byte.byte[0].state, bus1_bit.state)
        for y in range(1, 8):
            self.byte[y].state=s_and(in_byte.byte[y].state, s_not(bus1_bit.state))


# Declarations
ZeroByte = Byte()
Bus = Byte()
tmp = Byte()

# TEST
Bus.initial_set(np.array([0, 1, 0, 0, 0, 0, 1, 1]))
print("Bus:")
Bus.report()
print("tmp:")
tmp.report()
tmp.initial_set(np.array([0, 1, 0, 1, 0, 1, 0, 1]))
ZeroByte.initial_set(np.array([0, 0, 0, 0, 0, 0, 0, 0]))

test = ORer()
test.update(Bus, test)
test.report()
test.update(Bus, test)
test.report()
test.update(Bus, tmp)
test.report()


# op1 = Bit(0)
# op2 = Bit(1)
# op3 = Bit(0)
# carry = Bit(0)
# ALU = ArithmeticAndLogicUnit()
# ALU.update(tmp, Bus, carry, op1, op2, op3)
# print("ALU: ")
# ALU.report()
# ALU.larger.report()
# ALU.equal.report()
# ALU.Carry_out.report()
# ALU.Zero.report()

# MyBus1 = Bus1()
# MyBus1.update(Bus, op1)
# MyBus1.report()
# MyRAM = RAM256byte()
# AddressA = Byte()
# AddressA.initial_set(np.array([1, 1, 1, 1, 1, 1, 1, 1]))
#
# AddressB = Byte()
# AddressB.initial_set(np.array([0, 1, 1, 1, 1, 1, 1, 0]))


# E1 = Enabler()
# in_bit = Bit()
# E1.report()
# E1.update(Bus, in_bit)
# E1.report()
# print("Report Bus:")
# Bus.report()

# print("Report tmp:")
# tmp.report()
#
#
# Comparer = CompareByte()
# Comparer.update(Bus, tmp)
# print("Comparer: ")
# Comparer.report()
# Comparer.equal.report()
# Comparer.larger.report()

# Zero = Compare0()
# Zero.update(Bus)
# Zero.report()

#
# Adder = AddByte()
# in_bit = Bit()
# in_bit.state = 0
#
#
# in_bit = Adder.update(Bus, tmp, in_bit)
#
# Adder.report()
# in_bit.report()

# tmp.update(Bus)
# tmp.report()
# shift_out = right_shift(tmp, in_bit)
# tmp.report()
# shift_out = left_shift(tmp, in_bit)
# tmp.report()

