from functional_bytes import *


class RAM256byte(Byte):
    AddressSize = 16

    def __init__(self):
        super().__init__()
        self.RAM = [RAMbyte(x, y) for x, y in np.ndindex(self.AddressSize, self.AddressSize)]
        self.MAR = MemoryByte()
        self.OutputOR = ORer()
        self.Bit0 = Bit(0)
        self.Bit1 = Bit(1)
        self.nibblex = Nibble()
        self.nibbley = Nibble()

    def update(self, set_bit, enable_bit, input_byte, set_mar, address):

        self.MAR.update(set_mar, address)
        self.nibblex, self.nibbley = byte2nibble(self.MAR)
        addr_x = decode4x16(self.nibblex)  # unique 8-array
        addr_y = decode4x16(self.nibbley)  # unique 8-array
        for x in range(self.AddressSize ** 2):
            self.RAM[x].update(set_bit, enable_bit, input_byte, addr_x, addr_y)
            self.OutputOR.update(self.OutputOR, self.RAM[x])

        for y in range(self.size):
            self.byte[y].update(self.OutputOR.byte[y])
            self.OutputOR.byte[y].state = 0

    def reportMAR(self):
        for y in range(self.size-1, -1, -1):
            self.MAR.byte[y].report(y)

    def initial_RAM_set(self, address, data_input):
        nibblex, nibbley = byte2nibble(address)
        addr_x = decode4x16(nibblex)  # unique 8-array
        addr_y = decode4x16(nibbley)  # unique 8-array
        for x in range(self.AddressSize ** 2):
            self.RAM[x].update(self.Bit1, self.Bit0, data_input, addr_x, addr_y)


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

    def update(self, a_byte, b_byte, carry_bit, op):
        self.Decoder.update(op[0], op[1], op[2])

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


class Clock(Nibble):
    def __init__(self):
        super().__init__()
        self.clock_delayed = Bit()
        self.clock_set = Bit()
        self.clock_enable = Bit()
        self.clock = Bit()
        self.time = 0

    def update(self):
        self.clock_delayed.update(self.clock)
        if self.time % 4 == 0:
            self.clock.state = (self.clock.state + 1) % 2
        self.clock_enable.state = s_or(self.clock.state, self.clock_delayed.state)
        self.clock_set.state = s_and(self.clock.state, self.clock_delayed.state)

        self.time = self.time + 1

        self.byte[0].update(self.clock)
        self.byte[1].update(self.clock_delayed)
        self.byte[2].update(self.clock_set)
        self.byte[3].update(self.clock_enable)


