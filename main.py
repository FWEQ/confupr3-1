"""Assembler stage1 (very simple, robust parsing)."""
import json
from pathlib import Path
import argparse
import sys
import re

OPCODES = {"ld_const":57, "load":228, "store":52}
SIZE = 7

def parse_lines(text):
    ir=[]
    for line in text.splitlines():
        orig = line
        line = line.split('#',1)[0].strip()
        if not line:
            continue

        parts = line.split()
        mnemonic = parts[0]
        if mnemonic not in OPCODES:
            raise ValueError(f"Unknown mnemonic '{mnemonic}' in: {orig}")

        m = re.search(r'([+-]?\d+)', line)
        if not m:
            raise ValueError(f"No numeric operand found in: {orig}")
        B = int(m.group(1))
        A = OPCODES[mnemonic]
        b = [0]*SIZE
        b[0] = A & 0xFF
        b[1] = B & 0xFF
        b[2] = (B >> 8) & 0xFF
        instr = {"mnemonic":mnemonic, "A":A, "B":B, "size":SIZE, "bytes":b}
        ir.append(instr)
    return ir

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--test", "-t", action="store_true")
    args = parser.parse_args(argv)
    p = Path(args.src)
    if not p.exists():
        print("Source not found", p)
        sys.exit(2)
    text = p.read_text(encoding="utf-8")
    try:
        ir = parse_lines(text)
    except Exception as e:
        print("Assembly error:", e)
        sys.exit(3)
    if args.test:
        print(json.dumps(ir, ensure_ascii=False, indent=2))
        return 0

    out = Path(args.out)
    raw = bytearray()
    for instr in ir:
        raw.extend(instr["bytes"])
    out.write_bytes(raw)
    print("Wrote", out, len(raw))
    return 0

if __name__ == '__main__':
    sys.exit(main())