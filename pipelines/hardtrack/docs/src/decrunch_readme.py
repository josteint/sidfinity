#!/usr/bin/env python3
"""One-off 6502 emulator to decrunch the HardTrack "PRZECZYTAJ MNIE!" readme PRG.

The PRG (load $0801) is a self-displaying crunched note: BASIC `SYS 2059`
relocates a depacker to $0100 and runs it. We emulate the CPU, then dump
RAM regions that hold the decrunched PETSCII (it self-modifies into place).

Pure-Python minimal NMOS 6502 — enough opcodes for a cruncher (no decimal
mode used by crunchers). Reads the PRG read-only from tmp/, writes nothing
outside docs/.
"""
import sys

PRG = "/home/jtr/sidfinity/tmp/hardtrack/OUT_PRZECZYTAJ_MNIE.prg"

mem = bytearray(0x10000)
raw = open(PRG, "rb").read()
load = raw[0] | (raw[1] << 8)
body = raw[2:]
mem[load:load + len(body)] = body
END_HI = load + len(body)

A = X = Y = 0
SP = 0xFD
PC = 0
# flags
C = Z = I = D = B = V = N = 0

def setzn(v):
    global Z, N
    Z = 1 if (v & 0xFF) == 0 else 0
    N = 1 if (v & 0x80) else 0

def push(v):
    global SP
    mem[0x100 + SP] = v & 0xFF
    SP = (SP - 1) & 0xFF

def pull():
    global SP
    SP = (SP + 1) & 0xFF
    return mem[0x100 + SP]

def rd(a): return mem[a & 0xFFFF]
def wr(a, v): mem[a & 0xFFFF] = v & 0xFF

def flags_byte():
    return (N<<7)|(V<<6)|(1<<5)|(B<<4)|(D<<3)|(I<<2)|(Z<<1)|C

def set_flags(p):
    global N,V,B,D,I,Z,C
    N=(p>>7)&1; V=(p>>6)&1; B=(p>>4)&1; D=(p>>3)&1; I=(p>>2)&1; Z=(p>>1)&1; C=p&1

# BASIC SYS 2059 entry — find the SYS target. Stub does the work; start at the SYS addr.
# BASIC line: 0801: link, lineno, 0x9e 'SYS' then "2059" -> PC=2059
PC = 2059

steps = 0
MAXSTEPS = 50_000_000
seen_brk = False

def fetch():
    global PC
    op = mem[PC]; PC = (PC + 1) & 0xFFFF
    return op

def fetch16():
    global PC
    lo = mem[PC]; hi = mem[(PC+1)&0xFFFF]; PC = (PC + 2) & 0xFFFF
    return lo | (hi << 8)

