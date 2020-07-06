# Simulation of the Scott CPU / Scott Computer

import cProfile
from building_blocks import *
from support_functions import *
import numpy as np


class Computer(Byte):
    # size = 8
    def __init__(self):
        super().__init__()
        self.R = [Register() for i in range(4)]
        self.RAM = RAM256byte()
        self.TMP = MemoryByte()
        self.BUS1 = Bus1()
        self.ALU = ArithmeticAndLogicUnit()
        self.ACC = Register()
        self.BUS = Bus()
        self.IAR = Register()
        self.IR = MemoryByte()
        self.Control = ControlUnit()
        self.Flags = FlagRegister()
        self.CarryOut = RegisterBit()
        self.IOBus = IOBus()

    def __call__(self):
        self.Control(self.IR, self.Flags)
        self.BUS.reset()

        for i in range(2):
            # Loop through this twice, in order to ensure that Bus can travel everywhere

            # IAR I/O connected to BUS
            self.IAR(self.Control.Set_IAR, self.Control.Enable_IAR, self.BUS)
            self.BUS(self.IAR)

            # IR I/ connected to BUS, /O TBD
            self.IR(self.Control.Set_IR, self.BUS)

            # RAM I/O connected to BUS
            self.RAM(self.Control.Set_RAM, self.Control.Enable_RAM, self.BUS,
                     self.Control.Set_MAR, self.BUS)
            self.BUS(self.RAM)

            # R0-3 I/O connected to BUS
            self.R[0](self.Control.Set_R[0], self.Control.Enable_R[0], self.BUS)
            self.BUS(self.R[0])
            self.R[1](self.Control.Set_R[1], self.Control.Enable_R[1], self.BUS)
            self.BUS(self.R[1])
            self.R[2](self.Control.Set_R[2], self.Control.Enable_R[2], self.BUS)
            self.BUS(self.R[2])
            self.R[3](self.Control.Set_R[3], self.Control.Enable_R[3], self.BUS)
            self.BUS(self.R[3])

            # TMP I/ connect to BUS, /O connected to BUS1
            self.TMP(self.Control.Set_TMP, self.BUS)
            self.BUS1(self.TMP, self.Control.Bus1bit)
            # ALU I/ connected to BUS1, /O connected to ACC
            self.ALU(self.BUS, self.BUS1, self.CarryOut, self.Control.ALU_OP)
            # FLAG I/ connected to ALU flags, /O connected to CU
            self.Flags(self.Control.Set_Flags,
                       self.ALU.Carry_out, self.ALU.larger, self.ALU.equal, self.ALU.Zero)
            self.CarryOut(self.Control.Set_CarryFlag, self.Control.Enable_CarryFlag, self.Flags.Carry)
            # ACC I/ connected to ALU, /O connected to BUS
            self.ACC(self.Control.Set_ACC, self.Control.Enable_ACC, self.ALU)
            self.BUS(self.ACC)

            self.IOBus(self.Control.IOClock_Set, self.Control.IOClock_Enable,
                       self.Control.IO_OUTPUT, self.Control.IO_DATA_ADDRESS, self.BUS)
            # I/O Bus are the loose ends currently dangling out of the computer


