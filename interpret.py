"""@file interpret.py

Interpret XML reprezentace kódu
"""

import re
import argparse
from sys import stderr
import xml.etree.ElementTree as ET

# stderr.write("example of stderr\n")
# exit(0)

class Argument:
    def __init__(self, number, arg_type, value):
        self.number = number
        self.type = arg_type
        self.value = value

    def get_argument(self):
        print(self.number, self.type, self.value)

class Instruction:
    def __init__(self, name, number):
        self.name = name
        self.numberOfArg = number
        self.args = []

    def add_argument(self, number, arg_type, value):
        self.args.append(Argument(number, arg_type, value))

    def get_arguments(self):
        print("ARGUMENTS: ")
        for arg in self.args:
            arg.get_argument()

# class Variable:
#     temporary_frame = []
#     local_frame = []
#     global_frame = []

#     def __init__(self, frame, var_type, value):
#         self.frame = frame
#         self.type = var_type
#         self.value = value

#     def add_global_frame(self):
#         self.global_frame.append(self)


class Defvar(Instruction):
    def __init__(self, number):
        super().__init__("DEFVAR", number)

    def execute(self):
        print("DEFVAR" )

class Move(Instruction):
    def __init__(self, number, str_arg):
        super().__init__("MOVE", number, str_arg)


''' list of instruction '''
instructions = []

# parsovanie argumentov - argparse kniznica
parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, nargs=1, help="Usage: ")
parser.add_argument("--input", type=str, nargs=1, help="Usage: ")

args = parser.parse_args()
input_file = args.input
source_file = args.source[0]

if source_file is None:
    # read from stdin
    pass

# load xml - xml ElementTree
# sort, prečítať, uložiť lable
''' reading from file '''
tree = ET.parse(source_file) # add input

root = tree.getroot()


'''check xml''' 
# missing root tag
if root.tag != 'program':
    stderr.write("mising root tag\n")
    exit(52) 

for child in root:
    if child.tag != 'instruction':
        stderr.write("missing instruction\n")
        exit(52)

    # child_arguments = list(child.attrib.keys)
    # print("arguments", child.attrib.keys)
    for instr_arg in child:
        # print(child.attrib["opcode"], child.attrib["order"], instr_arg.tag, instr_arg.attrib)
        if not ('order' in child.attrib) or not ('opcode' in child.attrib):
            exit(52)

        if not(re.match(r"arg[123]", instr_arg.tag)):
            exit(52)

        if child.attrib["opcode"].upper() == "DEFVAR":
            # print(instr_arg.tag, instr_arg.attrib, child.find(instr_arg.tag).text)
            instructions.append(Defvar(1))
            instructions[int(child.attrib["order"])-1].add_argument(int(instr_arg.tag[3:]), instr_arg.attrib['type'], child.find(instr_arg.tag).text)
            instructions[int(child.attrib["order"])-1].get_arguments()
        elif child.attrib["opcode"].upper() == "MOVE":
            print(instr_arg.tag, instr_arg.attrib)
        elif child.attrib["opcode"].upper() == "ADD":
            print(instr_arg.tag, instr_arg.attrib)
        elif child.attrib["opcode"].upper() == "SUB":
            print(instr_arg.tag, instr_arg.attrib)
        elif child.attrib["opcode"].upper() == "WRITE":
            print(instr_arg.tag, instr_arg.attrib)
        else:
            stderr.write("wrong opcode\n")
            exit(53)
        

# # check childs
# for child in root:
#     if child.tag != 'instrukce':
#         exit(1)
#     child_arguments = list(child.attrib.keys)
#     if not('order' in child_arguments) or not ('opcode' in child_arguments):
#         exit(1)
#     for subelem in child:
#         # kontrola, regex
#         if not(re.match(r"arg[123]", subelem.tag)):
#             exit(1)

# # xml to instruction
# for e in root:
#     # class, global var na generovanie instrukcie
#     for subelem in e:
#         instruction.add_argument(arg_type, value)

# for i in instructions:
#     interpret(i)

# # interpret

# # f.close()
