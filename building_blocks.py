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
        self.nibblex, self.nibbley = byte2nibble(address)
        addr_x = decode4x16(self.nibblex)  # unique 8-array
        addr_y = decode4x16(self.nibbley)  # unique 8-array
        for x in range(self.AddressSize ** 2):
            self.RAM[x].update(self.Bit1, self.Bit0, data_input, addr_x, addr_y)

    def report_Address(self, address):
        self.nibblex, self.nibbley = byte2nibble(address)
        addr_x = decode4x16(self.nibblex)  # unique 8-array
        addr_y = decode4x16(self.nibbley)  # unique 8-array
        for x in range(self.AddressSize ** 2):
            if all(self.RAM[x].x == addr_x) & all(self.RAM[x].y == addr_y):
                self.RAM[x].Reg.Memory.report()


class FlagRegister(Nibble):
    def __init__(self):
        super().__init__()
        self.Carry = MemoryBit()
        self.Larger = MemoryBit()
        self.Equal = MemoryBit()
        self.Zero = MemoryBit()

    def update(self, set_bit, c, al, e, z):
        self.Carry.update(set_bit, c)
        self.Larger.update(set_bit, al)
        self.Equal.update(set_bit, e)
        self.Zero.update(set_bit, z)

        self.byte[0].update(self.Carry)
        self.byte[1].update(self.Larger)
        self.byte[2].update(self.Equal)
        self.byte[3].update(self.Zero)


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
        self.Bus1bit = OR3Bit()
        self.Enable_RAM = OR4Bit()
        self.Enable_IAR = OR3Bit()
        self.Enable_IAR_DATA = ANDBit()
        self.Enable_IAR_IAR_ADV = ANDBit()
        self.Enable_IAR_JUMP = ANDBit()
        self.Enable_RegA = ORBit()
        self.LOAD_or_STORE = ORBit()
        self.Enable_RegA_ALU = ANDBit()
        self.Enable_RegA_LOAD_STORE = ANDBit()
        self.Enable_RegB = OR3Bit()
        self.Enable_RegB_ALU = ANDBit()
        self.Enable_RegB_STORE = ANDBit()
        self.Enable_RegB_JMPR = ANDBit()
        self.Set_RegB = OR3Bit()
        self.Set_RegB_ALU = AND3Bit()
        self.Set_RegB_LOAD = ANDBit()
        self.Set_RegB_DATA = ANDBit()
        self.Enable_R = [ORBit() for i in range(4)]
        self.Enable_RA = [AND3Bit() for i in range(4)]
        self.Enable_RB = [AND3Bit() for i in range(4)]
        self.Set_R = [AND3Bit() for i in range(4)]
        self.Set_MAR = OR4Bit()
        self.Set_ACC = OR3Bit()
        self.Set_ACC_Advance_IAR = ANDBit()
        self.Set_ACC_DATA = ANDBit()
        self.Set_ACC_ALU_Operation = AND3Bit()
        self.Enable_ACC = OR3Bit()
        self.Enable_ACC_Advance_IAR = ANDBit()
        self.Enable_ACC_ALU_Operation = ANDBit()
        self.Enable_ACC_DATA = ANDBit()
        self.Set_RAM = ANDBit()
        self.Set_TMP = ANDBit()
        self.Set_IR = ANDBit()
        self.Set_IAR = OR4Bit()
        self.Set_IAR_DATA = ANDBit()
        self.Set_IAR_JMPR = ANDBit()
        self.Set_IAR_JUMP = ANDBit()
        self.Set_IAR_IAR_ADV = ANDBit()
        self.ALU_OP = [AND3Bit() for i in range(3)]
        self.Set_CarryFlag = ORBit()
        self.Set_CarryFlag_PostALU = AND3Bit()
        self.Set_CarryFlag_CLF = AND3Bit()
        self.Enable_CarryFlag = AND3Bit()
        self.Set_Flags = ORBit()

        self.Decoder_RA = Decoder2x4()
        self.Decoder_RB = Decoder2x4()
        self.InstructionDecoder = Decoder3x8()
        self.NonALUInstruction = NOTBit()
        self.NonALUCodes = [ANDBit() for i in range(8)]
        self.ALU_Instr_S6_NOT = NOTBit()
        self.ALU_Instr_S6_AND = AND3Bit()
        self.Set_MAR_ADVANCE_IAR = ANDBit()
        self.Set_MAR_LOAD_and_STORE = ANDBit()
        self.Set_MAR_DATA = ANDBit()
        self.Set_MAR_JUMP = ANDBit()
        self.Enable_RAM_ADVANCE_IAR = ANDBit()
        self.Enable_RAM_LOAD = ANDBit()
        self.Enable_RAM_JUMP = ANDBit()
        self.Enable_RAM_DATA = ANDBit()
        self.AND_STEP4_DATA = ANDBit()
        self.AND_STEP5_DATA = ANDBit()
        self.AND_STEP6_DATA = ANDBit()
        self.AND_STEP4_JMPR = ANDBit()
        self.AND_STEP4_JUMP = ANDBit()
        self.AND_STEP5_JUMP = ANDBit()
        self.AND_STEP5_ALU = ANDBit()
        self.AND_STEP4_CLF = ANDBit()
        self.Set_Flags_ALU = AND3Bit()
        self.Set_Flags_CLF = AND3Bit()

    def update(self, IR, Flags):
        self.clock.update()
        self.Stepper.update(self.clock, self.Stepper.byte[7])

        # Non-ALU Instruction Decoding
        self.InstructionDecoder.update(IR.byte[1], IR.byte[2], IR.byte[3])

        self.NonALUInstruction.update(IR.byte[0])
        self.NonALUCodes[0].update(self.NonALUInstruction, self.InstructionDecoder.byte[0])
        self.NonALUCodes[1].update(self.NonALUInstruction, self.InstructionDecoder.byte[1])
        self.NonALUCodes[2].update(self.NonALUInstruction, self.InstructionDecoder.byte[2])
        self.NonALUCodes[3].update(self.NonALUInstruction, self.InstructionDecoder.byte[3])
        self.NonALUCodes[4].update(self.NonALUInstruction, self.InstructionDecoder.byte[4])
        self.NonALUCodes[5].update(self.NonALUInstruction, self.InstructionDecoder.byte[5])
        self.NonALUCodes[6].update(self.NonALUInstruction, self.InstructionDecoder.byte[6])
        self.NonALUCodes[7].update(self.NonALUInstruction, self.InstructionDecoder.byte[7])

        # for i in range(8):
        #     print('IR.byte[{}]={}'.format(i, NonALUCodes[i].state))

        # Stepper Connections
        # Step1: Set IAR to MAR and increment IAR by 1 which is stored in ACC
        # Step2: Enable RAM to IR
        # Step3: Enable ACC to IAR
        # ALU Step 4: Set RegB to TMP
        # ALU Step 5: ALU gets Orders, Reg A (+ TMP) are set to ACC, Flags are set
        # ALU Step 6: Acc is set to Reg B
        # LOAD Step 4: Set RegA to MAR
        # LOAD Step 5: Set RAM to RegB
        # STORE Step 4: Set RegA to MAR
        # STORE Step 5: Set RegB to RAM
        # DATA Step 4: Set Bit1, Enable IAR to MAR and ACC(=IAR+Bit1)
        # DATA Step 5: Enable RAM to RegB
        # DATA Step 6: Enable ACC to IAR
        # JMPR Step 4: Enable RegB to IAR
        # JUMP Step 4: Enable IAR to MAR
        # JUMP Step 5: Enable RAM to IAR
        # CLF Step 4: Enable bus 1 set Flags

        #  JMPR Instruction
        self.AND_STEP4_JMPR.update(self.Stepper.byte[4], self.NonALUCodes[3])  # Step 4 JMPR

        #  JUMP Instruction
        self.AND_STEP4_JUMP.update(self.Stepper.byte[4], self.NonALUCodes[4])  # Step 4 JUMP
        self.AND_STEP5_JUMP.update(self.Stepper.byte[5], self.NonALUCodes[4])  # Step 5 JUMP

        #  DATA INSTRUCTION
        self.AND_STEP4_DATA.update(self.Stepper.byte[4], self.NonALUCodes[2])  # Step 4 DATA
        self.AND_STEP5_DATA.update(self.Stepper.byte[5], self.NonALUCodes[2])  # Step 5 DATA
        self.AND_STEP6_DATA.update(self.Stepper.byte[6], self.NonALUCodes[2])  # Step 6 DATA

        #  CLF Instruction
        self.AND_STEP4_CLF.update(self.Stepper.byte[4], self.NonALUCodes[6])

        self.Bus1bit.update(self.Stepper.byte[1], self.AND_STEP4_DATA, self.AND_STEP4_CLF)  # Step1 IAR ADVANCE _OR_ Step 4 DATA _OR_ Step 4 CLF

        self.Enable_IAR_DATA.update(self.clock.clock_enable, self.AND_STEP4_DATA)  # Step 4 DATA
        self.Enable_IAR_JUMP.update(self.clock.clock_enable, self.AND_STEP4_JUMP)  # Step 4 JUMP
        self.Enable_IAR_IAR_ADV.update(self.clock.clock_enable, self.Stepper.byte[1])  # Step1 IAR ADVANCE
        self.Enable_IAR.update(self.Enable_IAR_DATA, self.Enable_IAR_IAR_ADV, self.Enable_IAR_JUMP)

        self.Set_IAR_IAR_ADV.update(self.clock.clock_set, self.Stepper.byte[3])  # Step3 IAR ADVANCE
        self.Set_IAR_DATA.update(self.clock.clock_set, self.AND_STEP6_DATA)  # Step 6 DATA
        self.Set_IAR_JMPR.update(self.clock.clock_set, self.AND_STEP4_JMPR)  # Step 4 JMPR
        self.Set_IAR_JUMP.update(self.clock.clock_set, self.AND_STEP5_JUMP)  # Step 5 JUMP
        self.Set_IAR.update(self.Set_IAR_IAR_ADV, self.Set_IAR_DATA, self.Set_IAR_JMPR, self.Set_IAR_JUMP)

        self.Set_IR.update(self.clock.clock_set, self.Stepper.byte[2])  # Step2

        self.ALU_Instr_S6_AND.update(IR.byte[1], IR.byte[2], IR.byte[3])  # Step6   ALU
        self.ALU_Instr_S6_NOT.update(self.ALU_Instr_S6_AND)  # Step6    ALU

        self.Enable_RegB_ALU.update(self.Stepper.byte[4], IR.byte[0])  # Step4  ALU
        self.Enable_RegB_STORE.update(self.Stepper.byte[5], self.NonALUCodes[1])  # Step 5   STORE
        self.Enable_RegB_JMPR.update(self.Stepper.byte[4], self.NonALUCodes[3])  # Step 4 JMPR
        self.Enable_RegB.update(self.Enable_RegB_STORE, self.Enable_RegB_ALU, self.Enable_RegB_JMPR)  # OR over Steps
        self.LOAD_or_STORE.update(self.NonALUCodes[0], self.NonALUCodes[1])
        self.Enable_RegA_ALU.update(IR.byte[0], self.Stepper.byte[5])  # Step5  ALU
        self.Set_Flags_ALU.update(self.clock.clock_set, IR.byte[0], self.Stepper.byte[5])  # Step5  ALU
        self.Set_Flags_CLF.update(self.clock.clock_set, self.NonALUCodes[6], self.Stepper.byte[4])  # Step4  CLF
        self.Set_Flags.update(self.Set_Flags_ALU, self.Set_Flags_CLF)  # OR over Steps

        self.Set_CarryFlag_PostALU.update(self.clock.clock_set, IR.byte[0], self.Stepper.byte[6])  # Step6 Delayed CarryIn Flag
        self.Set_CarryFlag_CLF.update(self.clock.clock_set, self.NonALUCodes[6], self.Stepper.byte[4])  # Delayed CarryIn Flag Reset
        self.Set_CarryFlag.update(self.Set_CarryFlag_PostALU, self.Set_CarryFlag_CLF)
        self.Enable_CarryFlag.update(self.clock.clock_enable, IR.byte[0], self.Stepper.byte[5]) # CarryIn to ALU is enabled only in ALU Command Step 5
        self.AND_STEP5_ALU.update(IR.byte[0], self.Stepper.byte[5])  # Avoid feedback loop: Step 5 and ALU Instruction: Disable carry flag

        self.Enable_RegA_LOAD_STORE.update(self.Stepper.byte[4], self.LOAD_or_STORE)  # Step 4  LOAD AND STORE
        self.Enable_RegA.update(self.Enable_RegA_ALU, self.Enable_RegA_LOAD_STORE)  # OR over Steps
        self.Set_RegB_ALU.update(self.Stepper.byte[6], IR.byte[0], self.ALU_Instr_S6_NOT)  # Step6  ALU
        self.Set_RegB_LOAD.update(self.Stepper.byte[5], self.NonALUCodes[0])  # Step 5   LOAD
        self.Set_RegB_DATA.update(self.Stepper.byte[5], self.NonALUCodes[2])  # Step 5 DATA
        self.Set_RegB.update(self.Set_RegB_ALU, self.Set_RegB_LOAD, self.Set_RegB_DATA)  # OR over Steps

        self.Set_ACC_Advance_IAR.update(self.clock.clock_set, self.Stepper.byte[1])  # Step1
        self.Set_ACC_ALU_Operation.update(self.clock.clock_set, IR.byte[0], self.Stepper.byte[5])  # Step5  ALU
        self.Set_ACC_DATA.update(self.clock.clock_set, self.AND_STEP4_DATA)  # Step 4 DATA
        self.Set_ACC.update(self.Set_ACC_ALU_Operation, self.Set_ACC_Advance_IAR, self.Set_ACC_DATA)  # OR over Steps

        self.Enable_ACC_DATA.update(self.clock.clock_enable, self.AND_STEP6_DATA)  # Step 6 DATA
        self.Enable_ACC_Advance_IAR.update(self.clock.clock_enable, self.Stepper.byte[3])  # Step3
        self.Enable_ACC_ALU_Operation.update(self.Set_RegB_ALU, self.clock.clock_enable)  # Step6   ALU
        self.Enable_ACC.update(self.Enable_ACC_ALU_Operation,
                               self.Enable_ACC_Advance_IAR, self.Enable_ACC_DATA)  # OR over Steps

        self.Set_MAR_ADVANCE_IAR.update(self.clock.clock_set, self.Stepper.byte[1])  # Step1
        self.Set_MAR_LOAD_and_STORE.update(self.clock.clock_set, self.Enable_RegA_LOAD_STORE)  # Step 4  LOAD and STORE
        self.Set_MAR_DATA.update(self.clock.clock_set, self.AND_STEP4_DATA)  # Step 4 DATA
        self.Set_MAR_JUMP.update(self.clock.clock_set, self.AND_STEP4_JUMP)  # Step 4 JUMP
        self.Set_MAR.update(self.Set_MAR_ADVANCE_IAR, self.Set_MAR_LOAD_and_STORE, self.Set_MAR_DATA, self.Set_MAR_JUMP)  # OR over Steps

        self.Enable_RAM_DATA.update(self.clock.clock_enable, self.AND_STEP5_DATA)  # Step 5 DATA
        self.Enable_RAM_ADVANCE_IAR.update(self.clock.clock_enable, self.Stepper.byte[2])  # Step2
        self.Enable_RAM_LOAD.update(self.clock.clock_enable, self.Set_RegB_LOAD)  # Step 5    LOAD
        self.Enable_RAM_JUMP.update(self.clock.clock_enable, self.AND_STEP5_JUMP)  # Step 5    JUMP
        self.Enable_RAM.update(self.Enable_RAM_ADVANCE_IAR, self.Enable_RAM_LOAD, self.Enable_RAM_DATA, self.Enable_RAM_JUMP)  # OR over Steps

        self.Set_RAM.update(self.Enable_RegB_STORE, self.clock.clock_set)  # Step 5    STORE

        self.Set_TMP.update(self.Enable_RegB_ALU, self.clock.clock_set)  # Step4    ALU

        self.ALU_OP[0].update(IR.byte[0], self.Stepper.byte[5], IR.byte[1])  # Step5    ALU
        self.ALU_OP[1].update(IR.byte[0], self.Stepper.byte[5], IR.byte[2])  # Step5    ALU
        self.ALU_OP[2].update(IR.byte[0], self.Stepper.byte[5], IR.byte[3])  # Step5    ALU

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



