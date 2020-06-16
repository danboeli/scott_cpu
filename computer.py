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

    def update(self):
        self.Control.update(self.IR)
        self.BUS.reset()

        for i in range(2):
            # Loop through this twice, in order to ensure that Bus can travel everywhere

            # IAR I/O connected to BUS
            self.IAR.update(self.Control.Set_IAR, self.Control.Enable_IAR, self.BUS)
            self.BUS.update(self.IAR)

            # IR I/ connected to BUS, /O TBD
            self.IR.update(self.Control.Set_IR, self.BUS)

            # RAM I/O connected to BUS
            self.RAM.update(self.Control.Set_RAM, self.Control.Enable_RAM, self.BUS,
                            self.Control.Set_MAR, self.BUS)
            self.BUS.update(self.RAM)

            # R0-3 I/O connected to BUS
            self.R[0].update(self.Control.Set_R[0], self.Control.Enable_R[0], self.BUS)
            self.BUS.update(self.R[0])
            self.R[1].update(self.Control.Set_R[1], self.Control.Enable_R[1], self.BUS)
            self.BUS.update(self.R[1])
            self.R[2].update(self.Control.Set_R[2], self.Control.Enable_R[2], self.BUS)
            self.BUS.update(self.R[2])
            self.R[3].update(self.Control.Set_R[3], self.Control.Enable_R[3], self.BUS)
            self.BUS.update(self.R[3])

            # TMP I/ connect to BUS, /O connected to BUS1
            self.TMP.update(self.Control.Set_TMP, self.BUS)
            self.BUS1.update(self.TMP, self.Control.Bus1bit)
            # ALU I/ connected to BUS1, /O connected to ACC
            self.ALU.update(self.BUS, self.BUS1, self.Control.CarryIn, self.Control.ALU_OP)

            # ACC I/ connected to ALU, /O connected to BUS
            self.ACC.update(self.Control.Set_ACC, self.Control.Enable_ACC, self.ALU)
            self.BUS.update(self.ACC)


class Interpreter(Byte):
    def update(self, cmd1, *cmd2):
        if cmd1 == 'ADD': self.initial_set(np.array([0, 0, 0, 0, 0, 0, 0, 1]))
        if cmd1 == 'SHL': self.initial_set(np.array([0, 0, 0, 0, 1, 0, 0, 1])) # Todo: Swap SHL / SHR??
        if cmd1 == 'SHR': self.initial_set(np.array([0, 0, 0, 0, 0, 1, 0, 1])) # Todo: Swap SHL / SHR??
        if cmd1 == 'NOT': self.initial_set(np.array([0, 0, 0, 0, 1, 1, 0, 1]))
        if cmd1 == 'AND': self.initial_set(np.array([0, 0, 0, 0, 0, 0, 1, 1]))
        if cmd1 == 'OR': self.initial_set(np.array([0, 0, 0, 0, 1, 0, 1, 1]))
        if cmd1 == 'XOR': self.initial_set(np.array([0, 0, 0, 0, 0, 1, 1, 1]))
        if cmd1 == 'CMP': self.initial_set(np.array([0, 0, 0, 0, 1, 1, 1, 1]))
        if cmd1 == 'LOAD': self.initial_set(np.array([0, 0, 0, 0, 0, 0, 0, 0]))
        if cmd1 == 'STORE': self.initial_set(np.array([0, 0, 0, 0, 1, 0, 0, 0]))
        if cmd2[0] == 'R0':    self.byte[4].state, self.byte[5].state = 0, 0
        if cmd2[0] == 'R1':    self.byte[4].state, self.byte[5].state = 0, 1
        if cmd2[0] == 'R2':    self.byte[4].state, self.byte[5].state = 1, 0
        if cmd2[0] == 'R3':    self.byte[4].state, self.byte[5].state = 1, 1
        if cmd2[1] == 'R0':    self.byte[6].state, self.byte[7].state = 0, 0
        if cmd2[1] == 'R1':    self.byte[6].state, self.byte[7].state = 0, 1
        if cmd2[1] == 'R2':    self.byte[6].state, self.byte[7].state = 1, 0
        if cmd2[1] == 'R3':    self.byte[6].state, self.byte[7].state = 1, 1
        

