// Author: Chirag Chanchal (chiragchanchal)
// Project: Nand2Tetris - Capstone (Hack Assembly)
// Remarks: Original implementation by Chirag Chanchal. All rights reserved.
// Description: Draws a 16x16-pixel black rectangle at top-left of screen.

    @16
    D=A
    @rowsLeft
    M=D
    @SCREEN
    D=A
    @pixelAddr
    M=D

(DRAW_ROW)
    @pixelAddr
    A=M
    M=-1

    @32
    D=A
    @pixelAddr
    M=D+M

    @rowsLeft
    MD=M-1
    @DRAW_ROW
    D;JGT

(HALT)
    @HALT
    0;JMP
