MNEMONICS_0OP = frozenset(
    {
        "NOP",
        "HLT",
        "IRET",
        "RET",
        "RETF",
        "CLC",
        "STC",
        "CMC",
        "CLD",
        "STD",
        "CLI",
        "STI",
        "PUSHF",
        "POPF",
        "CBW",
        "CWD",
        "AAA",
        "AAD",
        "AAM",
        "AAS",
        "DAA",
        "DAS",
        "MOVSB",
        "MOVSW",
        "CMPSB",
        "CMPSW",
        "SCASB",
        "SCASW",
        "LODSB",
        "LODSW",
        "STOSB",
        "STOSW",
        "XLAT",
    }
)

MNEMONICS_1OP = frozenset(
    {
        "PUSH",
        "POP",
        "INC",
        "DEC",
        "NOT",
        "NEG",
        "MUL",
        "DIV",
        "IMUL",
        "IDIV",
        "CALL",
        "JMP",
        "JE",
        "JNE",
        "JZ",
        "JNZ",
        "JA",
        "JAE",
        "JB",
        "JBE",
        "JG",
        "JGE",
        "JL",
        "JLE",
        "JS",
        "JNS",
        "JO",
        "JNO",
        "JP",
        "JNP",
        "JCXZ",
        "LOOP",
        "LOOPE",
        "LOOPZ",
        "LOOPNE",
        "LOOPNZ",
        "INT",
    }
)

MNEMONICS_2OP = frozenset(
    {
        "MOV",
        "ADD",
        "SUB",
        "AND",
        "OR",
        "XOR",
        "CMP",
        "TEST",
        "LEA",
        "LDS",
        "LES",
        "XCHG",
        "SHL",
        "SHR",
        "SAL",
        "SAR",
        "ROL",
        "ROR",
        "RCL",
        "RCR",
        "IN",
        "OUT",
        "BOUND",
    }
)

MNEMONICS_OPT = frozenset(
    {
        "REP",
        "REPE",
        "REPZ",
        "REPNE",
        "REPNZ",
        "MOVS",
        "CMPS",
        "SCAS",
        "LODS",
        "STOS",
        "INTO",
        "LOCK",
        "WAIT",
    }
)

ALL_MNEMONICS = MNEMONICS_0OP | MNEMONICS_1OP | MNEMONICS_2OP | MNEMONICS_OPT

REGS_16 = frozenset({"AX", "BX", "CX", "DX", "SP", "BP", "SI", "DI", "IP"})
REGS_8 = frozenset({"AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL"})
REGS_SEG = frozenset({"CS", "DS", "SS", "ES"})
ALL_REGS = REGS_16 | REGS_8 | REGS_SEG

DIRECTIVES = frozenset(
    {
        "SEGMENT",
        "ENDS",
        "PROC",
        "ENDP",
        "DB",
        "DW",
        "DD",
        "DQ",
        "DT",
        "EQU",
        "ASSUME",
        "END",
        ".MODEL",
        "MODEL",
        ".CODE",
        "CODE",
        ".DATA",
        "DATA",
        ".STACK",
        "STACK",
        ".CONST",
        "CONST",
        "SMALL",
        "LARGE",
        "MEDIUM",
        "TINY",
        "HUGE",
        "NEAR",
        "FAR",
        "ORG",
        "OFFSET",
        "PTR",
        "BYTE",
        "WORD",
        "DWORD",
        "LABEL",
        "NAME",
        "INCLUDE",
        "EXTRN",
        "PUBLIC",
        "@DATA",
        "EVEN",
        "ALIGN",
    }
)

VALID_ADDR_COMBOS = frozenset(
    {
        frozenset({"BX"}),
        frozenset({"BP"}),
        frozenset({"SI"}),
        frozenset({"DI"}),
        frozenset({"BX", "SI"}),
        frozenset({"BX", "DI"}),
        frozenset({"BP", "SI"}),
        frozenset({"BP", "DI"}),
    }
)

RESERVED = ALL_MNEMONICS | ALL_REGS | DIRECTIVES


def classify(token: str) -> str:
    t = token.strip().upper()
    if t in ALL_MNEMONICS:
        return "mnemonic"
    if t in ALL_REGS:
        return "register"
    if t in DIRECTIVES:
        return "directive"
    return "unknown"
