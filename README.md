# scott_cpu
Simulation of the Scott CPU
following "But How Do It Know?" by J Clark Scott (2009)
http://www.buthowdoitknow.com/

Note:
	- Stepper from book is called State Machine in this simulation
	- Feedback loop from Carry Flag Register to ALU during calculation step was avoided by joining another delayed register in the circuit

computer.py is the executable script that will start the execution of the
programm specified during boot process via the interpreter.

Not yet fully tested

Todo: 
- Test left vs. right shift by implementing a multiplication algorithm
- get rid of logic gates as functions and switch to objects
- switch object count from the BIT to the NAND object
- comply with python naming conventions for instances vs. objects