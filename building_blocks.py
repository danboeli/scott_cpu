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
        self.addr_x = Decoder4x16()
        self.addr_y = Decoder4x16()

    def __call__(self, set_bit, enable_bit, input_byte, set_mar, address):
        self.MAR(set_mar, address)
        self.nibblex, self.nibbley = byte2nibble(self.MAR)
        self.addr_x(self.nibblex)  # unique 8-array
        self.addr_y(self.nibbley)  # unique 8-array
        for x in range(self.AddressSize ** 2):
            self.RAM[x](set_bit, enable_bit, input_byte, self.addr_x, self.addr_y)
            self.OutputOR(self.OutputOR, self.RAM[x])

        for y in range(self.size):
            self.byte[y](self.OutputOR.byte[y])
            self.OutputOR.byte[y].state = 0

    def reportMAR(self):
        for y in range(self.size-1, -1, -1):
            self.MAR.byte[y].report(y)

    def initial_RAM_set(self, address, data_input):
        self.nibblex, self.nibbley = byte2nibble(address)
        self.addr_x(self.nibblex)  # unique 8-array
        self.addr_y(self.nibbley)  # unique 8-array
        for x in range(self.AddressSize ** 2):
            self.RAM[x](self.Bit1, self.Bit0, data_input, self.addr_x, self.addr_y)

    def report_Address(self, address):
        self.nibblex, self.nibbley = byte2nibble(address)
        self.addr_x(self.nibblex)  # unique 8-array
        self.addr_y(self.nibbley)  # unique 8-array
        for i in range(self.AddressSize ** 2):
            if ((self.RAM[i].x == decoder2array(self.addr_x)).all()) & ((self.RAM[i].y == decoder2array(self.addr_y)).all()):
                return repr(self.RAM[i].Reg.Memory)

    def return_Address(self, address):
        self.nibblex, self.nibbley = byte2nibble(address)
        self.addr_x(self.nibblex)  # unique 8-array
        self.addr_y(self.nibbley)  # unique 8-array
        for j in range(self.AddressSize ** 2):
            if ((self.RAM[j].x == decoder2array(self.addr_x)).all()) & ((self.RAM[j].y == decoder2array(self.addr_y)).all()):
                return [self.RAM[j].Reg.Memory.byte[i].state for i in range(8)]


class FlagRegister(Nibble):
    def __init__(self):
        super().__init__()
        self.Carry = MemoryBit()
        self.Larger = MemoryBit()
        self.Equal = MemoryBit()
        self.Zero = MemoryBit()

    def __call__(self, set_bit, c, al, e, z):
        self.Carry(set_bit, c)
        self.Larger(set_bit, al)
        self.Equal(set_bit, e)
        self.Zero(set_bit, z)

        self.byte[0](self.Carry)
        self.byte[1](self.Larger)
        self.byte[2](self.Equal)
        self.byte[3](self.Zero)


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

    def __call__(self, a_byte, b_byte, carry_bit, op):
        self.Decoder(op[0], op[1], op[2])

        self.Comparer(a_byte, b_byte)
        self.Es[6](self.Comparer, self.Decoder.byte[6])
        self.larger(self.Comparer.larger)
        self.equal(self.Comparer.equal)

        self.Orer(a_byte, b_byte)
        self.Es[5](self.Orer, self.Decoder.byte[5])

        self.Ander(a_byte, b_byte)
        self.Es[4](self.Ander, self.Decoder.byte[4])

        self.Noter(a_byte)
        self.Es[3](self.Noter, self.Decoder.byte[3])

        self.LeftShifter(a_byte, carry_bit)
        self.ANDs[2](self.LeftShifter.shift_out, self.Decoder.byte[2])
        self.Es[2](self.LeftShifter, self.Decoder.byte[2])

        self.RightShifter(a_byte, carry_bit)
        self.ANDs[1](self.RightShifter.shift_out, self.Decoder.byte[1])
        self.Es[1](self.RightShifter, self.Decoder.byte[1])

        self.Adder(a_byte, b_byte, carry_bit)
        self.ANDs[0](self.Adder.carry_out, self.Decoder.byte[0])
        self.Es[0](self.Adder, self.Decoder.byte[0])

        for y in np.arange(8):
            self.byte[y].state = s_or8(self.Es[0].byte[y].state, self.Es[1].byte[y].state, self.Es[2].byte[y].state,
                                       self.Es[3].byte[y].state, self.Es[4].byte[y].state, self.Es[5].byte[y].state,
                                       self.Es[6].byte[y].state, 0)

        self.Carry_out(self.ANDs[0], self.ANDs[1], self.ANDs[2])

        self.Zero(self)


