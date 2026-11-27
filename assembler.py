# Author: Chirag Chanchal (chiragchanchal)
# Project: Nand2Tetris - Capstone (Two-Pass Hack Assembler)
# Remarks: Original implementation by Chirag Chanchal. All rights reserved.

"""Two-pass Hack Assembler translating .asm source files into 16-bit .hack binary."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SYMBOL_PATTERN = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")
MAX_ROM_ADDRESS = 32767
VAR_BASE_ADDRESS = 16

BASE_SYMBOLS: dict[str, int] = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    **{f"R{idx}": idx for idx in range(16)},
}

DEST_TABLE: dict[str, str] = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP_TABLE: dict[str, str] = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

COMP_TABLE: dict[str, str] = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}


@dataclass(frozen=True)
class SourceLine:
    """Single cleaned Hack assembly instruction paired with its 1-based line number."""

    line_number: int
    text: str


@dataclass(frozen=True)
class AssemblyResult:
    """Output artifacts produced by assembling a Hack .asm file."""

    machine_code: list[str]
    symbol_table: dict[str, int]
    labels: dict[str, int]
    warnings: list[str]


def preprocess_lines(source_text: str) -> list[SourceLine]:
    """Remove comments and blank lines while retaining original line numbers."""
    cleaned: list[SourceLine] = []
    for line_number, raw_line in enumerate(source_text.splitlines(), start=1):
        code_part = raw_line.split("//", 1)[0].strip()
        if code_part:
            cleaned.append(SourceLine(line_number=line_number, text=code_part))
    return cleaned


def run_first_pass(
    instructions: list[SourceLine],
) -> tuple[dict[str, int], dict[str, int], list[str], list[str]]:
    """Collect ROM label addresses and detect invalid or duplicate labels."""
    symbol_table = dict(BASE_SYMBOLS)
    labels: dict[str, int] = {}
    warnings: list[str] = []
    errors: list[str] = []
    rom_address = 0

    for item in instructions:
        if item.text.startswith("(") and item.text.endswith(")"):
            label = item.text[1:-1].strip()
            if not SYMBOL_PATTERN.fullmatch(label):
                errors.append(f"Line {item.line_number}: invalid label '{label}'")
                continue
            if label in symbol_table:
                warnings.append(
                    f"Line {item.line_number}: duplicate or predefined label '{label}' ignored"
                )
                continue
            symbol_table[label] = rom_address
            labels[label] = rom_address
        else:
            rom_address += 1

    return symbol_table, labels, warnings, errors


def encode_a_instruction(
    instruction: str,
    symbol_table: dict[str, int],
    next_var_addr: list[int],
) -> str:
    """Translate an @value or @symbol A-instruction to 16-bit binary."""
    token = instruction[1:].strip()
    if not token:
        raise ValueError("empty A-instruction")

    if token.isdigit():
        address = int(token)
    elif token in symbol_table:
        address = symbol_table[token]
    else:
        if not SYMBOL_PATTERN.fullmatch(token):
            raise ValueError(f"invalid symbol '{token}'")
        address = next_var_addr[0]
        next_var_addr[0] += 1
        symbol_table[token] = address

    if address < 0 or address > MAX_ROM_ADDRESS:
        raise ValueError(f"address {address} out of 15-bit range (0..{MAX_ROM_ADDRESS})")

    return format(address, "016b")


def encode_c_instruction(instruction: str) -> str:
    """Translate a dest=comp;jump C-instruction to 16-bit binary."""
    compact = re.sub(r"\s+", "", instruction)
    if compact.count("=") > 1 or compact.count(";") > 1:
        raise ValueError(f"malformed C-instruction '{instruction}'")

    if "=" in compact:
        dest, remainder = compact.split("=", 1)
    else:
        dest, remainder = "", compact

    if ";" in remainder:
        comp, jump = remainder.split(";", 1)
    else:
        comp, jump = remainder, ""

    if dest not in DEST_TABLE:
        raise ValueError(f"invalid destination '{dest}'")
    if comp not in COMP_TABLE:
        raise ValueError(f"invalid computation '{comp}'")
    if jump not in JUMP_TABLE:
        raise ValueError(f"invalid jump '{jump}'")

    return f"111{COMP_TABLE[comp]}{DEST_TABLE[dest]}{JUMP_TABLE[jump]}"


def run_second_pass(
    instructions: list[SourceLine],
    symbol_table: dict[str, int],
) -> tuple[list[str], list[str]]:
    """Encode instructions into binary and assign RAM addresses to variables."""
    machine_code: list[str] = []
    errors: list[str] = []
    next_var_addr = [VAR_BASE_ADDRESS]

    for item in instructions:
        if item.text.startswith("(") and item.text.endswith(")"):
            continue
        try:
            if item.text.startswith("@"):
                binary = encode_a_instruction(item.text, symbol_table, next_var_addr)
            else:
                binary = encode_c_instruction(item.text)
            machine_code.append(binary)
        except ValueError as exc:
            errors.append(f"Line {item.line_number}: {exc}")

    return machine_code, errors


def assemble_source(source_text: str) -> AssemblyResult:
    """Assemble Hack assembly source text and return binary plus symbol metadata."""
    instructions = preprocess_lines(source_text)
    symbol_table, labels, warnings, first_errors = run_first_pass(instructions)
    machine_code, second_errors = run_second_pass(instructions, symbol_table)

    all_errors = first_errors + second_errors
    if all_errors:
        raise ValueError("\n".join(all_errors))

    return AssemblyResult(
        machine_code=machine_code,
        symbol_table=symbol_table,
        labels=labels,
        warnings=warnings,
    )


def format_symbols_report(
    symbol_table: dict[str, int],
    labels: dict[str, int],
) -> str:
    """Format resolved labels and user variables for symbols.txt."""
    lines = ["# Labels (ROM addresses)"]
    for name, addr in labels.items():
        lines.append(f"{name}\t{addr}")

    lines.append("")
    lines.append("# Variables (RAM addresses)")
    for name, addr in symbol_table.items():
        if name not in BASE_SYMBOLS and name not in labels:
            lines.append(f"{name}\t{addr}")

    return "\n".join(lines) + "\n"


def resolve_input_path(asm_path: Path) -> Path:
    """Resolve an .asm path from CWD or fall back to the assembler script directory."""
    if asm_path.exists():
        return asm_path
    if not asm_path.is_absolute():
        script_relative = Path(__file__).resolve().parent / asm_path
        if script_relative.exists():
            return script_relative
    return asm_path


def assemble_file(
    asm_path: Path,
    output_path: Path | None = None,
    symbols_path: Path | None = None,
) -> AssemblyResult:
    """Read an .asm file, assemble it, and write .hack and symbols output files."""
    resolved_path = resolve_input_path(asm_path)
    source_text = resolved_path.read_text(encoding="utf-8-sig")
    result = assemble_source(source_text)

    hack_dest = output_path or resolved_path.with_suffix(".hack")
    hack_content = "\n".join(result.machine_code) + ("\n" if result.machine_code else "")
    hack_dest.write_text(hack_content, encoding="utf-8")

    sym_dest = symbols_path or hack_dest.with_name("symbols.txt")
    sym_dest.write_text(
        format_symbols_report(result.symbol_table, result.labels),
        encoding="utf-8",
    )
    return result


def prompt_for_input_file() -> Path | None:
    """Prompt interactively for an .asm file when invoked without CLI arguments."""
    script_dir = Path(__file__).resolve().parent
    available = sorted(
        {p.name for p in Path.cwd().glob("*.asm")} | {p.name for p in script_dir.glob("*.asm")}
    )
    if available:
        print("Available .asm files:", ", ".join(available))
    default_choice = "Box.asm" if "Box.asm" in available else (available[0] if available else "")
    prompt = f"Enter .asm file path [{default_choice}]: " if default_choice else "Enter .asm file path: "
    try:
        entered = input(prompt).strip().strip('"').strip("'")
    except EOFError:
        return None
    chosen = entered or default_choice
    return Path(chosen) if chosen else None


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the Hack Assembler."""
    parser = argparse.ArgumentParser(
        description="Assemble a Hack .asm file into 16-bit binary .hack machine code."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the input .asm file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional path for the generated .hack file",
    )
    parser.add_argument(
        "--symbols",
        type=Path,
        default=None,
        help="Optional path for the generated symbols table file",
    )
    args = parser.parse_args(argv)

    input_path = args.input_file
    if input_path is None:
        if sys.stdin.isatty():
            input_path = prompt_for_input_file()
        if input_path is None:
            parser.print_usage(sys.stderr)
            return 1

    resolved_input = resolve_input_path(input_path)
    try:
        result = assemble_file(resolved_input, args.output, args.symbols)
    except FileNotFoundError:
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print("Assembly failed:", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1

    for warning in result.warnings:
        print(f"Warning: {warning}")

    out_path = args.output or resolved_input.with_suffix(".hack")
    sym_path = args.symbols or out_path.with_name("symbols.txt")
    print(f"Assembled {len(result.machine_code)} instructions -> {out_path}")
    print(f"Symbols written -> {sym_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
