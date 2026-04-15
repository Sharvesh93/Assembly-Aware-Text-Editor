.MODEL SMALL
.CODE
ORG 100h

MAIN_LOOP:
    MOV  DX, OFFSET MSG_PROMPT
    CALL PRINT_STR

    MOV  AH, 0Ah
    MOV  DX, OFFSET INPUT_BUF
    INT  21h

    MOV  DX, OFFSET CRLF
    CALL PRINT_STR

    MOV  SI, OFFSET INPUT_BUF + 1
    XOR  CH, CH
    MOV  CL, [SI]
    INC  SI

    MOV  DI, OFFSET WORD_BUF
    MOV  [WORD_LEN], CL

    JCXZ MAIN_LOOP

TOUPPER_LOOP:
    MOV  AL, [SI]
    CMP  AL, 61h
    JB   STORE_C
    CMP  AL, 7Ah
    JA   STORE_C
    SUB  AL, 20h

STORE_C:
    MOV  [DI], AL
    INC  SI
    INC  DI
    LOOP TOUPPER_LOOP

    MOV  BYTE PTR [DI], 0

    ; Check for EXIT
    MOV  SI, OFFSET WORD_BUF
    MOV  DI, OFFSET KW_EXIT
    CALL STR_CMP
    JZ   END_PROGRAM

    CALL CLASSIFY_WORD
    JMP  MAIN_LOOP

END_PROGRAM:
    MOV  DX, OFFSET MSG_BYE
    CALL PRINT_STR
    MOV  AH, 4Ch
    INT  21h

;======================================================================
CLASSIFY_WORD PROC
    MOV  SI, OFFSET MNEMONIC_TABLE
    CALL SEARCH_TABLE
    JZ   IS_MNE

    MOV  SI, OFFSET REGISTER_TABLE
    CALL SEARCH_TABLE
    JZ   IS_REG

    MOV  SI, OFFSET DIRECTIVE_TABLE
    CALL SEARCH_TABLE
    JZ   IS_DIR

    ; Unknown
    MOV  DX, OFFSET MSG_UNKNOWN
    CALL PRINT_STR
    MOV  DX, OFFSET WORD_BUF
    CALL PRINT_STR
    MOV  DX, OFFSET TAIL_UNK
    CALL PRINT_STR
    RET

IS_MNE:
    MOV  DX, OFFSET MSG_MNEMONIC
    CALL PRINT_STR
    MOV  DX, OFFSET WORD_BUF
    CALL PRINT_STR
    MOV  DX, OFFSET TAIL_MNE
    CALL PRINT_STR
    RET

IS_REG:
    MOV  DX, OFFSET MSG_REGISTER
    CALL PRINT_STR
    MOV  DX, OFFSET WORD_BUF
    CALL PRINT_STR
    MOV  DX, OFFSET TAIL_REG
    CALL PRINT_STR
    RET

IS_DIR:
    MOV  DX, OFFSET MSG_DIRECTIVE
    CALL PRINT_STR
    MOV  DX, OFFSET WORD_BUF
    CALL PRINT_STR
    MOV  DX, OFFSET TAIL_DIR
    CALL PRINT_STR
    RET
CLASSIFY_WORD ENDP

;======================================================================
SEARCH_TABLE PROC
NXT:
    MOV  AL, [SI]
    CMP  AL, 0FFh
    JE   NOT_FND

    XOR  CH, CH
    MOV  CL, AL
    CMP  CL, [WORD_LEN]
    JNE  SKIP

    INC  SI
    MOV  DI, OFFSET WORD_BUF
    PUSH CX
    PUSH SI

CMP_CH:
    MOV  AL, [SI]
    CMP  AL, [DI]
    JNE  MISM
    INC  SI
    INC  DI
    LOOP CMP_CH

    POP  SI
    POP  CX
    XOR  AX, AX
    RET

MISM:
    POP  SI
    POP  CX
    DEC  SI

SKIP:
    XOR  CH, CH
    MOV  CL, [SI]
    INC  CX
    ADD  SI, CX
    JMP  NXT

NOT_FND:
    OR   AX, 1
    RET
SEARCH_TABLE ENDP

;======================================================================
STR_CMP PROC
SL:
    MOV  AL, [SI]
    MOV  BL, [DI]
    CMP  AL, BL
    JNE  SN
    CMP  AL, 0
    JE   SE
    INC  SI
    INC  DI
    JMP  SL
SE:
    XOR  AX, AX
    RET
SN:
    OR   AX, 1
    RET
STR_CMP ENDP