class ControlUnit(Byte):
    size = 18

    def __init__(self):
        super(ControlUnit, self).__init__()
        self.clock = Clock()
        self.Stepper = Stepper()
        self.Bus1bit = Bit()
        self.Enable_RAM = ANDBit()
        self.Enable_IAR = ANDBit()
        self.Enable_RegA = ANDBit()
        self.Enable_RegB = ANDBit()
        self.Set_RegB = AND3Bit()
        self.Enable_R = [ORBit() for i in range(4)]
        self.Enable_RA = [AND3Bit() for i in range(4)]
        self.Enable_RB = [AND3Bit() for i in range(4)]
        self.Set_R = [AND3Bit() for i in range(4)]
        self.Set_MAR = ANDBit()
        self.Set_ACC = ORBit()
        self.Set_ACC_Advance_IAR = ANDBit()
        self.Set_ACC_ALU_Operation = ANDBit()
        self.Enable_ACC = ORBit()
        self.Enable_ACC_Advance_IAR = ANDBit()
        self.Enable_ACC_ALU_Operation = ANDBit()
        self.Set_RAM = ANDBit()
        self.Set_TMP = ANDBit()
        self.Set_IR = ANDBit()
        self.Set_IAR = ANDBit()
        self.ALU_OP = [AND3Bit() for i in range(3)]
        self.CarryIn = Bit()
        self.Decoder_RA = Decoder2x4()
        self.Decoder_RB = Decoder2x4()
        self.ALU_Instr_S6_NOT = NOTBit()
        self.ALU_Instr_S6_AND = AND3Bit()

    def update(self, IR):
        self.clock.update()
        self.Stepper.update(self.clock, self.Stepper.byte[7])

        # Dynamic Register
        self.Decoder_RA.update(IR.byte[4], IR.byte[5])
        self.Decoder_RB.update(IR.byte[6], IR.byte[7])
        self.Set_R[0].update(self.clock.clock_set, self.Decoder_RB.byte[0], self.Set_RegB)
        self.Set_R[1].update(self.clock.clock_set, self.Decoder_RB.byte[1], self.Set_RegB)
        self.Set_R[2].update(self.clock.clock_set, self.Decoder_RB.byte[2], self.Set_RegB)
        self.Set_R[3].update(self.clock.clock_set, self.Decoder_RB.byte[3], self.Set_RegB)
        self.Enable_RB[0].update(self.clock.clock_enable, self.Decoder_RB.byte[0], self.Enable_RegB)
        self.Enable_RB[1].update(self.clock.clock_enable, self.Decoder_RB.byte[1], self.Enable_RegB)
        self.Enable_RB[2].update(self.clock.clock_enable, self.Decoder_RB.byte[2], self.Enable_RegB)
        self.Enable_RB[3].update(self.clock.clock_enable, self.Decoder_RB.byte[3], self.Enable_RegB)
        self.Enable_RA[0].update(self.clock.clock_enable, self.Decoder_RA.byte[0], self.Enable_RegA)
        self.Enable_RA[1].update(self.clock.clock_enable, self.Decoder_RA.byte[1], self.Enable_RegA)
        self.Enable_RA[2].update(self.clock.clock_enable, self.Decoder_RA.byte[2], self.Enable_RegA)
        self.Enable_RA[3].update(self.clock.clock_enable, self.Decoder_RA.byte[3], self.Enable_RegA)
        self.Enable_R[0].update(self.Enable_RA[0], self.Enable_RB[0])
        self.Enable_R[1].update(self.Enable_RA[1], self.Enable_RB[1])
        self.Enable_R[2].update(self.Enable_RA[2], self.Enable_RB[2])
        self.Enable_R[3].update(self.Enable_RA[3], self.Enable_RB[3])

        # Stepper Connections
        # Step1: Set IAR to MAR and increment IAR by 1 which is stored in ACC
        # Step2: Enable RAM to IR
        # Step3: Enable ACC to IAR
        # Step 4: Set RegB to TMP
        # Step 5: ALU gets Orders, Reg A (+ TMP) are set to ACC
        # Step 6: Acc is set to Reg B

        self.Bus1bit.update(self.Stepper.byte[1]) # Step1

        self.Enable_IAR.update(self.clock.clock_enable, self.Stepper.byte[1]) # Step1
        self.Set_IAR.update(self.clock.clock_set, self.Stepper.byte[3])  # Step3

        self.Set_IR.update(self.clock.clock_set, self.Stepper.byte[2])  # Step2

        self.Set_MAR.update(self.clock.clock_set, self.Stepper.byte[1]) # Step1

        self.Set_ACC_Advance_IAR.update(self.clock.clock_set, self.Stepper.byte[1]) # Step1
        self.Set_ACC_ALU_Operation.update(self.Enable_RegA, self.clock.clock_set)  # Step5
        self.Set_ACC.update(self.Set_ACC_ALU_Operation, self.Set_ACC_Advance_IAR)  # OR over Steps
        self.Enable_ACC_Advance_IAR.update(self.clock.clock_enable, self.Stepper.byte[3])  # Step3
        self.Enable_ACC_ALU_Operation.update(self.Set_RegB, self.clock.clock_enable)  # Step6
        self.Enable_ACC.update(self.Enable_ACC_ALU_Operation, self.Enable_ACC_Advance_IAR)  # OR over Steps

        self.Enable_RAM.update(self.clock.clock_enable, self.Stepper.byte[2])  # Step2

        self.Set_TMP.update(self.Enable_RegB, self.clock.clock_set)  # Step4

        self.ALU_Instr_S6_AND.update(IR.byte[1], IR.byte[2], IR.byte[3])  # Step6
        self.ALU_Instr_S6_NOT.update(self.ALU_Instr_S6_AND)  # Step6

        self.Enable_RegB.update(self.Stepper.byte[4], IR.byte[0])  # Step4
        self.Enable_RegA.update(IR.byte[0], self.Stepper.byte[5])  # Step5
        self.Set_RegB.update(self.Stepper.byte[6], IR.byte[0], self.ALU_Instr_S6_NOT)  # Step6

        self.ALU_OP[0].update(IR.byte[0], self.Stepper.byte[5], IR.byte[1])  # Step5
        self.ALU_OP[1].update(IR.byte[0], self.Stepper.byte[5], IR.byte[2])  # Step5
        self.ALU_OP[2].update(IR.byte[0], self.Stepper.byte[5], IR.byte[3])  # Step5
