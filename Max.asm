// Author: Chirag Chanchal (chiragchanchal)
// Project: Nand2Tetris - Capstone (Hack Assembly)
// Remarks: Original implementation by Chirag Chanchal. All rights reserved.
// Description: Computes R2 = max(R0, R1).

    @R0
    D=M
    @R1
    D=D-M
    @FIRST_IS_MAX
    D;JGT

    // R1 >= R0
    @R1
    D=M
    @STORE_MAX
    0;JMP

(FIRST_IS_MAX)
    @R0
    D=M

(STORE_MAX)
    @R2
    M=D

(HALT)
    @HALT
    0;JMP