class Clock(Nibble):
    def __init__(self):
        super().__init__()
        self.clock_delayed = Bit()
        self.clock_set = Bit()
        self.clock_enable = Bit()
        self.clock = Bit()
        self.time = 0

    def __call__(self):
        self.clock_delayed(self.clock)
        if self.time % 4 == 0:
            self.clock.state = (self.clock.state + 1) % 2
        self.clock_enable.state = s_or(self.clock.state, self.clock_delayed.state)
        self.clock_set.state = s_and(self.clock.state, self.clock_delayed.state)

        self.time = self.time + 1

        self.byte[0](self.clock)
        self.byte[1](self.clock_delayed)
        self.byte[2](self.clock_set)
        self.byte[3](self.clock_enable)


class IOBus:
    def __init__(self):
        self.IO_SET_Clock = Bit()
        self.IO_ENABLE_Clock = Bit()
        self.IN_OUT = Bit()
        self.DATA_ADDRESS = Bit()
        self.IO_BUS = Byte()

    def __call__(self, set_clock, enable_clock, in_out, d_a, bus):
        self.IO_SET_Clock(set_clock)
        self.IO_ENABLE_Clock(enable_clock)
        self.IN_OUT(in_out)
        self.DATA_ADDRESS(d_a)
        self.IO_BUS(bus)