try:
    while steps < MAXSTEPS:
        steps += 1
        op = fetch()
        # --- addressing helpers ---
        if op == 0x00:  # BRK -> treat as program end
            break
        elif op == 0xEA:  # NOP
            pass
        # LDA
        elif op == 0xA9: A = fetch(); setzn(A)
        elif op == 0xA5: A = rd(fetch()); setzn(A)
        elif op == 0xB5: A = rd((fetch()+X)&0xFF); setzn(A)
        elif op == 0xAD: A = rd(fetch16()); setzn(A)
        elif op == 0xBD: A = rd((fetch16()+X)&0xFFFF); setzn(A)
        elif op == 0xB9: A = rd((fetch16()+Y)&0xFFFF); setzn(A)
        elif op == 0xA1:
            z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); A=rd(a); setzn(A)
        elif op == 0xB1:
            z=fetch(); a=(rd(z)|(rd((z+1)&0xFF)<<8)); A=rd((a+Y)&0xFFFF); setzn(A)
        # LDX
        elif op == 0xA2: X = fetch(); setzn(X)
        elif op == 0xA6: X = rd(fetch()); setzn(X)
        elif op == 0xB6: X = rd((fetch()+Y)&0xFF); setzn(X)
        elif op == 0xAE: X = rd(fetch16()); setzn(X)
        elif op == 0xBE: X = rd((fetch16()+Y)&0xFFFF); setzn(X)
        # LDY
        elif op == 0xA0: Y = fetch(); setzn(Y)
        elif op == 0xA4: Y = rd(fetch()); setzn(Y)
        elif op == 0xB4: Y = rd((fetch()+X)&0xFF); setzn(Y)
        elif op == 0xAC: Y = rd(fetch16()); setzn(Y)
        elif op == 0xBC: Y = rd((fetch16()+X)&0xFFFF); setzn(Y)
        # STA
        elif op == 0x85: wr(fetch(), A)
        elif op == 0x95: wr((fetch()+X)&0xFF, A)
        elif op == 0x8D: wr(fetch16(), A)
        elif op == 0x9D: wr((fetch16()+X)&0xFFFF, A)
        elif op == 0x99: wr((fetch16()+Y)&0xFFFF, A)
        elif op == 0x81:
            z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); wr(a, A)
        elif op == 0x91:
            z=fetch(); a=(rd(z)|(rd((z+1)&0xFF)<<8)); wr((a+Y)&0xFFFF, A)
        # STX / STY
        elif op == 0x86: wr(fetch(), X)
        elif op == 0x96: wr((fetch()+Y)&0xFF, X)
        elif op == 0x8E: wr(fetch16(), X)
        elif op == 0x84: wr(fetch(), Y)
        elif op == 0x94: wr((fetch()+X)&0xFF, Y)
        elif op == 0x8C: wr(fetch16(), Y)
        # transfers
        elif op == 0xAA: X = A; setzn(X)
        elif op == 0xA8: Y = A; setzn(Y)
        elif op == 0x8A: A = X; setzn(A)
        elif op == 0x98: A = Y; setzn(A)
        elif op == 0xBA: X = SP; setzn(X)
        elif op == 0x9A: SP = X
        # stack
        elif op == 0x48: push(A)
        elif op == 0x68: A = pull(); setzn(A)
        elif op == 0x08: push(flags_byte() | 0x10)
        elif op == 0x28: set_flags(pull())
        # inc/dec
        elif op == 0xE8: X = (X+1)&0xFF; setzn(X)
        elif op == 0xCA: X = (X-1)&0xFF; setzn(X)
        elif op == 0xC8: Y = (Y+1)&0xFF; setzn(Y)
        elif op == 0x88: Y = (Y-1)&0xFF; setzn(Y)
        elif op == 0xE6: a=fetch(); v=(rd(a)+1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xF6: a=(fetch()+X)&0xFF; v=(rd(a)+1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xEE: a=fetch16(); v=(rd(a)+1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xFE: a=(fetch16()+X)&0xFFFF; v=(rd(a)+1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xC6: a=fetch(); v=(rd(a)-1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xD6: a=(fetch()+X)&0xFF; v=(rd(a)-1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xCE: a=fetch16(); v=(rd(a)-1)&0xFF; wr(a,v); setzn(v)
        elif op == 0xDE: a=(fetch16()+X)&0xFFFF; v=(rd(a)-1)&0xFF; wr(a,v); setzn(v)
        # logic
        elif op in (0x29,0x25,0x35,0x2D,0x3D,0x39,0x21,0x31):
            if op==0x29: m=fetch()
            elif op==0x25: m=rd(fetch())
            elif op==0x35: m=rd((fetch()+X)&0xFF)
            elif op==0x2D: m=rd(fetch16())
            elif op==0x3D: m=rd((fetch16()+X)&0xFFFF)
            elif op==0x39: m=rd((fetch16()+Y)&0xFFFF)
            elif op==0x21: z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd(a)
            else: z=fetch(); a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd((a+Y)&0xFFFF)
            A&=m; setzn(A)
        elif op in (0x09,0x05,0x15,0x0D,0x1D,0x19,0x01,0x11):
            if op==0x09: m=fetch()
            elif op==0x05: m=rd(fetch())
            elif op==0x15: m=rd((fetch()+X)&0xFF)
            elif op==0x0D: m=rd(fetch16())
            elif op==0x1D: m=rd((fetch16()+X)&0xFFFF)
            elif op==0x19: m=rd((fetch16()+Y)&0xFFFF)
            elif op==0x01: z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd(a)
            else: z=fetch(); a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd((a+Y)&0xFFFF)
            A|=m; setzn(A)
        elif op in (0x49,0x45,0x55,0x4D,0x5D,0x59,0x41,0x51):
            if op==0x49: m=fetch()
            elif op==0x45: m=rd(fetch())
            elif op==0x55: m=rd((fetch()+X)&0xFF)
            elif op==0x4D: m=rd(fetch16())
            elif op==0x5D: m=rd((fetch16()+X)&0xFFFF)
            elif op==0x59: m=rd((fetch16()+Y)&0xFFFF)
            elif op==0x41: z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd(a)
            else: z=fetch(); a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd((a+Y)&0xFFFF)
            A^=m; setzn(A)
        # bit
        elif op in (0x24,0x2C):
            m = rd(fetch()) if op==0x24 else rd(fetch16())
            Z = 1 if (A & m)==0 else 0; N=(m>>7)&1; V=(m>>6)&1
        # shifts/rotates on A
        elif op == 0x0A: C=(A>>7)&1; A=(A<<1)&0xFF; setzn(A)
        elif op == 0x4A: C=A&1; A=A>>1; setzn(A)
        elif op == 0x2A: nc=(A>>7)&1; A=((A<<1)|C)&0xFF; C=nc; setzn(A)
        elif op == 0x6A: nc=A&1; A=((A>>1)|(C<<7))&0xFF; C=nc; setzn(A)
        # shifts/rotates on memory
        elif op in (0x06,0x16,0x0E,0x1E,0x46,0x56,0x4E,0x5E,0x26,0x36,0x2E,0x3E,0x66,0x76,0x6E,0x7E):
            if op in (0x06,0x46,0x26,0x66): a=fetch()
            elif op in (0x16,0x56,0x36,0x76): a=(fetch()+X)&0xFF
            elif op in (0x0E,0x4E,0x2E,0x6E): a=fetch16()
            else: a=(fetch16()+X)&0xFFFF
            m=rd(a)
            if op in (0x06,0x16,0x0E,0x1E): C=(m>>7)&1; m=(m<<1)&0xFF
            elif op in (0x46,0x56,0x4E,0x5E): C=m&1; m=m>>1
            elif op in (0x26,0x36,0x2E,0x3E): nc=(m>>7)&1; m=((m<<1)|C)&0xFF; C=nc
            else: nc=m&1; m=((m>>1)|(C<<7))&0xFF; C=nc
            wr(a,m); setzn(m)
        # compares
        elif op in (0xC9,0xC5,0xD5,0xCD,0xDD,0xD9,0xC1,0xD1):
            if op==0xC9: m=fetch()
            elif op==0xC5: m=rd(fetch())
            elif op==0xD5: m=rd((fetch()+X)&0xFF)
            elif op==0xCD: m=rd(fetch16())
            elif op==0xDD: m=rd((fetch16()+X)&0xFFFF)
            elif op==0xD9: m=rd((fetch16()+Y)&0xFFFF)
            elif op==0xC1: z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd(a)
            else: z=fetch(); a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd((a+Y)&0xFFFF)
            t=(A-m)&0x1FF; C=1 if A>=m else 0; setzn(t&0xFF)
        elif op in (0xE0,0xE4,0xEC):
            m = fetch() if op==0xE0 else (rd(fetch()) if op==0xE4 else rd(fetch16()))
            C=1 if X>=m else 0; setzn((X-m)&0xFF)
        elif op in (0xC0,0xC4,0xCC):
            m = fetch() if op==0xC0 else (rd(fetch()) if op==0xC4 else rd(fetch16()))
            C=1 if Y>=m else 0; setzn((Y-m)&0xFF)
        # ADC/SBC (binary mode only)
        elif op in (0x69,0x65,0x75,0x6D,0x7D,0x79,0x61,0x71):
            if op==0x69: m=fetch()
            elif op==0x65: m=rd(fetch())
            elif op==0x75: m=rd((fetch()+X)&0xFF)
            elif op==0x6D: m=rd(fetch16())
            elif op==0x7D: m=rd((fetch16()+X)&0xFFFF)
            elif op==0x79: m=rd((fetch16()+Y)&0xFFFF)
            elif op==0x61: z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd(a)
            else: z=fetch(); a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd((a+Y)&0xFFFF)
            s=A+m+C; V=1 if (~(A^m)&(A^s)&0x80) else 0; C=1 if s>0xFF else 0; A=s&0xFF; setzn(A)
        elif op in (0xE9,0xE5,0xF5,0xED,0xFD,0xF9,0xE1,0xF1):
            if op==0xE9: m=fetch()
            elif op==0xE5: m=rd(fetch())
            elif op==0xF5: m=rd((fetch()+X)&0xFF)
            elif op==0xED: m=rd(fetch16())
            elif op==0xFD: m=rd((fetch16()+X)&0xFFFF)
            elif op==0xF9: m=rd((fetch16()+Y)&0xFFFF)
            elif op==0xE1: z=(fetch()+X)&0xFF; a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd(a)
            else: z=fetch(); a=rd(z)|(rd((z+1)&0xFF)<<8); m=rd((a+Y)&0xFFFF)
            m^=0xFF; s=A+m+C; V=1 if (~(A^m)&(A^s)&0x80) else 0; C=1 if s>0xFF else 0; A=s&0xFF; setzn(A)
        # flag ops
        elif op == 0x18: C=0
        elif op == 0x38: C=1
        elif op == 0x58: I=0
        elif op == 0x78: I=1
        elif op == 0xB8: V=0
        elif op == 0xD8: D=0
        elif op == 0xF8: D=1
        # branches
        elif op in (0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0):
            off = fetch()
            if off >= 0x80: off -= 256
            take = ((op==0x10 and N==0) or (op==0x30 and N==1) or
                    (op==0x50 and V==0) or (op==0x70 and V==1) or
                    (op==0x90 and C==0) or (op==0xB0 and C==1) or
                    (op==0xD0 and Z==0) or (op==0xF0 and Z==1))
            if take: PC = (PC + off) & 0xFFFF
        # jumps
        elif op == 0x4C: PC = fetch16()
        elif op == 0x6C:
            a=fetch16(); lo=rd(a); hi=rd((a&0xFF00)|((a+1)&0xFF)); PC=lo|(hi<<8)
        elif op == 0x20:
            a=fetch16(); ret=(PC-1)&0xFFFF; push((ret>>8)&0xFF); push(ret&0xFF); PC=a
        elif op == 0x60:
            lo=pull(); hi=pull(); PC=((lo|(hi<<8))+1)&0xFFFF
        elif op == 0x40:
            set_flags(pull()); lo=pull(); hi=pull(); PC=lo|(hi<<8)
        else:
            sys.stderr.write(f"UNKNOWN OPCODE {op:02x} at {(PC-1)&0xFFFF:04x} step {steps}\n")
            break
        # Heuristic stop: many crunchers JMP back to BASIC warm start ($A474/$E37B)
        # or hit a tight loop. We detect a JMP into ROM/return-to-basic.
        if PC in (0xA474, 0xE37B, 0xA7AE, 0xFCE2, 0x0000):
            sys.stderr.write(f"reached terminator PC={PC:04x} after {steps} steps\n")
            break
except Exception as e:
    sys.stderr.write(f"halt: {e} at PC={PC:04x} step {steps}\n")

sys.stderr.write(f"ran {steps} steps, final PC={PC:04x}\n")

# Dump candidate text regions. Crunched notes usually decode to $0400 (screen)
# or a buffer; scan all RAM for long PETSCII runs.
def petscii_to_ascii(b):
    # screen codes vs petscii: try petscii first
    out=[]
    for c in b:
        if c==0x0d or c==0x0a: out.append('\n')
        elif 0x20<=c<0x60: out.append(chr(c))
        elif 0x60<=c<0x7b: out.append(chr(c-0x60+0x40))  # rough
        elif 0xc1<=c<=0xda: out.append(chr(c-0x80))
        else: out.append('.')
    return ''.join(out)

# screen RAM
scr = bytes(mem[0x0400:0x07e8])
# convert screen codes to ascii
def scrcode_to_ascii(b):
    out=[]
    for c in b:
        c&=0x7f
        if c==0: out.append('@')
        elif 1<=c<=26: out.append(chr(ord('a')+c-1))
        elif 27<=c<=31: out.append('[\\]^_'[c-27])
        elif c==32: out.append(' ')
        elif 33<=c<=63: out.append(chr(c))
        else: out.append('.')
    return ''.join(out)

print("===== SCREEN RAM ($0400) as screencodes =====")
s = scrcode_to_ascii(scr)
for i in range(0,len(s),40):
    print(s[i:i+40])

print("\n===== LONG PETSCII RUNS across RAM =====")
import re
full = bytes(mem)
for m in re.finditer(rb'[\x20-\x5f\x0d\xc1-\xda]{20,}', full):
    txt = petscii_to_ascii(m.group())
    if sum(c.isalpha() for c in txt) > 12:
        print(f"@{m.start():04x}: {txt[:200]}")
