from logic_functions import *


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


class Stepper(Byte):
    def __init__(self):
        super().__init__()
        self.Mem = [MemoryBit() for i in range(12)]
        self.StepOR = ORBit()
        self.StepAND = [ANDBit() for i in range(5)]
        self.ClockOR = ORBit()
        self.InvClockOR = ORBit()
        self.InvClock = NOTBit()
        self.NotReset = NOTBit()
        self.Noter = [NOTBit() for i in range(6)]

    def update(self, clock, reset):
        self.NotReset.update(reset)
        self.InvClock.update(clock.clock)
        self.ClockOR.update(clock.clock, reset)
        self.InvClockOR.update(self.InvClock, reset)

        self.Mem[0].update(self.InvClockOR, self.NotReset)
        self.Mem[1].update(self.ClockOR, self.Mem[0])
        self.Noter[0].update(self.Mem[1])
        self.StepOR.update(reset, self.Noter[0])
        self.byte[1].update(self.StepOR)

        self.Mem[2].update(self.InvClockOR, self.Mem[1])
        self.Mem[3].update(self.ClockOR, self.Mem[2])
        self.Noter[1].update(self.Mem[3])
        self.StepAND[0].update(self.Mem[1], self.Noter[1])
        self.byte[2].update(self.StepAND[0])

        self.Mem[4].update(self.InvClockOR, self.Mem[3])
        self.Mem[5].update(self.ClockOR, self.Mem[4])
        self.Noter[2].update(self.Mem[5])
        self.StepAND[1].update(self.Mem[3], self.Noter[2])
        self.byte[3].update(self.StepAND[1])

        self.Mem[6].update(self.InvClockOR, self.Mem[5])
        self.Mem[7].update(self.ClockOR, self.Mem[6])
        self.Noter[3].update(self.Mem[7])
        self.StepAND[2].update(self.Mem[5], self.Noter[3])
        self.byte[4].update(self.StepAND[2])

        self.Mem[8].update(self.InvClockOR, self.Mem[7])
        self.Mem[9].update(self.ClockOR, self.Mem[8])
        self.Noter[4].update(self.Mem[9])
        self.StepAND[3].update(self.Mem[7], self.Noter[4])
        self.byte[5].update(self.StepAND[3])

        self.Mem[10].update(self.InvClockOR, self.Mem[9])
        self.Mem[11].update(self.ClockOR, self.Mem[10])
        self.Noter[5].update(self.Mem[11])
        self.StepAND[4].update(self.Mem[9], self.Noter[5])
        self.byte[6].update(self.StepAND[4])
        self.byte[7].update(self.Mem[11])
