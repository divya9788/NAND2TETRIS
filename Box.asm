// Author: Chirag Chanchal (chiragchanchal)
// Project: Nand2Tetris - Capstone (Keyboard-Controlled Screen Box)
// Remarks: Original implementation by Chirag Chanchal. All rights reserved.
//
// Parameter guide for roll-number suffix K (last 3 digits of roll number):
//   Starting row   = K
//   Start address  = 16384 + (K * 32)
//   Width (pixels) = 16 * ((K mod 4) + 1)  -> words per row = (K mod 4) + 1
//   Height (rows)  = 20
//
// Configured below with K = 71 from roll number 2501010071:
//   Start address = 16384 + (71 * 32) = 18656
//   Width         = 16 * ((71 mod 4) + 1) = 64 px (4 words per row)
//   Height        = 20 rows

(MAIN_LOOP)
    @KBD
    D=M
    @SET_BLACK
    D;JGT

    // No key pressed -> clear box (white)
    @color
    M=0
    @START_DRAW
    0;JMP

(SET_BLACK)
    // Key pressed -> fill box (black)
    @color
    M=-1

(START_DRAW)
    @18656
    D=A
    @rowAddr
    M=D

    @20
    D=A
    @rowsLeft
    M=D

(ROW_LOOP)
    @rowAddr
    D=M
    @wordAddr
    M=D

    // Number of 16-bit screen words per row = (71 mod 4) + 1 = 4
    @4
    D=A
    @colsLeft
    M=D

(COL_LOOP)
    @color
    D=M
    @wordAddr
    A=M
    M=D

    @wordAddr
    M=M+1

    @colsLeft
    MD=M-1
    @COL_LOOP
    D;JGT

    // Advance by 32 words (512 pixels / 16 bits per word) to next screen row
    @32
    D=A
    @rowAddr
    M=D+M

    @rowsLeft
    MD=M-1
    @ROW_LOOP
    D;JGT

    @MAIN_LOOP
    0;JMP