class ControlUnit(Byte):
    size = 18

    def __init__(self):
        super(ControlUnit, self).__init__()
        self.clock = Clock()
        self.State_Machine = State_Machine()
        self.Bus1bit = OR4Bit()
        self.Enable_RAM = OR5Bit()
        self.Enable_IAR = OR4Bit()
        self.Enable_IAR_DATA = ANDBit()
        self.Enable_IAR_IAR_ADV = ANDBit()
        self.Enable_IAR_JUMP = ANDBit()
        self.Enable_RegA = ORBit()
        self.LOAD_or_STORE = ORBit()
        self.Enable_RegA_ALU = ANDBit()
        self.Enable_RegA_LOAD_STORE = ANDBit()
        self.Enable_RegB = OR4Bit()
        self.Enable_RegB_ALU = ANDBit()
        self.Enable_RegB_STORE = ANDBit()
        self.Enable_RegB_JMPR = ANDBit()
        self.Set_RegB = OR4Bit()
        self.Set_RegB_ALU = AND3Bit()
        self.Set_RegB_LOAD = ANDBit()
        self.Set_RegB_DATA = ANDBit()
        self.Enable_R = [ORBit() for i in range(4)]
        self.Enable_RA = [AND3Bit() for i in range(4)]
        self.Enable_RB = [AND3Bit() for i in range(4)]
        self.Set_R = [AND3Bit() for i in range(4)]
        self.Set_MAR = OR5Bit()
        self.Set_ACC = OR4Bit()
        self.Set_ACC_Advance_IAR = ANDBit()
        self.Set_ACC_DATA = ANDBit()
        self.Set_ACC_ALU_Operation = AND3Bit()
        self.Enable_ACC = OR4Bit()
        self.Enable_ACC_Advance_IAR = ANDBit()
        self.Enable_ACC_ALU_Operation = ANDBit()
        self.Enable_ACC_DATA = ANDBit()
        self.Set_RAM = ANDBit()
        self.Set_TMP = ANDBit()
        self.Set_IR = ANDBit()
        self.Set_IAR = OR6Bit()
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
        self.Flag_C = ANDBit()
        self.Flag_A = ANDBit()
        self.Flag_E = ANDBit()
        self.Flag_Z = ANDBit()
        self.JUMPIF_OR = OR4Bit()
        self.AND_STEP4_JMPIF = ANDBit()
        self.AND_STEP5_JMPIF = ANDBit()
        self.AND_STEP6_JMPIF = AND3Bit()
        self.Enable_IAR_JMPIF = ANDBit()  # Step 4 JMPIF
        self.Set_MAR_JMPIF = ANDBit()  # Step 4 JMPIF
        self.Set_ACC_JMPIF = ANDBit()  # Step 4 JMPIF
        self.Enable_ACC_JMPIF = ANDBit()  # Step 5 JMPIF
        self.Set_IAR5_JMPIF = ANDBit()  # Step 5 JMPIF
        self.Enable_RAM_JMPIF = ANDBit()  # Step 6 JMPIF
        self.Set_IAR6_JMPIF = ANDBit()  # Step 6 JMPIF
        self.AND_STEP4_IO = AND3Bit()  # Step 4 I/O OUTPUT
        self.IO_INPUT = NOTBit()  # I/O Identify INPUT
        self.IO_OUTPUT = Bit()  # I/O Identify OUTPUT
        self.IO_DATA_ADDRESS = Bit()  # I/O Identify OUTPUT
        self.AND_STEP5_IO = AND3Bit() # Step 5 I/O INPUT
        self.IOClock_Set = ANDBit()  # Step 4  I/O OUTPUT
        self.IOClock_Enable = ANDBit()  # Step 5 I/O INPUT
        self.Enable_RegB_IO = ANDBit()  # Step 4 I/O OUTPUT
        self.Set_RegB_IO = ANDBit()  # Step 5 I/O INPUT

    def __call__(self, IR, Flags):
        self.clock()
        self.State_Machine(self.clock, self.State_Machine.byte[7])

        # Non-ALU Instruction Decoding
        self.InstructionDecoder(IR.byte[1], IR.byte[2], IR.byte[3])

        self.NonALUInstruction(IR.byte[0])
        self.NonALUCodes[0](self.NonALUInstruction, self.InstructionDecoder.byte[0])
        self.NonALUCodes[1](self.NonALUInstruction, self.InstructionDecoder.byte[1])
        self.NonALUCodes[2](self.NonALUInstruction, self.InstructionDecoder.byte[2])
        self.NonALUCodes[3](self.NonALUInstruction, self.InstructionDecoder.byte[3])
        self.NonALUCodes[4](self.NonALUInstruction, self.InstructionDecoder.byte[4])
        self.NonALUCodes[5](self.NonALUInstruction, self.InstructionDecoder.byte[5])
        self.NonALUCodes[6](self.NonALUInstruction, self.InstructionDecoder.byte[6])
        self.NonALUCodes[7](self.NonALUInstruction, self.InstructionDecoder.byte[7])

        # for i in range(8):
        #     print('IR.byte[{}]={}'.format(i, NonALUCodes[i].state))

        # State_Machine Connections
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
        # JMPIF: As for all instructions, IAR already points to address in RAM following JMPIF (Step1-3).
        # Address in RAM following JMPIF is the jump address, no instruction. Hence IAR needs to be incremented again
        # and then points to next instruction in RAM.
        # If jump is not executed, nothing further needs to be done. If jump is executed, IAR is overwritten by address
        # in RAM pointing to the jump target address.
        # JMPIF Step 4: Enable Bus 1 and IAR to ACC(=IAR already incremented +1 ) and MAR(=IAR already incremented)
        # JMPIF Step 5: Enable ACC to IAR
        # JMPIF Step 6: Enable RAM to IAR (if jump is executed)
        # I/O Step 4: Enable RegB, Activate I/O Set clock (OUT)
        # I/O Step 5: Set RegB, Activate I/O Enable clock (IN)

        #  DATA INSTRUCTION
        self.AND_STEP4_DATA(self.State_Machine.byte[4], self.NonALUCodes[2])  # Step 4 DATA
        self.AND_STEP5_DATA(self.State_Machine.byte[5], self.NonALUCodes[2])  # Step 5 DATA
        self.AND_STEP6_DATA(self.State_Machine.byte[6], self.NonALUCodes[2])  # Step 6 DATA

        #  JMPR Instruction
        self.AND_STEP4_JMPR(self.State_Machine.byte[4], self.NonALUCodes[3])  # Step 4 JMPR

        #  JUMP Instruction
        self.AND_STEP4_JUMP(self.State_Machine.byte[4], self.NonALUCodes[4])  # Step 4 JUMP
        self.AND_STEP5_JUMP(self.State_Machine.byte[5], self.NonALUCodes[4])  # Step 5 JUMP

        #  JMPIF Instruction
        self.Flag_C(Flags.Carry, IR.byte[4])
        self.Flag_A(Flags.Larger, IR.byte[5])
        self.Flag_E(Flags.Equal, IR.byte[6])
        self.Flag_Z(Flags.Zero, IR.byte[7])
        self.JUMPIF_OR(self.Flag_C, self.Flag_A, self.Flag_E, self.Flag_Z)
        self.AND_STEP4_JMPIF(self.State_Machine.byte[4], self.NonALUCodes[5])  # Step 4 JMPIF
        self.AND_STEP5_JMPIF(self.State_Machine.byte[5], self.NonALUCodes[5])  # Step 5 JMPIF
        self.AND_STEP6_JMPIF(self.State_Machine.byte[6], self.NonALUCodes[5], self.JUMPIF_OR)  # Step 6 JMPIF

        # CLF Instruction
        self.AND_STEP4_CLF(self.State_Machine.byte[4], self.NonALUCodes[6])

        # I/O Instruction
        self.IO_OUTPUT(IR.byte[4])  # I/O Identify OUTPUT
        self.IO_INPUT(IR.byte[4])  # I/O Identify INPUT
        self.IO_DATA_ADDRESS(IR.byte[5])  # I/O Identify INPUT
        self.AND_STEP4_IO(self.State_Machine.byte[4], self.NonALUCodes[7], self.IO_OUTPUT)  # Step 4 I/O OUTPUT
        self.AND_STEP5_IO(self.State_Machine.byte[4], self.NonALUCodes[7], self.IO_INPUT)  # Step 5 I/O INPUT
        self.IOClock_Set(self.clock.clock_set, self.AND_STEP4_IO)  # Step 4  I/O OUTPUT
        self.IOClock_Enable(self.clock.clock_enable, self.AND_STEP5_IO)  # Step 5 I/O INPUT

        self.Bus1bit(self.State_Machine.byte[1], self.AND_STEP4_DATA, self.AND_STEP4_CLF, self.AND_STEP4_JMPIF)
        # Step1 IAR ADVANCE _OR_ Step 4 DATA _OR_ Step 4 CLF _OR_ Step 4 JMPIF

        self.Enable_IAR_DATA(self.clock.clock_enable, self.AND_STEP4_DATA)  # Step 4 DATA
        self.Enable_IAR_JUMP(self.clock.clock_enable, self.AND_STEP4_JUMP)  # Step 4 JUMP
        self.Enable_IAR_IAR_ADV(self.clock.clock_enable, self.State_Machine.byte[1])  # Step1 IAR ADVANCE
        self.Enable_IAR_JMPIF(self.clock.clock_enable, self.AND_STEP4_JMPIF)  # Step 4 JMPIF
        self.Enable_IAR(self.Enable_IAR_DATA, self.Enable_IAR_IAR_ADV, self.Enable_IAR_JUMP, self.Enable_IAR_JMPIF)

        self.Set_IAR_IAR_ADV(self.clock.clock_set, self.State_Machine.byte[3])  # Step3 IAR ADVANCE
        self.Set_IAR_DATA(self.clock.clock_set, self.AND_STEP6_DATA)  # Step 6 DATA
        self.Set_IAR_JMPR(self.clock.clock_set, self.AND_STEP4_JMPR)  # Step 4 JMPR
        self.Set_IAR_JUMP(self.clock.clock_set, self.AND_STEP5_JUMP)  # Step 5 JUMP
        self.Set_IAR5_JMPIF(self.clock.clock_set, self.AND_STEP5_JMPIF)  # Step 5 JMPIF
        self.Set_IAR6_JMPIF(self.clock.clock_set, self.AND_STEP6_JMPIF)  # Step 6 JMPIF
        self.Set_IAR(self.Set_IAR_IAR_ADV, self.Set_IAR_DATA, self.Set_IAR_JMPR,
                            self.Set_IAR_JUMP, self.Set_IAR5_JMPIF, self.Set_IAR6_JMPIF)

        self.Set_IR(self.clock.clock_set, self.State_Machine.byte[2])  # Step2

        self.ALU_Instr_S6_AND(IR.byte[1], IR.byte[2], IR.byte[3])  # Step6   ALU
        self.ALU_Instr_S6_NOT(self.ALU_Instr_S6_AND)  # Step6    ALU

        self.Enable_RegB_ALU(self.State_Machine.byte[4], IR.byte[0])  # Step4  ALU
        self.Enable_RegB_STORE(self.State_Machine.byte[5], self.NonALUCodes[1])  # Step 5   STORE
        self.Enable_RegB_JMPR(self.State_Machine.byte[4], self.NonALUCodes[3])  # Step 4 JMPR
        self.Enable_RegB_IO(self.clock.clock_enable, self.AND_STEP4_IO)  # Step 4 I/O OUTPUT
        self.Enable_RegB(self.Enable_RegB_STORE, self.Enable_RegB_ALU, self.Enable_RegB_JMPR, self.Enable_RegB_IO)  # OR over Steps
        self.LOAD_or_STORE(self.NonALUCodes[0], self.NonALUCodes[1])
        self.Enable_RegA_ALU(IR.byte[0], self.State_Machine.byte[5])  # Step5  ALU
        self.Set_Flags_ALU(self.clock.clock_set, IR.byte[0], self.State_Machine.byte[5])  # Step5  ALU
        self.Set_Flags_CLF(self.clock.clock_set, self.NonALUCodes[6], self.State_Machine.byte[4])  # Step4  CLF
        self.Set_Flags(self.Set_Flags_ALU, self.Set_Flags_CLF)  # OR over Steps

        self.Set_CarryFlag_PostALU(self.clock.clock_set, IR.byte[0], self.State_Machine.byte[6])  # Step6 Delayed CarryIn Flag
        self.Set_CarryFlag_CLF(self.clock.clock_set, self.NonALUCodes[6], self.State_Machine.byte[4])  # Delayed CarryIn Flag Reset
        self.Set_CarryFlag(self.Set_CarryFlag_PostALU, self.Set_CarryFlag_CLF)
        self.Enable_CarryFlag(self.clock.clock_enable, IR.byte[0], self.State_Machine.byte[5]) # CarryIn to ALU is enabled only in ALU Command Step 5
        self.AND_STEP5_ALU(IR.byte[0], self.State_Machine.byte[5])  # Avoid feedback loop: Step 5 and ALU Instruction: Disable carry flag

        self.Enable_RegA_LOAD_STORE(self.State_Machine.byte[4], self.LOAD_or_STORE)  # Step 4  LOAD AND STORE
        self.Enable_RegA(self.Enable_RegA_ALU, self.Enable_RegA_LOAD_STORE)  # OR over Steps
        self.Set_RegB_ALU(self.State_Machine.byte[6], IR.byte[0], self.ALU_Instr_S6_NOT)  # Step6  ALU
        self.Set_RegB_LOAD(self.State_Machine.byte[5], self.NonALUCodes[0])  # Step 5   LOAD
        self.Set_RegB_DATA(self.State_Machine.byte[5], self.NonALUCodes[2])  # Step 5 DATA
        self.Set_RegB_IO(self.clock.clock_set, self.AND_STEP5_IO)  # Step 5 I/O INPUT
        self.Set_RegB(self.Set_RegB_ALU, self.Set_RegB_LOAD, self.Set_RegB_DATA, self.Set_RegB_IO)  # OR over Steps

        self.Set_ACC_Advance_IAR(self.clock.clock_set, self.State_Machine.byte[1])  # Step1
        self.Set_ACC_ALU_Operation(self.clock.clock_set, IR.byte[0], self.State_Machine.byte[5])  # Step5  ALU
        self.Set_ACC_DATA(self.clock.clock_set, self.AND_STEP4_DATA)  # Step 4 DATA
        self.Set_ACC_JMPIF(self.clock.clock_set, self.AND_STEP4_JMPIF)  # Step 4 JMPIF
        self.Set_ACC(self.Set_ACC_ALU_Operation, self.Set_ACC_Advance_IAR, self.Set_ACC_DATA, self.Set_ACC_JMPIF)  # OR over Steps

        self.Enable_ACC_DATA(self.clock.clock_enable, self.AND_STEP6_DATA)  # Step 6 DATA
        self.Enable_ACC_Advance_IAR(self.clock.clock_enable, self.State_Machine.byte[3])  # Step3
        self.Enable_ACC_ALU_Operation(self.Set_RegB_ALU, self.clock.clock_enable)  # Step6   ALU
        self.Enable_ACC_JMPIF(self.clock.clock_enable, self.AND_STEP5_JMPIF)  # Step 5 JMPIF
        self.Enable_ACC(self.Enable_ACC_ALU_Operation, self.Enable_ACC_JMPIF,
                               self.Enable_ACC_Advance_IAR, self.Enable_ACC_DATA)  # OR over Steps

        self.Set_MAR_ADVANCE_IAR(self.clock.clock_set, self.State_Machine.byte[1])  # Step1
        self.Set_MAR_LOAD_and_STORE(self.clock.clock_set, self.Enable_RegA_LOAD_STORE)  # Step 4  LOAD and STORE
        self.Set_MAR_DATA(self.clock.clock_set, self.AND_STEP4_DATA)  # Step 4 DATA
        self.Set_MAR_JUMP(self.clock.clock_set, self.AND_STEP4_JUMP)  # Step 4 JUMP
        self.Set_MAR_JMPIF(self.clock.clock_set, self.AND_STEP4_JMPIF)  # Step 4 JMPIF
        self.Set_MAR(self.Set_MAR_ADVANCE_IAR, self.Set_MAR_LOAD_and_STORE,
                            self.Set_MAR_DATA, self.Set_MAR_JUMP, self.Set_MAR_JMPIF)  # OR over Steps

        self.Enable_RAM_DATA(self.clock.clock_enable, self.AND_STEP5_DATA)  # Step 5 DATA
        self.Enable_RAM_ADVANCE_IAR(self.clock.clock_enable, self.State_Machine.byte[2])  # Step2
        self.Enable_RAM_LOAD(self.clock.clock_enable, self.Set_RegB_LOAD)  # Step 5    LOAD
        self.Enable_RAM_JUMP(self.clock.clock_enable, self.AND_STEP5_JUMP)  # Step 5    JUMP
        self.Enable_RAM_JMPIF(self.clock.clock_enable, self.AND_STEP6_JMPIF)  # Step 6 JMPIF
        self.Enable_RAM(self.Enable_RAM_ADVANCE_IAR, self.Enable_RAM_LOAD, self.Enable_RAM_DATA,
                               self.Enable_RAM_JUMP, self.Enable_RAM_JMPIF)  # OR over Steps

        self.Set_RAM(self.Enable_RegB_STORE, self.clock.clock_set)  # Step 5    STORE

        self.Set_TMP(self.Enable_RegB_ALU, self.clock.clock_set)  # Step4    ALU

        self.ALU_OP[0](IR.byte[0], self.State_Machine.byte[5], IR.byte[1])  # Step5    ALU
        self.ALU_OP[1](IR.byte[0], self.State_Machine.byte[5], IR.byte[2])  # Step5    ALU
        self.ALU_OP[2](IR.byte[0], self.State_Machine.byte[5], IR.byte[3])  # Step5    ALU

        self.Decoder_RA(IR.byte[4], IR.byte[5])
        self.Decoder_RB(IR.byte[6], IR.byte[7])
        self.Set_R[0](self.clock.clock_set, self.Decoder_RB.byte[0], self.Set_RegB)
        self.Set_R[1](self.clock.clock_set, self.Decoder_RB.byte[1], self.Set_RegB)
        self.Set_R[2](self.clock.clock_set, self.Decoder_RB.byte[2], self.Set_RegB)
        self.Set_R[3](self.clock.clock_set, self.Decoder_RB.byte[3], self.Set_RegB)
        self.Enable_RB[0](self.clock.clock_enable, self.Decoder_RB.byte[0], self.Enable_RegB)
        self.Enable_RB[1](self.clock.clock_enable, self.Decoder_RB.byte[1], self.Enable_RegB)
        self.Enable_RB[2](self.clock.clock_enable, self.Decoder_RB.byte[2], self.Enable_RegB)
        self.Enable_RB[3](self.clock.clock_enable, self.Decoder_RB.byte[3], self.Enable_RegB)
        self.Enable_RA[0](self.clock.clock_enable, self.Decoder_RA.byte[0], self.Enable_RegA)
        self.Enable_RA[1](self.clock.clock_enable, self.Decoder_RA.byte[1], self.Enable_RegA)
        self.Enable_RA[2](self.clock.clock_enable, self.Decoder_RA.byte[2], self.Enable_RegA)
        self.Enable_RA[3](self.clock.clock_enable, self.Decoder_RA.byte[3], self.Enable_RegA)
        self.Enable_R[0](self.Enable_RA[0], self.Enable_RB[0])
        self.Enable_R[1](self.Enable_RA[1], self.Enable_RB[1])
        self.Enable_R[2](self.Enable_RA[2], self.Enable_RB[2])
        self.Enable_R[3](self.Enable_RA[3], self.Enable_RB[3])



