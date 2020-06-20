from logic_gates import *


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
        one = s_nand(set_bit.state, input_bit.state)
        two = s_nand(set_bit.state, one)
        four = s_nand(two, self.state)
        three = s_nand(one, four)
        self.state = three


class ANDBit(Bit):
    def update(self, a_bit, b_bit):
        self.state = s_not(s_nand(a_bit.state, b_bit.state))


class AND3Bit(Bit):
    def update(self, a_bit, b_bit, c_bit):
        self.state = s_and3(a_bit.state, b_bit.state, c_bit.state)


class NOTBit(Bit):
    def update(self, a_bit):
        self.state = s_not(a_bit.state)


class ORBit(Bit):
    def update(self, a_bit, b_bit):
        self.state = s_or(a_bit.state, b_bit.state)


class OR3Bit(Bit):
    def update(self, a_bit, b_bit, c_bit):
        self.state = s_or3(a_bit.state, b_bit.state, c_bit.state)


class OR4Bit(Bit):
    def update(self, a_bit, b_bit, c_bit, d_bit):
        self.state = s_or4(a_bit.state, b_bit.state, c_bit.state, d_bit.state)


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