;======================================================================
PRINT_STR PROC
    MOV  AH, 09h
    INT  21h
    RET
PRINT_STR ENDP

;======================================================================
; Data
INPUT_BUF   DB  20, 0, 21 DUP(0)
WORD_BUF    DB  21 DUP(0)
WORD_LEN    DB  0

KW_EXIT     DB  'EXIT', 0

MSG_PROMPT  DB  0Dh,0Ah,'  Input   : ','$'
CRLF        DB  0Dh,0Ah,'$'

MSG_MNEMONIC  DB '  Result  : [MNEMONIC]  --> ','$'
MSG_REGISTER  DB '  Result  : [REGISTER]  --> ','$'
MSG_DIRECTIVE DB '  Result  : [DIRECTIVE] --> ','$'
MSG_UNKNOWN   DB '  Result  : [UNKNOWN]   --> ','$'

TAIL_MNE    DB ' is a valid 8086 instruction opcode.',0Dh,0Ah,'$'
TAIL_REG    DB ' is a valid 8086 register name.',0Dh,0Ah,'$'
TAIL_DIR    DB ' is a valid assembler directive.',0Dh,0Ah,'$'
TAIL_UNK    DB ' is NOT a recognised 8086 keyword.',0Dh,0Ah,'$'

MSG_BYE     DB  0Dh,0Ah,' Process_Finished',0Dh,0Ah,'$'

;======================================================================
; Tables (compact, no dumping)
MNEMONIC_TABLE:
    DB 3,'MOV', 4,'PUSH',3,'POP', 3,'ADD',3,'SUB',3,'MUL',3,'DIV'
    DB 4,'IDIV',4,'IMUL',3,'AND',2,'OR', 3,'XOR',3,'NOT',3,'NEG'
    DB 3,'CMP',4,'TEST',3,'JMP',2,'JE', 3,'JNE',2,'JZ', 3,'JNZ'
    DB 2,'JA', 3,'JAE',2,'JB', 3,'JBE',2,'JG', 3,'JGE',2,'JL',3,'JLE'
    DB 2,'JS', 3,'JNS',2,'JO', 3,'JNO',4,'JCXZ',4,'CALL',3,'RET'
    DB 4,'RETF',4,'LOOP',5,'LOOPE',5,'LOOPZ',6,'LOOPNE',6,'LOOPNZ'
    DB 3,'NOP',3,'HLT',3,'INT',4,'INTO',4,'IRET',2,'IN',3,'OUT'
    DB 3,'LEA',3,'LDS',3,'LES',4,'XCHG',4,'XLAT',3,'CBW',3,'CWD'
    DB 3,'SHL',3,'SHR',3,'SAL',3,'SAR',3,'ROL',3,'ROR',3,'RCL',3,'RCR'
    DB 4,'MOVS',5,'MOVSB',5,'MOVSW',4,'CMPS',5,'CMPSB',5,'CMPSW'
    DB 4,'SCAS',5,'SCASB',5,'SCASW',4,'LODS',5,'LODSB',5,'LODSW'
    DB 4,'STOS',5,'STOSB',5,'STOSW',3,'REP',4,'REPE',4,'REPZ'
    DB 5,'REPNE',5,'REPNZ',3,'STC',3,'CLC',3,'CMC',3,'STD',3,'CLD'
    DB 3,'STI',3,'CLI',5,'PUSHF',4,'POPF',3,'AAA',3,'AAD',3,'AAM'
    DB 3,'AAS',3,'DAA',3,'DAS',5,'BOUND'
    DB 0FFh

REGISTER_TABLE:
    DB 2,'AX',2,'BX',2,'CX',2,'DX',2,'AH',2,'AL',2,'BH',2,'BL'
    DB 2,'CH',2,'CL',2,'DH',2,'DL',2,'SP',2,'BP',2,'SI',2,'DI'
    DB 2,'IP',2,'CS',2,'DS',2,'SS',2,'ES'
    DB 0FFh

DIRECTIVE_TABLE:
    DB 7,'SEGMENT',4,'ENDS',4,'PROC',4,'ENDP',2,'DB',2,'DW',2,'DD'
    DB 3,'EQU',6,'ASSUME',3,'END',5,'MODEL',5,'SMALL',5,'LARGE'
    DB 6,'MEDIUM',4,'CODE',4,'DATA',5,'STACK',4,'NEAR',3,'FAR'
    DB 3,'ORG',6,'OFFSET',3,'PTR',4,'BYTE',4,'WORD',5,'DWORD'
    DB 5,'LABEL'
    DB 0FFh

END MAIN_LOOP