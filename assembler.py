#!/usr/bin/env python3
"""Hack assembler. Usage: python assembler.py Prog.asm  -> Prog.hack
Extra feature (K=13, K mod 3 = 1): clear error messages with line numbers.
"""
import re
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100",
    "A": "0110000", "!D": "0001101", "!A": "0110001", "-D": "0001111",
    "-A": "0110011", "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011", "A-D": "0000111",
    "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
SYMBOLS.update({f"R{i}": i for i in range(16)})

SYM_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


class AsmError(Exception):
    pass


def clean(line):
    """Remove comments and all whitespace."""
    return re.sub(r"\s+", "", line.split("//")[0])


def first_pass(lines, errors):
    """Record labels; return list of (line_number, instruction)."""
    table = dict(SYMBOLS)
    program = []
    for num, raw in enumerate(lines, 1):
        line = clean(raw)
        if not line:
            continue
        if line.startswith("("):
            if not (line.endswith(")") and SYM_RE.match(line[1:-1])):
                errors.append(f"Line {num}: invalid label '{line}'")
            else:
                table[line[1:-1]] = len(program)
            continue
        program.append((num, line))
    return table, program


def encode_a(body, table, state):
    if body.isdigit():
        value = int(body)
        if value > 32767:
            raise AsmError(f"address {value} is too large (max 32767)")
    elif SYM_RE.match(body):
        if body not in table:
            table[body] = state["next_var"]
            state["next_var"] += 1
        value = table[body]
    else:
        raise AsmError(f"invalid A-instruction '@{body}'")
    return format(value, "016b")


def encode_c(line):
    dest, comp, jump = "", line, ""
    if "=" in line:
        dest, comp = line.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if dest not in DEST:
        raise AsmError(f"invalid destination '{dest}'")
    if comp not in COMP:
        raise AsmError(f"invalid instruction (bad computation '{comp}')")
    if jump not in JUMP:
        raise AsmError(f"invalid jump '{jump}'")
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(lines):
    errors = []
    table, program = first_pass(lines, errors)
    state = {"next_var": 16}
    out = []
    for num, line in program:
        try:
            if line.startswith("@"):
                out.append(encode_a(line[1:], table, state))
            else:
                out.append(encode_c(line))
        except AsmError as e:
            errors.append(f"Line {num}: {e}")
    return out, errors


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError as e:
        print(f"Cannot open file: {e}")
        sys.exit(1)

    out, errors = assemble(lines)
    if errors:
        for e in errors:
            print(e)
        print(f"Assembly failed with {len(errors)} error(s). No .hack file written.")
        sys.exit(1)

    with open(path[:-4] + ".hack", "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"OK: wrote {len(out)} instructions to {path[:-4]}.hack")


if __name__ == "__main__":
    main()
