import re
from src.asm_keywords import VALID_ADDR_COMBOS

_REG_INSIDE = re.compile(r"\b(BX|BP|SI|DI|AX|CX|DX|SP|AH|AL|BH|BL|CH|CL|DH|DL)\b")
_NUM_ONLY = re.compile(r"^[0-9A-Fa-f]+[Hh]?$|^\d+$")


def validate_operand(operand: str):
    op = operand.strip()
    if not op.startswith("["):
        return False, True, ""
    if not op.endswith("]"):
        return True, False, "Missing closing bracket ']'"
    inner = op[1:-1].strip()
    regs_found = [m.group().upper() for m in _REG_INSIDE.finditer(inner)]
    reg_set = frozenset(regs_found)
    illegal = reg_set - frozenset({"BX", "BP", "SI", "DI"})
    if illegal:
        return True, False, (
            f"Register(s) {', '.join(sorted(illegal))} cannot be used in a memory address – use BX, BP, SI, or DI only"
        )
    if len(regs_found) > 2:
        return True, False, "Too many registers in addressing expression"
    if len(reg_set) > 0 and reg_set not in VALID_ADDR_COMBOS:
        return True, False, f"Invalid base/index combination [{'+'.join(sorted(reg_set))}] – use BX/BP as base and SI/DI as index"
    stripped = _REG_INSIDE.sub("", inner).replace("+", "").replace("-", "").strip()
    if stripped and not _NUM_ONLY.match(stripped):
        return True, False, f"Unrecognised token in address: '{stripped}'"
    return True, True, ""
