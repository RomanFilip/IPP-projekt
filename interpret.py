"""@file interpret.py

Interpret XML reprezentace kódu
"""

import re
import argparse
from sys import stderr
import sys
import xml.etree.ElementTree as ET

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

    def find_var(self, position):
        value = self.args[position].value.split("@")
        if value[0] == "GF":
            for variable in global_frame:
                if variable.get_variable_name() == value[1]:
                    return variable
            return -1
        elif value[0] == "LF":
            for variable in global_frame:
                if variable.get_variable_name() == value[1]:
                    return variable
            return -1
        elif value[0] == "TF":
            for variable in global_frame:
                if variable.get_variable_name() == value[1]:
                    return variable
            return -1
        else:
            stderr.write("frame not found\n")
            exit(52)
        
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

    def get_variable_type(self):
        return self.var_type

    def get_variable_name(self):
        return self.name
    
    def get_variable_value(self):
        return self.value
    
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
            stderr.write("frame not found\n")
            exit(52)

        
class Move(Instruction):
    def __init__(self, number):
        super().__init__("MOVE", number)

    def check_instr(self):
        pass
    
    def execute(self):
        var = self.find_var(0)  
        if var == -1: exit(56)         
        var.update_variable(self.args[1].arg_type, self.args[1].value)      

