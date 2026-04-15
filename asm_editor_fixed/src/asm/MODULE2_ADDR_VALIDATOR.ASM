.MODEL SMALL
.CODE
ORG 100h

START:
LOOP_TOP:
    MOV  DX, OFFSET MSG_PROMPT      
    CALL PRINT_STR                  
    MOV  AH, 0Ah                    
    MOV  DX, OFFSET INPUT_BUF       
    INT  21h                        

    MOV  DX, OFFSET CRLF
    CALL PRINT_STR                  

    MOV  SI, OFFSET INPUT_BUF+1     
    XOR  CH, CH                    
    MOV  CL, [SI]                   
    INC  SI                         
    MOV  DI, OFFSET EXPR_BUF        
    JCXZ LOOP_TOP                   

UP_LOOP:
    MOV  AL, [SI]                   
    CMP  AL, 'a'                    
    JB   UC_OK                      
    CMP  AL, 'z'                    
    JA   UC_OK                      
    SUB  AL, 32
                        
UC_OK:
    MOV  [DI], AL                  
    INC  SI
    INC  DI
    LOOP UP_LOOP                    ; Repeat for all characters

    MOV  BYTE PTR [DI], 0           ; Null-terminate EXPR_BUF

    ; -- Check if user typed EXIT --
    MOV  SI, OFFSET EXPR_BUF
    MOV  DI, OFFSET KW_EXIT
    CALL STR_CMP                    ; Compare EXPR_BUF with "EXIT"
    JZ   QUIT                      

    CALL VALIDATE_ADDR             
    JMP  LOOP_TOP                   

QUIT:
    MOV  DX, OFFSET MSG_BYE
    CALL PRINT_STR                  
    MOV  AH, 4Ch
    INT  21h                        



; --- VALIDATE_ADDR -----------------------------------------------------------

VALIDATE_ADDR PROC
        MOV  SI, OFFSET EXPR_BUF
        MOV  AL, [SI]
        CMP  AL, '['
        JNE  NOT_MEM                ; Must start with '[' to be a memory reference

        MOV  DI, SI
    FIND_CLOSE:
        MOV  AL, [DI]
        CMP  AL, 0
        JE   NO_CLOSE               ; Reached end of string without finding ']'
        CMP  AL, ']'
        JE   HAS_CLOSE              ; Found closing bracket
        INC  DI
        JMP  FIND_CLOSE

    NOT_MEM:
        MOV  DX, OFFSET MSG_INVALID ; Not a memory expression
        CALL PRINT_STR
        RET

    NO_CLOSE:
        MOV  DX, OFFSET MSG_INVALID ; Missing closing ']'
        CALL PRINT_STR
        RET

    HAS_CLOSE:
        ; -- Extract content between '[' and ']' into INNER_BUF --
        MOV  SI, OFFSET EXPR_BUF
        INC  SI                     ; Skip opening '['
        MOV  DI, OFFSET INNER_BUF
    COPY_INNER:
        MOV  AL, [SI]
        CMP  AL, ']'
        JE   INNER_DONE             ; Stop at closing ']'
        MOV  [DI], AL
        INC  SI
        INC  DI
        JMP  COPY_INNER
    INNER_DONE:
        MOV  BYTE PTR [DI], 0       ; Null-terminate INNER_BUF
        MOV  SI, OFFSET INNER_BUF   ; SI now points to inner content

        MOV  DI, OFFSET REG_BX
        CALL CHECK_PREFIX           ; Check for "BX"
        JZ   BASE_OK

        MOV  DI, OFFSET REG_BP
        CALL CHECK_PREFIX           ; Check for "BP"
        JZ   BASE_OK

        MOV  DI, OFFSET REG_SI
        CALL CHECK_PREFIX           ; Check for "SI"
        JZ   BASE_OK

        MOV  DI, OFFSET REG_DI
        CALL CHECK_PREFIX           ; Check for "DI"
        JZ   BASE_OK

        ; -- Check if it's a direct numeric address
        MOV  AL, [SI]
        CMP  AL, '0'
        JB   INVALID_BASE           
        CMP  AL, '9'
        JA   INVALID_BASE           
        MOV  DX, OFFSET MSG_DIRECT
        CALL PRINT_STR              
        RET

    INVALID_BASE:
        MOV  DX, OFFSET MSG_INVALID 
        CALL PRINT_STR
        RET

    BASE_OK:
        MOV  DX, OFFSET MSG_DIRECT
        CALL PRINT_STR
        RET    
        
VALIDATE_ADDR ENDP



CHECK_PREFIX PROC
        PUSH SI
        PUSH DI
    CP_LOOP:
        MOV  AL, [DI]
        CMP  AL, 0
        JE   CP_MATCH               ; Reached end of DI string ? full prefix matched
        MOV  BL, [SI]
        CMP  AL, BL
        JNE  CP_MISS                ; Mismatch found
        INC  SI
        INC  DI
        JMP  CP_LOOP
    CP_MATCH:
        POP  DI
        POP  SI
        XOR  AX, AX                 ; AX=0 ? ZF=1 (match)
        RET
    CP_MISS:
        POP  DI
        POP  SI
        OR   AX, 1                  ; AX?0 ? ZF=0 (no match)
        RET
CHECK_PREFIX ENDP




STR_CMP PROC
    SL: MOV  AL, [SI]
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



PRINT_STR PROC

    MOV  AH, 09h                    
    INT  21h                        
    RET                              
 
PRINT_STR ENDP

; --- Data Buffers ------------------
INPUT_BUF   DB 30, 0, 31 DUP(0)    
EXPR_BUF    DB 32 DUP(0)           
INNER_BUF   DB 32 DUP(0)           

; --- Keywords & Register Names ---------------
KW_EXIT     DB 'EXIT', 0           
REG_BX      DB 'BX', 0            
REG_BP      DB 'BP', 0            
REG_SI      DB 'SI', 0            
REG_DI      DB 'DI', 0            

; --- Messages ----------------------
CRLF        DB 0Dh, 0Ah, '$'                         
MSG_PROMPT  DB 0Dh,0Ah,'  Enter  : ','$'             
MSG_DIRECT  DB '  Result: VALID.',0Dh,0Ah,'$'        
MSG_INVALID DB '  Result: INVALID',0Dh,0Ah,'$'       
MSG_BYE     DB 0Dh,0Ah,'Completed !!',0Dh,0Ah,'$'   

END START