class BootProcess:
    def __init__(self, pointer=0):
        self.AddressPointer = pointer
        self.pointer_bin = np.zeros(8, dtype=int)
        self.pointer = np.zeros(8, dtype=int)
        self.Address = Byte()
        self.Address.initial_set(np.array([0, 0, 0, 0, 0, 0, 0, 0]))
        self.interpreter = Interpreter()

    def update(self, computer, cmd1, *cmd2):
        
        if isinstance(cmd1, str):
            self.interpreter.update(cmd1, cmd2[0], cmd2[1])
        if isinstance(cmd1, (np.ndarray, np.generic)):
            self.interpreter.initial_set(cmd1)

        computer.RAM.initial_RAM_set(self.Address, self.interpreter)
        
        self.AddressPointer = self.AddressPointer + 1

        self.pointer_bin = np.array([int(x) for x in list('{0:0b}'.format(self.AddressPointer))])
        for i in range(8 - len(self.pointer_bin), 8):
            self.pointer[i] = self.pointer_bin[i - 8 + len(self.pointer_bin)]
        self.Address.initial_set(self.pointer)
        self.pointer = np.array([0, 0, 0, 0, 0, 0, 0, 0])


def run_computer(run_time):
    # t_clock = np.zeros(run_time, dtype=float)
    # t_clock_set = np.zeros(run_time, dtype=float)
    # t_clock_enable = np.zeros(run_time, dtype=float)
    # t_step = np.zeros([run_time, 8], dtype=float)

    my_computer = Computer()
    booter = BootProcess()

    # Boot to RAM
    booter.update(my_computer, 'LOAD', 'R0', 'R1')  # Load Add R0 to R1
    booter.update(my_computer, 'ADD', 'R3', 'R1')  # Add R1 + R3 and store in R1
    booter.update(my_computer, 'STORE', 'R2', 'R1')  # Store R1 at R2
    booter.update(my_computer, np.array([1, 1, 0, 0, 0, 1, 0, 1]))  # Data to load initially to R1
    booter.update(my_computer, np.array([0, 0, 1, 0, 0, 1, 0, 1]))

    # Boot to Register
    my_computer.R[0].Memory.initial_set(np.array([0, 0, 0, 0, 0, 0, 1, 1]))
    my_computer.R[3].Memory.initial_set(np.array([0, 0, 0, 0, 0, 1, 0, 1]))
    my_computer.R[2].Memory.initial_set(np.array([0, 0, 0, 1, 0, 0, 0, 1]))

    for t in range(run_time):
        print('--t= {}'.format(t))
        print('Stepper = ', end='')
        my_computer.Control.Stepper.report()
        # print('IAR = ', end='')
        # my_computer.IAR.Memory.report()
        # print('IR = ', end='')
        # my_computer.IR.report()
        print('R0 = ', end='')
        my_computer.R[0].Memory.report()
        print('R1 = ', end='')
        my_computer.R[1].Memory.report()
        print('R2 = ', end='')
        my_computer.R[2].Memory.report()
        print('R3 = ', end='')
        my_computer.R[3].Memory.report()
        print('RAM@[0, 0, 0, 1, 0, 0, 0, 1] = ', end='')
        my_computer.RAM.report_Address(my_computer.R[2].Memory)

        my_computer.update()

        # t_clock[t] = my_computer.Control.clock.clock.state
        # t_step[t, :] = np.array(my_computer.Control.Stepper.get_data())

    # oplot = plt.figure()
    #
    # for i in range(1, 8):
    #     enhance_for_plot(t_step[:, i], run_time, oplot)
    # enhance_for_plot(t_clock, run_time, oplot, 'r-')
    #
    # plt.axis([0, run_time, -0.1, 1.1])
    # plt.show()


runtime = 150
pr = cProfile.Profile()
pr.enable()
run_computer(runtime)
pr.disable()
pr.print_stats(sort='cumtime')