class ArithmeticOperations(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def check_instr(self):
        if (len(self.args) > 3):
            exit(52)

    def execute(self):
        if self.args[1].arg_type == "int":
            symb1 = self.args[1].value
        elif self.args[1].arg_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb1 = var.get_variable_value()
        else:
            exit(53)
        if not(re.match(r"^[-0-9]+$", symb1)):
            exit(32)

        if self.args[2].arg_type == "int":
            symb2 = self.args[2].value
        elif self.args[2].arg_type == "var":
            var = self.find_var(2)
            if var == -1: exit(56)
            symb2 = var.get_variable_value()
        else:
            exit(53)
        if not(re.match(r"^[-0-9]+$", symb2)):
            exit(32)

        if self.name == "ADD":
            result = int(symb1) + int(symb2)
        elif self.name == "SUB":
            result = int(symb1) - int(symb2)
        elif self.name == "MUL":
            result = int(symb1) * int(symb2)
        elif self.name == "IDIV":
            if int(symb2) == 0:
                exit(57)
            result = int(symb1) // int(symb2)

        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable("int", result)

class RelationalOperators(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def check_instr(self):
        if (len(self.args) > 3):
            exit(52)

    def execute(self):
        # get type of symbol adn value
        if self.args[1].arg_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb1_type = var.get_variable_type()
            symb1 = var.get_variable_value()
        else:
            symb1_type = self.args[1].arg_type
            symb1 = self.args[1].value

        # check supported types
        if not(re.match(r"int|bool|string", symb1_type)):
            exit(53)

        # get type of symbol and value
        if self.args[2].arg_type == "var":
            var = self.find_var(2)
            if var == -1: exit(56)
            symb2 = var.get_variable_value()
            symb2_type = var.get_variable_type()
        else:
            symb2 = self.args[2].value
            symb2_type = self.args[2].arg_type

        # check type compatibility
        if symb1_type != symb2_type:
            exit(53)

        if self.name == "LT":
            result = symb1 < symb2
        if self.name == "GT":
            result = symb1 > symb2
        if self.name == "EQ":
            result = symb1 == symb2
        
        # save result
        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable('bool', result)
class BooleanOperators(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def check_instr(self):
        if (len(self.args) > 3):
            exit(52)

    def execute(self):
        # get type of symbol adn value
        symb1_type = self.args[1].arg_type
        if  symb1_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb1_type = var.get_variable_type()
            symb1 = var.get_variable_value()
        
        if symb1_type == "bool":
            symb1 = self.args[1].value
        else: 
            exit(53)
        
        symb2_type = self.args[2].arg_type
        if  symb2_type == "var":
            var = self.find_var(2)
            if var == -1: exit(56)
            symb2_type = var.get_variable_type()
            symb2 = var.get_variable_value()
        
        if symb2_type == "bool":
            symb2 = self.args[2].value
        else: 
            exit(53)

        if self.opcode == "AND":
            result = symb1 and symb2
        elif self.opcode == "OR":
            result = symb1 or symb2

        # save result
        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable('bool', result)

class Not(Instruction):
    def __init__(self, number):
        super().__init__("NOT", number)

    def check_instr(self):
        if (len(self.args) > 2):
            exit(52)

    def execute(self):
        # get type of symbol adn value
        symb1_type = self.args[1].arg_type
        if symb1_type == "bool":
            symb1 = self.args[1].value
        elif symb1_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb1_type = var.get_variable_type()
            symb1 = var.get_variable_value()

        if symb1_type != "bool":
            exit(53)

        result = not symb1
        
        # save result
        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable('bool', result)
class Int2Char(Instruction):
    def __init__(self, number):
        super().__init__("INT2CHAR", number)

    def check_instr(self):
        if (len(self.args) > 2):
            exit(52)

    def execute(self):
        # get type of symbol adn value
        symb1_type = self.args[1].arg_type
        if symb1_type == "int":
            symb1 = self.args[1].value
        elif  symb1_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb1_type = var.get_variable_type()
            if symb1_type != "int": exit(53)
            symb1 = var.get_variable_value()
        else:
            exit(53)
        
        if symb1 < 0 and symb1 > 1114111:
            exit(58)

        result = chr(symb1)
        
        # save result
        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable('string', result)
class StrI2Int(Instruction):
    def __init__(self, number):
        super().__init__("STRI2INT", number)

    def check_instr(self):
        if (len(self.args) > 3):
            exit(52)

    def execute(self):
        # get type of symbol adn value
        symb1_type = self.args[1].arg_type
        if symb1_type == "string":
            symb1 = self.args[1].value
        elif  symb1_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb1_type = var.get_variable_type()
            if symb1_type != "string": exit(53)
            symb1 = var.get_variable_value()
        else:
            exit(53)
        
        symb2_type = self.args[2].arg_type
        if symb2_type == "int":
            symb2 = int(self.args[2].value)
        elif  symb2_type == "var":
            var = self.find_var(1)
            if var == -1: exit(56)
            symb2_type = var.get_variable_type()
            if symb2_type != "int": exit(53)
            symb2 = int(var.get_variable_value())
        else:
            exit(53)
        
        lenght = len(symb1)
        if symb2 > lenght:
            exit(58)

        result = ord(symb1[symb2])
        
        # save result
        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable('string', result)


class Write(Instruction):
    def __init__(self, number):
        super().__init__("WRITE", number)

    def check_instr(self):
        # print("syntax analyzator")
        pass
    def execute(self):
        arg_type = self.args[0].arg_type
        if not(re.match(r"string|bool|int|nil|var", arg_type)):
            stderr.write("[WRITE] wrong type")
            exit(52)

        if  arg_type == "var":
            var = self.find_var(0)
            if var == -1: exit(56)

            result = var.get_variable_value()
        else:
            result = self.args[0].value

        if result == "nil":
            result = ""

        print(result, end='')
class Read(Instruction):
    def __init__(self, number):
        super().__init__("READ", number)

    def check_instr(self):
        # print("syntax analyzator")
        pass
    def execute(self):
        if input_file is None:
            value = input()
        else:
            print("soorrry")
            # read from file
            # f.open(input_file)
        
        arg_type = self.args[1].arg_type
        if not(re.match(r"string|bool|int", arg_type)):
            stderr.write("[READ] wrong type")
            exit(52)

        var = self.find_var(0)
        if var == -1: exit(56)
        var.update_variable(arg_type, value)


        

''' list of instruction '''
instructions = []

# parsovanie argumentov - argparse kniznica
parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, nargs=1, help="Usage: ")
parser.add_argument("--input", type=str, nargs=1, help="Usage: ")

args = parser.parse_args()
input_file = args.input

if args.source is None:
    # if input_file is None:
    #     exit(52)
    # read from stdin
    source_file = sys.stdin
else:
    source_file = args.source[0]

# print(args)
# load xml - xml ElementTree
# sort, prečítať, uložiť lable
''' reading from file '''
tree = ET.parse(source_file) # add input
root = tree.getroot()

root[:] = sorted(root, key=lambda child: child.get("order")) # sort by order pridar INT !!!!!!!!!

# Define a custom key function for sorting

# Print the sorted XML

'''check xml''' 
# missing root tag
if root.tag != 'program':
    stderr.write("mising root tag\n")
    exit(52) 

for child in root:
    if child.tag != 'instruction':
        stderr.write("missing instruction\n")
        exit(52)

    instruction_opcode = child.attrib["opcode"].upper()
    if instruction_opcode == "DEFVAR":
        instructions.append(Defvar(1))
    elif instruction_opcode == "MOVE":
        instructions.append(Move(2))
    elif instruction_opcode == "ADD" or instruction_opcode == "SUB" or instruction_opcode == "MUL" or instruction_opcode == "IDIV":
        instructions.append(ArithmeticOperations(instruction_opcode ,3))       
    elif instruction_opcode == "LT" or instruction_opcode == "GT" or instruction_opcode == "EQ":
        instructions.append(RelationalOperators(instruction_opcode, 3))
    elif instruction_opcode == "AND" or instruction_opcode == "OR":
        instructions.append(BooleanOperators(instruction_opcode, 3))
    elif instruction_opcode == "NOT":
        instructions.append(Not(2))
    elif instruction_opcode == "INT2CHAR":
        instructions.append(Int2Char(2))
    elif instruction_opcode == "STRI2INT":
        instructions.append(StrI2Int(2))
    elif instruction_opcode == "WRITE":
        instructions.append(Write(1))    
    elif instruction_opcode == "READ":
        instructions.append(Read(2))    
    elif instruction_opcode == "CONCAT":
        instructions.append(Concat(3))
    elif instruction_opcode == "STRLEN":
        instructions.append(Strlen(2))
    elif instruction_opcode == "GETCHAR":
        instructions.append(Getchar(3))
    elif instruction_opcode == "SETCHAR":
        instructions.append(Setchar(3))
        
    else:
        stderr.write("wrong opcode\n")
        exit(53)

    # iter trough child

    for instr_arg in child:
        root[:] = sorted(root, key=lambda instr_arg: instr_arg.tag[-1:]) # sort by order pridar INT !!!!!!!!!

        print(child.attrib["opcode"], child.attrib["order"], instr_arg.tag, instr_arg.attrib)

        if not ('order' in child.attrib) or not ('opcode' in child.attrib):
            stderr.write("missing order or opcode")
            exit(52)

        if not(re.match(r"arg[123]", instr_arg.tag)):
            stderr.write("wrong argument format")
            exit(52)

        # add arguments to instruction        
        instructions[int(child.attrib["order"])-1].add_argument(int(instr_arg.tag[3:]), instr_arg.attrib['type'], child.find(instr_arg.tag).text)

# interpret
for instr in instructions:
    # print("______instruction")
    # print(type(instr))
    instr.check_instr()
    instr.execute()

exit(0)