class Interpreter(Byte):
    def __call__(self, cmd1, *cmd2):
        if cmd1 == 'ADD':       self.initial_set(np.array([0, 0, 0, 0, 0, 0, 0, 1]))  # ALU 0
        if cmd1 == 'AND':       self.initial_set(np.array([0, 0, 0, 0, 0, 0, 1, 1]))  # ALU 1
        if cmd1 == 'SHR':       self.initial_set(np.array([0, 0, 0, 0, 1, 0, 0, 1]))  # ALU 2
        if cmd1 == 'XOR':       self.initial_set(np.array([0, 0, 0, 0, 0, 1, 1, 1]))  # ALU 3
        if cmd1 == 'SHL':       self.initial_set(np.array([0, 0, 0, 0, 0, 1, 0, 1]))  # ALU 4
        if cmd1 == 'OR':        self.initial_set(np.array([0, 0, 0, 0, 1, 0, 1, 1]))  # ALU 5
        if cmd1 == 'NOT':       self.initial_set(np.array([0, 0, 0, 0, 1, 1, 0, 1]))  # ALU 6
        if cmd1 == 'CMP':       self.initial_set(np.array([0, 0, 0, 0, 1, 1, 1, 1]))  # ALU 7

        if cmd1 == 'LOAD':      self.initial_set(
            np.array([0, 0, 0, 0, 0, 0, 0, 0]))  # CMD 0 Load RB from RAM Address RA
        if cmd1 == 'JUMP':      self.initial_set(
            np.array([0, 0, 0, 0, 0, 0, 1, 0]))  # CMD 1 Next go to the RAM Address stored in next Byte
        if cmd1 == 'DATA':      self.initial_set(
            np.array([0, 0, 0, 0, 0, 1, 0, 0]))  # CMD 2 Next Byte in RAM is data, store this in RB
        if cmd1 == 'CLF':       self.initial_set(np.array([0, 0, 0, 0, 0, 1, 1, 0]))  # CMD 3 Clear Flags
        if cmd1 == 'STORE':     self.initial_set(np.array([0, 0, 0, 0, 1, 0, 0, 0]))  # CMD 4 Store RB at RAM Address RA
        if cmd1 == 'JMPIF':     self.initial_set(
            np.array([0, 0, 0, 0, 1, 0, 1, 0]))  # CMD 5 Jump if to next RAM Address
        if cmd1 == 'JMPR':      self.initial_set(
            np.array([0, 0, 0, 0, 1, 1, 0, 0]))  # CMD 6 Next go to the RAM Address stored in RB
        if cmd1 == 'IN Data':   self.initial_set(np.array([0, 0, 0, 0, 1, 1, 1, 0]))  # CMD 7 INPUT Data
        if cmd1 == 'OUT Data':  self.initial_set(np.array([0, 0, 0, 1, 1, 1, 1, 0]))  # CMD 7 OUTPUT Data
        if cmd1 == 'IN Addr':   self.initial_set(np.array([0, 0, 0, 0, 1, 1, 1, 0]))  # CMD 7 INPUT Address
        if cmd1 == 'OUT Addr':  self.initial_set(np.array([0, 0, 1, 1, 1, 1, 1, 0]))  # CMD 7 OUTPUT Address

        if len(cmd2) == 4:
            self.byte[4].state = cmd2[0]
            self.byte[5].state = cmd2[1]
            self.byte[6].state = cmd2[2]
            self.byte[7].state = cmd2[3]
        if len(cmd2) == 1:
            if cmd2[0] == 'R0':     self.byte[6].state, self.byte[7].state = 0, 0
            if cmd2[0] == 'R1':     self.byte[6].state, self.byte[7].state = 0, 1
            if cmd2[0] == 'R2':     self.byte[6].state, self.byte[7].state = 1, 0
            if cmd2[0] == 'R3':     self.byte[6].state, self.byte[7].state = 1, 1
        if len(cmd2) == 2:
            if cmd2[0] == 'R0':     self.byte[4].state, self.byte[5].state = 0, 0
            if cmd2[0] == 'R1':     self.byte[4].state, self.byte[5].state = 0, 1
            if cmd2[0] == 'R2':     self.byte[4].state, self.byte[5].state = 1, 0
            if cmd2[0] == 'R3':     self.byte[4].state, self.byte[5].state = 1, 1
            if cmd2[1] == 'R0':     self.byte[6].state, self.byte[7].state = 0, 0
            if cmd2[1] == 'R1':     self.byte[6].state, self.byte[7].state = 0, 1
            if cmd2[1] == 'R2':     self.byte[6].state, self.byte[7].state = 1, 0
            if cmd2[1] == 'R3':     self.byte[6].state, self.byte[7].state = 1, 1


class BootProcess:
    def __init__(self, pointer=0):
        self.AddressPointer = pointer
        self.pointer_bin = np.zeros(8, dtype=int)
        self.pointer = np.zeros(8, dtype=int)
        self.Address = Byte()
        self.Address.initial_set(np.array([0, 0, 0, 0, 0, 0, 0, 0]))
        self.interpreter = Interpreter()

    def __call__(self, computer, cmd1, *cmd2):

        if isinstance(cmd1, str):  # For commands
            if len(cmd2) == 4:
                self.interpreter(cmd1, cmd2[0], cmd2[1], cmd2[2], cmd2[3])
            if len(cmd2) == 2:
                self.interpreter(cmd1, cmd2[0], cmd2[1])
            if len(cmd2) == 1:
                self.interpreter(cmd1, cmd2[0])
            if len(cmd2) == 0:
                self.interpreter(cmd1)
        if isinstance(cmd1, (np.ndarray, np.generic)):  # For data
            self.interpreter.initial_set(cmd1)

        computer.RAM.initial_RAM_set(self.Address, self.interpreter)

        self.AddressPointer = self.AddressPointer + 1

        self.pointer_bin = np.array([int(x) for x in list('{0:0b}'.format(self.AddressPointer))])
        for i in range(8 - len(self.pointer_bin), 8):
            self.pointer[i] = self.pointer_bin[i - 8 + len(self.pointer_bin)]
        self.Address.initial_set(self.pointer)
        self.pointer = np.array([0, 0, 0, 0, 0, 0, 0, 0])


