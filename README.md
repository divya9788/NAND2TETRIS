# Nand2Tetris Hardware & Hack Assembler

**Author:** Chirag Chanchal (`chiragchanchal`)  
**Repository:** `https://github.com/chiragchanchal/nand2tetris`

> **Author Remarks & Notice:**  
> All HDL implementations, assembly programs, and assembler source code in this repository are authored by **Chirag Chanchal**. All rights reserved. Do not copy, redistribute, or submit this work without explicit written permission from the author.

---

## Repository Structure

```text
nand2tetris/
├── Project 1/                 # Elementary, 16-bit, and multi-way logic gates (.hdl)
│   ├── Not.hdl
│   ├── And.hdl
│   ├── Or.hdl
│   ├── Xor.hdl
│   ├── Mux.hdl
│   ├── DMux.hdl
│   ├── Not16.hdl
│   ├── And16.hdl
│   ├── Or16.hdl
│   ├── Mux16.hdl
│   ├── Or8Way.hdl
│   ├── Mux4Way16.hdl
│   ├── Mux8Way16.hdl
│   ├── DMux4Way.hdl
│   └── DMux8Way.hdl
├── Project 2/                 # Combinational arithmetic & Hack ALU (.hdl)
│   ├── HalfAdder.hdl
│   ├── FullAdder.hdl
│   ├── Add16.hdl
│   ├── Inc16.hdl
│   └── ALU.hdl
├── Project 3/                 # Sequential chips, registers, RAM hierarchy, PC (.hdl)
│   ├── Bit.hdl
│   ├── Register.hdl
│   ├── RAM8.hdl
│   ├── RAM64.hdl
│   ├── RAM512.hdl
│   ├── RAM4K.hdl
│   ├── RAM16K.hdl
│   └── PC.hdl
├── Project 5/                 # Hack Computer hardware architecture (.hdl)
│   ├── Memory.hdl
│   ├── CPU.hdl
│   └── Computer.hdl
├── Capstone/
│   └── assembler/             # Two-pass Hack Assembler & assembly programs
│       ├── assembler.py
│       ├── Add.asm / Add.hack
│       ├── Max.asm / Max.hack
│       ├── Rect.asm / Rect.hack
│       ├── Box.asm / Box.hack
│       ├── symbols.txt
│       └── NAND2Tetris_Capstone_Project_Report_Updated.pdf
├── NAND2Tetris_Capstone_Project_Report_Updated.pdf
├── nand.pdf                   # Reference specification / textbook PDF
└── README.md
```

---

## Usage

### 1. Assemble Hack Programs

Run the two-pass Python assembler from `Capstone/assembler/`:

```bash
python Capstone/assembler/assembler.py Capstone/assembler/Box.asm
```

This generates the 16-bit binary `.hack` output alongside a resolved `symbols.txt` file containing ROM labels and allocated RAM variables (starting at address `16`).

### 2. Customizing `Box.asm` for Roll-Number Parameter `K`

`Capstone/assembler/Box.asm` draws a `20`-row keyboard-controlled rectangle (black when a key is pressed, white when released):

- `Starting row = K`
- `Start address = 16384 + (K * 32)`
- `Width (pixels) = 16 * ((K mod 4) + 1)` (i.e. `(K mod 4) + 1` screen words per row)

By default, `Box.asm` uses `K = 71` from roll number `2501010071` (`@18656`, width `4` words = `64` pixels, height `20` rows). Update those two constants in `Box.asm` and re-run `assembler.py` if using a different `K`.
