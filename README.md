Abstract

Assembly-Aware Text Editor is a special text editor that is specifically designed for working with assembly code. It offers syntax-awareness, structure-aware editing, and associated tools that are meant to aid productivity when developing low-level software.

Introduction

Assembly-Aware Text Editor has features like syntax highlighting, assembly-awareness of such things as labels, instructions, and directives, a fast and light weight editor, ability to open/save files, and an easy to use interface. If possible, any mechanism of error detection or validation can be included to increase accuracy.

System Overview

Features

- Syntax highlighting adapted for assembly language
- Assembly-awareness of labels, instructions, and directives
- Fast and light weight performance
- Ability to open and save files
- Error detection/validation (if included)
- Easy to use interface

Project Structure

The following is the standard format of a project directory in the repository:

- src/: source code
- assets/: UI assets (if used)
- main.py or main.cpp: program entry point
- requirements.txt: dependencies (if using Python implementation)
- README.md

Installation

Repository Acquisition

- Clone the repository using the provided link
- Change directory to the project folder

Dependency Installation (if applicable)

- If using Python implementation, install required dependencies: pip install -r requirements.txt

Usage

Launch Editor

- To launch an interpreted implementation of the editor: python main.py
- To launch a compiled version: ./editor

Operation

- Editor breaks assembly code into tokens like instructions, registers, and labels
- Implements syntax highlighting based on the rules applied to the editor
- Keeps track of structure for editing convenience
- Optional instruction/syntax validation capability

Features of the Supported Assembly

- Labels (such as LOOP:)
- Instructions (like MOV, ADD, etc.)
- Registers (like AX, BX, etc.)
- Directives (.data, .text, etc.)

Technologies

- Programming Language: (Python/C++)
- GUI framework: (Tkinter/Qt)
- Tokenization/Parsing: (custom/tokenizer/parser)

Limitations

- Limited support for some assembly languages (e.g. x86)
- Limited debugging capability (if included)
- No full assembler/compilation support

Future Work

- Adding assembler/compiler support
- Implementing debugger
- Instruction auto-complete feature
- Plugin architecture
- Multi-file project support

Author

Sharvesh

License

This project is free and open-source software (FOSS) available under MIT license.
