"""@file interpret.py

Interpret XML reprezentace kódu
"""

import re
import argparse
from sys import stderr
import xml.etree.ElementTree as ET

# stderr.write("example of stderr\n")
# exit(0)
temporary_frame = []
local_frame = []
global_frame = []

class Argument:
    def __init__(self, number, arg_type, value):
        self.number = number
        self.arg_type = arg_type
        self.value = value

    def get_argument(self):
        print(self.number, self.arg_type, self.value)

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

        
class Variable:

    def __init__(self, frame, var_type, name, value):
        self.frame = frame
        self.var_type = var_type
        self.name = name
        self.value = value

    
    def add_global_frame(self):
        self.global_frame.append(self)

    def get_variable(self):
        print(self.frame, self.var_type, self.name, self.value)

    def get_variable_name(self):
        return self.name
    
    def update_variable(self, var_type, value):
        self.var_type = var_type
        self.value = value


class Defvar(Instruction):
    def __init__(self, number):
        super().__init__("DEFVAR", number)

    def check_instr(self):
        if (len(self.args) > 1):
            stderr.write("wrong argument\n")
            exit(52)

        if (self.args[0].arg_type != "var"):
            stderr.write("wrong argument arg_type\n")
            exit(52)
            
    def execute(self):
        value = self.args[0].value.split("@")
        var = Variable(value[0], self.args[0].arg_type, value[1], "")

        # check if exist and save variable
        if(value[0] == "GF"):
            if(value[1] in global_frame):
                stderr.write("variable already declared\n")
                exit(52) 
            else:
                global_frame.append(var)
        elif(value[0] == "LF"):
            if(value[1] in local_frame):
                stderr.write("variable already declared\n")
                exit(52)
            else:
                local_frame.append(var)
        elif(value[0] == "TF"):
            if(value[1] in temporary_frame):
                stderr.write("variable already declared\n")
                exit(52)
            else:
                temporary_frame.append(var)
        else:
            exit(52)

        

class Move(Instruction):
    def __init__(self, number):
        super().__init__("MOVE", number)

    def check_instr(self):
        pass
    
    def execute(self):
        value = self.args[0].value.split("@")
        if value[0] == "GF":
            for variable in global_frame:
                if variable.get_variable_name() == value[1]:
                    variable.update_variable(self.args[1].arg_type, self.args[1].value)      
        if value[0] == "LF":
            for variable in local_frame:
                if variable.get_variable_name() == value[1]:
                    variable.update_variable(self.args[1].arg_type, self.args[1].value)      
        if value[0] == "TF":
            for variable in local_frame:
                if variable.get_variable_name() == value[1]:
                    variable.update_variable(self.args[1].arg_type, self.args[1].value)      

class Add(Instruction):
    def __init__(self, number):
        super().__init__("ADD", number)

    def check_instr(self):
        print("syntax analyzator")

    
    def execute(self):
        pass

    
class Sub(Instruction):
    def __init__(self, number):
        super().__init__("SUB", number)

    def check_instr(self):
        print("syntax analyzator")
    
    def execute(self):
        pass
class Write(Instruction):
    def __init__(self, number):
        super().__init__("WRITE", number)

    def check_instr(self):
        print("syntax analyzator")
    
    def execute(self):
        pass

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

    if child.attrib["opcode"].upper() == "DEFVAR":
        # print(instr_arg.tag, instr_arg.attrib, child.find(instr_arg.tag).text)
        print("___DEFVAR")
        instructions.append(Defvar(1))
        # instructions[int(child.attrib["order"])-1].get_arguments()
    elif child.attrib["opcode"].upper() == "MOVE":
        print("___MOVE")
        instructions.append(Move(2))
        # instructions[int(child.attrib["order"])-1].get_arguments()

    elif child.attrib["opcode"].upper() == "ADD":
        print("___Add")
        instructions.append(Add(3))
        # instructions[int(child.attrib["order"])-1].get_arguments()
    elif child.attrib["opcode"].upper() == "SUB":
        print("___Sub")
        instructions.append(Sub(3))
        # instructions[int(child.attrib["order"])-1].get_arguments()
    elif child.attrib["opcode"].upper() == "WRITE":
        print("___Write")
        instructions.append(Write(1))
        # instructions[int(child.attrib["order"])-1].get_arguments()
    else:
        stderr.write("wrong opcode\n")
        exit(53)

    # iter trough child
    for instr_arg in child:
        # print(child.attrib["opcode"], child.attrib["order"], instr_arg.tag, instr_arg.attrib)
        if not ('order' in child.attrib) or not ('opcode' in child.attrib):
            exit(52)

        if not(re.match(r"arg[123]", instr_arg.tag)):
            exit(52)


        # add arguments to instruction        
        instructions[int(child.attrib["order"])-1].add_argument(int(instr_arg.tag[3:]), instr_arg.attrib['type'], child.find(instr_arg.tag).text)

# interpret
for instr in instructions:
    print("______instruction")
    print(type(instr))
    instr.check_instr()
    instr.execute()
# print("-------------------")
# print(global_frame[1].get_variable())

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

