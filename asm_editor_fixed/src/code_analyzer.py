"""
Code Analysis Module
Provides real-time analysis of assembly code including:
- Instruction statistics and frequency
- Label definitions and references
- Register usage tracking
- Memory segment analysis
- Code size estimation
"""

import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple
from src.asm_keywords import (
    ALL_MNEMONICS,
    ALL_REGS,
    MNEMONICS_0OP,
    MNEMONICS_1OP,
    MNEMONICS_2OP,
    MNEMONICS_OPT,
    REGS_8,
    REGS_16,
    REGS_SEG,
)


class CodeAnalyzer:
    """Analyzes assembly code for statistics and insights"""

    _LABEL_DEF = re.compile(r"^([A-Za-z_@][A-Za-z0-9_@?]*)\s*:", re.IGNORECASE)
    _JUMP_REF = re.compile(
        r"^\s*(?:JMP|JE|JNE|JZ|JNZ|JA|JAE|JB|JBE|JG|JGE|JL|JLE|"
        r"JS|JNS|JO|JNO|JP|JNP|JCXZ|LOOP|LOOPE|LOOPZ|LOOPNE|LOOPNZ|CALL)"
        r"\s+([A-Za-z_@][A-Za-z0-9_@?]*)\s*(?:;.*)?$",
        re.IGNORECASE,
    )

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset analysis state"""
        self.instructions = Counter()  # instruction -> count
        self.registers = Counter()  # register -> count
        self.labels_defined = {}  # label_name -> line_number
        self.labels_referenced = defaultdict(list)  # label_name -> [line_numbers]
        self.directives = Counter()  # directive -> count
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0
        self.data_segment_size = 0
        self.jump_targets = {}  # label -> count of references

    def analyze(self, source: str) -> Dict:
        """
        Analyze assembly code and return statistics
        
        Args:
            source: Assembly source code as string
            
        Returns:
            Dictionary with analysis results
        """
        self.reset()
        lines = source.splitlines()
        self.total_lines = len(lines)

        for lineno, raw in enumerate(lines, 1):
            # Count comment lines
            if raw.strip().startswith(";"):
                self.comment_lines += 1
                continue

            line = raw.strip()
            if not line:
                continue

            self.code_lines += 1

            # Extract code part (before comment)
            code = line.split(";")[0].strip()

            # Check for label definition
            label_match = self._LABEL_DEF.match(code)
            if label_match:
                label_name = label_match.group(1).upper()
                self.labels_defined[label_name] = lineno
                # Remove label from code for further processing
                code = code[label_match.end():].strip()

            # Check for jump references
            jump_match = self._JUMP_REF.match(line)
            if jump_match:
                target = jump_match.group(1).upper()
                self.labels_referenced[target].append(lineno)
                self.jump_targets[target] = self.jump_targets.get(target, 0) + 1

            # Extract mnemonic (first word)
            parts = code.split()
            if not parts:
                continue

            mnemonic = parts[0].upper()

            # Categorize instruction or directive
            if mnemonic.startswith("."):
                self.directives[mnemonic] += 1
                # Estimate data segment size for .byte, .word, .dword
                if mnemonic == ".BYTE":
                    self.data_segment_size += 1
                elif mnemonic == ".WORD":
                    self.data_segment_size += 2
                elif mnemonic == ".DWORD":
                    self.data_segment_size += 4
            elif mnemonic in ALL_MNEMONICS:
                self.instructions[mnemonic] += 1

            # Track register usage
            self._extract_registers(code)

        return self._generate_report()

    def _extract_registers(self, code: str):
        """Extract and count register usage from code line"""
        # Look for register names in the code
        words = re.split(r"[\s,\[\]()]+", code.upper())
        for word in words:
            if word in ALL_REGS:
                self.registers[word] += 1

    def _generate_report(self) -> Dict:
        """Generate analysis report"""
        return {
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.total_lines - self.code_lines - self.comment_lines,
            "total_instructions": sum(self.instructions.values()),
            "unique_instructions": len(self.instructions),
            "top_instructions": self.instructions.most_common(5),
            "total_directives": sum(self.directives.values()),
            "directives": dict(self.directives),
            "total_registers": sum(self.registers.values()),
            "unique_registers": len(self.registers),
            "register_usage": self.registers.most_common(8),
            "labels_defined": len(self.labels_defined),
            "label_list": self.labels_defined,
            "unreferenced_labels": self._find_unreferenced_labels(),
            "undefined_jumps": self._find_undefined_jumps(),
            "data_segment_size": self.data_segment_size,
            "estimated_code_size": self._estimate_code_size(),
        }

    def _find_unreferenced_labels(self) -> List[str]:
        """Find labels that are defined but never referenced"""
        unreferenced = []
        for label in self.labels_defined:
            if label not in self.labels_referenced:
                unreferenced.append(label)
        return unreferenced

    def _find_undefined_jumps(self) -> List[str]:
        """Find jump targets that are not defined"""
        undefined = []
        for label in self.labels_referenced:
            if label not in self.labels_defined:
                undefined.append(label)
        return undefined

    def _estimate_code_size(self) -> int:
        """
        Rough estimate of code size in bytes
        Based on typical instruction sizes for 8086 assembly
        """
        size = 0
        # Average instruction size estimation
        instr_count = sum(self.instructions.values())
        
        # Most instructions are 2-4 bytes, some are longer
        if instr_count > 0:
            # Conservative estimate: 3 bytes average
            size = instr_count * 3
        
        return size

    def get_summary(self) -> str:
        """Get human-readable summary of analysis"""
        report = self.analyze("")  # Will be called with fresh source
        
        lines = [
            "═══ CODE STATISTICS ═══",
            f"Total Lines: {self.total_lines}",
            f"Code Lines: {self.code_lines}",
            f"Comments: {self.comment_lines}",
            "",
            "═══ INSTRUCTIONS ═══",
            f"Total: {report['total_instructions']}",
            f"Unique: {report['unique_instructions']}",
        ]
        
        if report['top_instructions']:
            lines.append("\nMost Used:")
            for instr, count in report['top_instructions'][:3]:
                lines.append(f"  {instr}: {count}x")
        
        lines.extend([
            "",
            "═══ LABELS ═══",
            f"Defined: {report['labels_defined']}",
        ])
        
        if report['unreferenced_labels']:
            lines.append(f"Unused: {len(report['unreferenced_labels'])}")
        
        if report['undefined_jumps']:
            lines.append(f"Undefined: {len(report['undefined_jumps'])}")
        
        lines.extend([
            "",
            "═══ REGISTERS ═══",
            f"Used: {report['unique_registers']}",
        ])
        
        if report['register_usage']:
            lines.append("Top Used:")
            for reg, count in report['register_usage'][:3]:
                lines.append(f"  {reg}: {count}x")
        
        return "\n".join(lines)
