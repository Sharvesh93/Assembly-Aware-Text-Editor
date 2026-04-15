import re
from typing import List, Dict
from src.asm_keywords import (
    ALL_MNEMONICS,
    ALL_REGS,
    DIRECTIVES,
    RESERVED,
    MNEMONICS_0OP,
    MNEMONICS_1OP,
    MNEMONICS_2OP,
    MNEMONICS_OPT,
    REGS_8,
    REGS_16,
    REGS_SEG,
)
from src.addr_validator import validate_operand

_LABEL_DEF = re.compile(r"^([A-Za-z_@][A-Za-z0-9_@?]*)\s*:", re.IGNORECASE)
_JUMP_REF = re.compile(
    r"^\s*(?:JMP|JE|JNE|JZ|JNZ|JA|JAE|JB|JBE|JG|JGE|JL|JLE|"
    r"JS|JNS|JO|JNO|JP|JNP|JCXZ|LOOP|LOOPE|LOOPZ|LOOPNE|LOOPNZ|CALL)"
    r"\s+([A-Za-z_@][A-Za-z0-9_@?]*)\s*(?:;.*)?$",
    re.IGNORECASE,
)
_MEM_PAT = re.compile(r"\[.*?\]")
_HEX_NUM = re.compile(r"^[0-9A-Fa-f]+[Hh]$")
_DEC_NUM = re.compile(r"^\d+$")
_BIN_NUM = re.compile(r"^[01]+[Bb]$")


def _is_number(s: str) -> bool:
    s = s.strip()
    return bool(_HEX_NUM.match(s) or _DEC_NUM.match(s) or _BIN_NUM.match(s))


def _split_operands(s: str) -> List[str]:
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "[":
            depth += 1
            cur += ch
        elif ch == "]":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def _err(line: int, sev: str, msg: str) -> Dict:
    return {"line": line, "severity": sev, "message": msg}


class AsmLinter:
    def lint(self, source: str) -> List[Dict]:
        errors: List[Dict] = []
        label_defs: Dict[str, int] = {}
        jump_refs: List[tuple] = []
        lines = source.splitlines()
        for lineno, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or line.startswith(";"):
                continue
            code = line.split(";")[0].strip()
            lm = _LABEL_DEF.match(code)
            if lm:
                lbl = lm.group(1).upper()
                if lbl in label_defs:
                    errors.append(
                        _err(
                            lineno,
                            "error",
                            f"Duplicate label '{lbl}' (first at line {label_defs[lbl]})",
                        )
                    )
                elif lbl in RESERVED:
                    errors.append(_err(lineno, "error", f"'{lbl}' is a reserved word – cannot be used as label"))
                else:
                    label_defs[lbl] = lineno
                code = code[lm.end() :].strip()
            if not code:
                continue
            tokens_upper = [t.upper().lstrip(".") for t in code.split()]
            dir_strip = {d.lstrip(".") for d in DIRECTIVES}
            if any(t in dir_strip for t in tokens_upper):
                continue
            parts = code.split(None, 1)
            mnemonic = parts[0].upper()
            op_str = parts[1].strip() if len(parts) > 1 else ""
            operands = _split_operands(op_str) if op_str else []
            n = len(operands)
            if mnemonic not in ALL_MNEMONICS:
                errors.append(_err(lineno, "error", f"Unknown mnemonic '{parts[0]}'"))
                continue
            if mnemonic in MNEMONICS_0OP and n > 0:
                errors.append(_err(lineno, "warning", f"'{mnemonic}' takes no operands ({n} given)"))
            elif mnemonic in MNEMONICS_1OP:
                if n == 0:
                    errors.append(_err(lineno, "error", f"'{mnemonic}' requires 1 operand"))
                elif n > 1:
                    errors.append(_err(lineno, "warning", f"'{mnemonic}' takes 1 operand ({n} given)"))
            elif mnemonic in MNEMONICS_2OP:
                if n < 2:
                    errors.append(_err(lineno, "error", f"'{mnemonic}' requires 2 operands ({n} given)"))
                elif n > 2:
                    errors.append(_err(lineno, "warning", f"'{mnemonic}' takes 2 operands ({n} given)"))
            if mnemonic == "MOV" and n == 2:
                dst = operands[0].strip().upper()
                src = operands[1].strip().upper()
                if _MEM_PAT.search(dst) and _MEM_PAT.search(src):
                    errors.append(_err(lineno, "error", "MOV: both operands cannot be memory – use a register as intermediate"))
                if dst == "CS":
                    errors.append(_err(lineno, "error", "MOV: CS cannot be a destination register"))
                if dst in REGS_SEG and (_is_number(src) or src.startswith("0")):
                    errors.append(
                        _err(
                            lineno,
                            "error",
                            f"MOV: cannot move immediate into segment register {dst} – load into AX/BX first, then move",
                        )
                    )
                if dst in REGS_8 and src in REGS_16:
                    errors.append(_err(lineno, "error", f"MOV: size mismatch – 8-bit dst '{dst}' ← 16-bit src '{src}'"))
                if dst in REGS_16 and src in REGS_8:
                    errors.append(_err(lineno, "error", f"MOV: size mismatch – 16-bit dst '{dst}' ← 8-bit src '{src}'"))
            for op in operands:
                is_mem, is_valid, msg = validate_operand(op)
                if is_mem and not is_valid:
                    errors.append(_err(lineno, "error", f"Addressing mode error in '{op}': {msg}"))
            jm = _JUMP_REF.match(line)
            if jm:
                tgt = jm.group(1).upper()
                if tgt not in ALL_REGS:
                    jump_refs.append((tgt, lineno))
        for tgt, lineno in jump_refs:
            if tgt not in label_defs:
                errors.append(_err(lineno, "warning", f"Undefined label '{tgt}' used as jump/call target"))
        return sorted(errors, key=lambda e: e["line"])
