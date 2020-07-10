# scott_cpu
Simulation of the Scott CPU
following "But How Do It Know?" by J Clark Scott (2009)

http://www.buthowdoitknow.com/

Computer is currently programmed to
Calculate 19 mod (2 x 4), store the result in RAM, and then shut down

Note:

	- Stepper from book is called State Machine in this simulation
	- Feedback loop from Carry Flag Register to ALU during calculation step was avoided by joining another delayed register in the circuit
	- I/O Bus is dangling out of the case

**computer.py** is the executable script that will start the execution of the
programm specified during boot process via the interpreter.