def run_computer():
    # t_clock = np.zeros(run_time, dtype=float)
    # t_clock_set = np.zeros(run_time, dtype=float)
    # t_clock_enable = np.zeros(run_time, dtype=float)
    # t_step = np.zeros([run_time, 8], dtype=float)

    my_computer = Computer()
    booter = BootProcess()
    goodbye_byte = Byte()
    multi_purpose_byte = Byte()
    goodbye_byte.initial_set(np.array([1, 1, 1, 1, 1, 1, 1, 1]))
    multi_purpose_byte.initial_set(np.array([1, 1, 1, 1, 1, 1, 1, 0]))

    # Calculate R1=2 x R0=4 = R2
    booter(my_computer, 'DATA', 'R3')  # 0- Load Data to R3 as Stop Signal
    booter(my_computer, np.array([0, 0, 0, 0, 0, 0, 0, 1]))  # 1- Data to R3 "1"
    booter(my_computer, 'DATA', 'R1')  # 2- Load Data to R1 as Operand 2
    booter(my_computer, np.array([0, 0, 0, 0, 0, 0, 1, 0]))  # 3- Data to R1 "2"
    booter(my_computer, 'DATA', 'R0')  # 4- Load Data to R0 ad Operand 1
    booter(my_computer, np.array([0, 0, 0, 0, 0, 1, 0, 0]))  # 5- Data to R0 "4"
    booter(my_computer, 'XOR', 'R2', 'R2')  # 6- Make sure R2 is zero
    booter(my_computer, 'CLF')  # 7- Clear Flags TARGET 3
    booter(my_computer, 'SHR', 'R0', 'R0')  # 8- Shiftright R0 - only carry is relevant
    booter(my_computer, 'JMPIF', 1, 0, 0, 0)  # 9- JUMP to Address if carry is one
    booter(my_computer, np.array([0, 0, 0, 0, 1, 1, 0, 1]))  # 10- GOTO Target 1
    booter(my_computer, 'JUMP')  # 11- JUMP to Address if carry is zero
    booter(my_computer, np.array([0, 0, 0, 0, 1, 1, 1, 1]))  # 12- GOTO Target 2
    booter(my_computer, 'CLF')  # 13- Clear Flags TARGET 1
    booter(my_computer, 'ADD', 'R1', 'R2')  # 14- Add R2 = R1 + R2
    booter(my_computer, 'CLF')  # 15- Clear Flags TARGET 2
    booter(my_computer, 'SHL', 'R1', 'R1')  # 16- Shiftleft R1 - and repeat process
    booter(my_computer, 'SHL', 'R3', 'R3')  # 17- Shiftleft R3 - stop if carry is active
    booter(my_computer, 'JMPIF', 1, 0, 0, 0)  # 18- JUMP to Address if carry is one
    booter(my_computer, np.array([0, 0, 0, 1, 0, 1, 1, 0]))  # 19- GOTO Target 4
    booter(my_computer, 'JUMP')  # 20- JUMP to Address if carry is zero (not yet done)
    booter(my_computer, np.array([0, 0, 0, 0, 0, 1, 1, 1]))  # 21- GOTO Target 3
    booter(my_computer, 'XOR', 'R1', 'R1')  # 22 Target 4 XOR R1 - make sure its zero
    booter(my_computer, 'CLF')  # 23 clf
    booter(my_computer, 'ADD', 'R2', 'R1')  # 24 add R1+R2=R1
    booter(my_computer, 'CLF')  # 25 clf
    # Calculate R0=19 modulo R1=8
    # # -1- Load R0 from RAM
    booter(my_computer, 'DATA', 'R0')  # 26- Load Data to R0 as Operand 1
    booter(my_computer, np.array([0, 0, 0, 0, 1, 0, 1, 1]))  # 27- Data to R0 "11"
    booter(my_computer, 'XOR', 'R3', 'R3')  # 28 make sure r3 is zero
    booter(my_computer, 'CLF')  # 29 clf
    booter(my_computer, 'ADD', 'R1', 'R3')  # 30- Add R1 + 0 and check if result is zero
    booter(my_computer, 'JMPIF', 0, 0, 0, 1)  # 31- JUMP to Address 16 stored in next byte
    booter(my_computer, np.array([0, 0, 1, 1, 0, 0, 0, 0]))  # 32- GOTO GOODBYE
    # If R1 is bigger than R0 the result is R0
    booter(my_computer, 'CMP', 'R1', 'R0')  # 33- Compare R1 >= R0
    booter(my_computer, 'JMPIF', 0, 1, 0, 0)  # 34- JUMP to Address 16 stored in next byte
    booter(my_computer, np.array([0, 0, 1, 0, 1, 1, 0, 1]))  # 35- GOTO TARGET X1
    # -2-  Invert R1 and add 1
    booter(my_computer, 'DATA', 'R2')  # 36- Load 1 to R2 to add
    booter(my_computer, np.array([0, 0, 0, 0, 0, 0, 0, 1]))  # 37- Data to R2 "1"
    booter(my_computer, 'NOT', 'R1', 'R3')  # 38- Not R2 to R3
    booter(my_computer, 'ADD', 'R2', 'R3')  # 39- Add R2 + R3 and store in R3 as Result
    #  -5-  Calculate R0=R0-R1(orig) by calculating R0+R1(inverted,incremented) as long is R0 is bigger than R1
    booter(my_computer, 'ADD', 'R3', 'R0')  # 40- Add R3 + R0 and store in R0 as Result TARGET X2
    booter(my_computer, 'CLF')  # 41- Clear Flags
    booter(my_computer, 'CMP', 'R0', 'R1')  # 42- Compare R0 >= R1
    booter(my_computer, 'JMPIF', 0, 1, 0, 0)  # 43- JUMP to Address stored in next byte
    booter(my_computer, np.array([0, 0, 1, 0, 1, 0, 0, 0]))  # 44- GOTO TARGET X2
    #  -4-  - Save current value of R0
    booter(my_computer, 'DATA', 'R2')  # 45- Load Data to R2 as RAM Address TARGET X1
    booter(my_computer, np.array([1, 1, 1, 1, 1, 1, 1, 0]))  # 46- Data to R2 which is Result RAM Address
    booter(my_computer, 'STORE', 'R2', 'R0')  # 47- Store R0 at R2 in RAM

    # Goodbye Sequence

    booter(my_computer, 'DATA', 'R3')  # 48- Load Data to R3 as RAM Address of Goodbye Store
    booter(my_computer, np.array([1, 1, 1, 1, 1, 1, 1, 1]))  # - Goodbye Store
    booter(my_computer, 'DATA', 'R2')  # - Load Data to R2 as Goodbye Message
    booter(my_computer, np.array([0, 0, 0, 0, 0, 0, 0, 1]))  # - Goodbye Message
    booter(my_computer, 'STORE', 'R3', 'R2')  # - Store R2 at R3 in RAM

    t = 0

    print('Created Bits: {}'.format(
        Bit.bitcount))  # Switch bitcount from Bit to NAND after switch from logic functions to logic objects

    while my_computer.RAM.return_Address(goodbye_byte)[0] == 0:
        t = t + 1
        if ((t - 1) % 48 == 0) & (t > 1):
            print('t = {}'.format(t))
            print(my_computer.Control.State_Machine.__radd__('State Machine= ', order='byte'))
            print(my_computer.IR.__radd__('Instruction Register = ', order='byte'))
            print('Instruction Address Register = ' + my_computer.IAR.Memory)
            print('Larger Flag = ' + my_computer.Flags.Larger)
            print('Carry Flag = ' + my_computer.CarryOut.Memory)
            print('Zero Flag = ' + my_computer.Flags.Zero)
            print('R0 = ' + my_computer.R[0].Memory)
            print('R1 = ' + my_computer.R[1].Memory)
            print('R2 = ' + my_computer.R[2].Memory)
            print('R3 = ' + my_computer.R[3].Memory)
            print('RAM@[1, 1, 1, 1, 1, 1, 1, 0] = ' + my_computer.RAM.report_Address(multi_purpose_byte))

        my_computer()

        # t_clock[t] = my_computer.Control.clock.clock.state
        # t_step[t, :] = np.array(my_computer.Control.State_Machine.get_data())

    # oplot = plt.figure()
    #
    # for i in range(1, 8):
    #     enhance_for_plot(t_step[:, i], run_time, oplot)
    # enhance_for_plot(t_clock, run_time, oplot, 'r-')
    #
    # plt.axis([0, run_time, -0.1, 1.1])
    # plt.show()


pr = cProfile.Profile()
pr.enable()
run_computer()
pr.disable()
pr.print_stats(sort='cumtime')
