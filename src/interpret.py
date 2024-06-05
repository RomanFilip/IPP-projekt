"""@file interpret.py

Interpret XML reprezentace kódu

@author: Filip Roman (xroman16)
"""

import re
import argparse
from sys import stderr
import sys
import xml.etree.ElementTree as ET

labels = []
data_stack = []
stack_position = []

class Argument:
    def __init__(self, number, arg_type, value):
        self.number = number
        self.arg_type = arg_type
        self.value = value

    def get_argument(self):
        print(self.number, self.arg_type, self.value)
    
    def get_argument_number(self):
        return self.number
    
    def get_argument_value(self):
        return self.value
    
    def get_argument_type(self):
        return self.arg_type

class Frame:
    def __init__(self):
        self.globalFrme = {}
        self.tmpFrame = {}
        self.tmpFrameDefined = False
        self.frameStack = []

    def get_frame(self, frame):
        if frame == "GF":
            return self.globalFrme
        elif frame == "LF":
            return self.frameStack[-1] if len(self.frameStack) > 0 else None
        elif frame == "TF":
            return self.tmpFrame if self.tmpFrameDefined else None
        else:
            return None
        
    def create_frame(self):
        self.tmpFrame = {}
        self.tmpFrameDefined = True

    def push_frame(self):
        if len(self.frameStack):
            self.frameStack.append(self.tmpFrame)
            self.tmpFrameDefined = False
        else:
            stderr.write("frame is not defined\n")
            exit(55)

    def pop_frame(self):
        if len(self.frameStack):
            self.tmpFrame == self.frameStack.pop()
            self.tmpFrameDefined = True
        else:
            stderr.write("empty stack\n")
            exit(55)
    
    def set_var(self, arg, arg_type, value):
        
        arg_value = arg.get_argument_value().split("@")
        frame = arg_value[0]; name = arg_value[1]
        frame_obj = self.get_frame(frame)
        if frame_obj is None:
            stderr.write("not defined\n")
            exit(52)
        if name not in frame_obj:
            stderr.write("variable doesnt exist\n")
            exit(54)
        frame_obj[name]["value"] = value
        frame_obj[name]["type_arg"] = arg_type

    def def_var(self, arg):
        arg_value = arg.get_argument_value().split("@")
        frame = arg_value[0]; name = arg_value[1]
        frame_obj = self.get_frame(frame)
        if frame_obj is None:
            stderr.write("not defined\n")
            exit(55)
        else:
            if name in frame_obj:
                stderr.write("variable cant redifine\n")
                exit(52)
            else:
                frame_obj[name] = {"value": None, "type_arg": None}
            
frames = Frame()
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

    def find_label(self, position):
        for labl in labels:
            if labl.get_label_name() == self.args[position].get_argument_value():
                return labl
        return -1

    def get_symb(self, number_of_argument):
            if self.args[number_of_argument].arg_type == "var": # is variable
                arg_value = self.args[number_of_argument].get_argument_value().split("@")
                frame = arg_value[0]; value = arg_value[1]
                frame_obj = frames.get_frame(frame)
                if frame_obj is None:
                    stderr.write("frame does not exist\n")
                    exit(55)
                if value not in frame_obj:
                    stderr.write("variable not defined\n")
                    exit(54)
                else:
                    if frame_obj[value]["type_arg"] is None:
                        return "", "nil"
                    return frame_obj[value]["value"], frame_obj[value]["type_arg"]
            else:                               # is constant
                symb_type = self.args[number_of_argument].arg_type
                symb = self.args[number_of_argument].value
            return (str(symb), symb_type)
        
class Defvar(Instruction):
    def __init__(self, number):
        super().__init__("DEFVAR", number)

    
    def execute(self):
        if (len(self.args) != 1):
            stderr.write("wrong argument\n")
            exit(32)

        if (self.args[0].arg_type != "var"):
            stderr.write("wrong argument arg_type\n")
            exit(32)

        frames.def_var(self.args[0])

class Createframe(Instruction):
    def __init__(self, number):
        super().__init__("CREATEFRAME", number)

    def execute(self):
        if (len(self.args) != 0):
            stderr.write("wrong argument\n")
            exit(32)
        frames.create_frame()
class Pushframe(Instruction):
    def __init__(self, number):
        super().__init__("PUSHFRAME", number)

    def execute(self):
        if (len(self.args) != 0):
            stderr.write("wrong argument\n")
            exit(32)

        frames.push_frame()
        
class Popframe(Instruction):
    def __init__(self, number):
        super().__init__("POPFRAME", number)

    def execute(self):
        if (len(self.args) != 0):
            stderr.write("wrong argument\n")
            exit(32)

        frames.pop_frame()
class Call(Instruction):
    def __init__(self, number, order):
        super().__init__("CALL", number)
        self.order = order

    def execute(self):
        if (len(self.args) != 1):
            stderr.write("wrong argument\n")
            exit(32)
        
        stack_position.append(self.order)
        lab = self.find_label(0)
        if lab == -1: 
            stderr.write("lable doesnt exists\n")
            exit(52)
        jump_to = lab.get_position()
        global position
        position = int(jump_to)-1

class Return(Instruction):
    def __init__(self, number):
        super().__init__("RETURN", number)

    def execute(self):
        if (len(self.args) != 0):
            stderr.write("wrong argument\n")
            exit(32)
        
        try:
            global position
            position = int(stack_position.pop())
        except IndexError:
            stderr.write("empty stack\n")
            exit(56)

class Pushs(Instruction):
    def __init__(self, number):
        super().__init__("PUSHS", number)

    def execute(self):
        if (len(self.args) != 1):
            stderr.write("wrong argument\n")
            exit(32)

        symb, symb_type = self.get_symb(0)
        if not (re.match(r"int|string|nil|bool|var", symb_type)):
            exit(32)
        
        data_stack.append((symb_type, symb))

class Pops(Instruction):
    def __init__(self, number):
        super().__init__("POPS", number)

    def execute(self):
        if (len(self.args) != 1):
            stderr.write("wrong argument\n")
            exit(52)

        try:
            arg_type, arg_value = data_stack.pop()
            frames.set_var(self.args[0], arg_type, arg_value)
        except IndexError:
            stderr.write("empty stack\n")
            exit(56)

        
class Move(Instruction):
    def __init__(self, number):
        super().__init__("MOVE", number)
    
    def execute(self):
        if len(self.args) != 2:
            stderr.write("wrong number of arguments")
            exit(32)

        if self.args[1].arg_type == "var":
            symb, symb_type = self.get_symb(1)
            frames.set_var(self.args[0], symb_type, symb)
        else:
            frames.set_var(self.args[0], self.args[1].arg_type, self.args[1].value)


class ArithmeticOperations(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def execute(self):
        if (len(self.args) != 3):
            exit(32)
        symb1, symb1_type = self.get_symb(1)
        if symb1_type != "int":
            exit(53)
        if not(re.match(r"^[-0-9]+$", symb1)):
            exit(32)

        symb2, symb2_type = self.get_symb(2)

        if symb2_type != "int":
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

        frames.set_var(self.args[0], "int", str(result))

class RelationalOperators(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def execute(self):
        if (len(self.args) != 3):
            exit(32)

        # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)
        # check supported types
        if not(re.match(r"int|bool|string|var", symb1_type)):
            exit(53)

        # get type of symbol and value
        symb2, symb2_type = self.get_symb(2)
        if not(re.match(r"int|bool|string|var", symb2_type)):
            exit(53)

        # check type compatibility
        if symb1_type != symb2_type:
            exit(53)

        if self.name == "LT":
            result = symb1 < symb2
        if self.name == "GT":
            result = symb1 > symb2
        
        # save result
        frames.set_var(self.args[0], "bool", str(result))

class Eq(Instruction):
    def __init__(self, number):
        super().__init__("GT", number)

    def execute(self):
        if (len(self.args) != 3):
            exit(32)

        # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)

        # check supported types
        if not(re.match(r"int|bool|string|var|nil", symb1_type)):
            exit(53)

        # get type of symbol and value
        symb2, symb2_type = self.get_symb(2)
        if not(re.match(r"int|bool|string|var|nil", symb2_type)):
            exit(53)

        # check type compatibility
        if symb1_type != symb2_type:
            if (symb1_type == "nil" or symb2_type == "nil"):
                result = False
            else:
                exit(53)
        else:
            result = symb1 == symb2
        
        # save result
        frames.set_var(self.args[0], "bool", str(result))

class BooleanOperators(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def execute(self):
        if (len(self.args) != 3):
            exit(32)
        # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)

        # check supported types
        if not(re.match(r"bool", symb1_type)):
            exit(53)
        if not(re.match(r"true|false", symb1)):
            exit(53)
        
        # get type of symbol adn value
        symb2, symb2_type = self.get_symb(2)
        # check supported types
        if not(re.match(r"bool", symb2_type)):
            exit(53)
        if not(re.match(r"true|false", symb2)):
            exit(53)

        if symb1 == "false":
            symb1 = ""
        if symb2 == "false":
            symb2 = ""
        if self.name == "AND":
            result = bool(symb1) and bool(symb2)
        if self.name == "OR":
            result = bool(symb1) or bool(symb2)
        
        # save result
        frames.set_var(self.args[0], "bool", str(result))

class Not(Instruction):
    def __init__(self, number):
        super().__init__("NOT", number)

    def execute(self):
        if (len(self.args) != 2):
            exit(32)

        # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)
        if symb1_type != "bool":
            exit(53)

        if symb1 == "false":
            symb1 = ""
        result = not bool(symb1)    
        
        # save result
        frames.set_var(self.args[0], "bool", str(result))

class Int2Char(Instruction):
    def __init__(self, number):
        super().__init__("INT2CHAR", number)

    def execute(self):
        if (len(self.args) != 2):
            exit(32)

        # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)
        if not(re.match(r"^[0-9]+$", symb1)):
            exit(53)
        symb1 = int(symb1)

        # print(symb1_type)
        if symb1_type != "int":
            stderr.write("wrong type bro\n")
            exit(52)    
        
        if symb1 < 0 or symb1 > 1114111:
            exit(58)

        result = chr(symb1)
        
        # save result
        frames.set_var(self.args[0], "string", result)

class StrI2Int(Instruction):
    def __init__(self, number):
        super().__init__("STRI2INT", number)

    def execute(self):
        if (len(self.args) != 3):
            exit(32)

        # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)
        if symb1_type != "string":
            exit(53)
        
        symb2, symb2_type = self.get_symb(2)
        if symb2_type != "int":
            exit(53)

        if not(re.match(r"^[0-9]+$", symb2)):
            exit(32)
        symb2 = int(symb2)

        lenght = len(symb1)
        if symb2 > lenght:
            exit(58)

        result = ord(symb1[symb2])
        
        # save result
        frames.set_var(self.args[0], "string", str(result))

class Write(Instruction):
    def __init__(self, number):
        super().__init__("WRITE", number)

    def execute(self):
        if len(self.args) != 1:
            stderr.write("wrong number of arguments")
            exit(32)

        value, arg_type = self.get_symb(0)
        if not(re.match(r"string|bool|int|nil|var", arg_type)):
            stderr.write("[WRITE] wrong type")
            exit(52)

        result = value
        if arg_type == "bool":
            if value == "True":
                result = "true"
            if value == "False":
                result = "false"
        elif arg_type == "nil":
            result = ""
        else:
            result = value
        
        # find and replace escape sequence
        ascii_char = re.search(r"([\\][0-9][0-9][0-9])", result)
        while ascii_char is not None:
            ascii_code = int(ascii_char.group()[1:])
            if ascii_code == 35 or ascii_code == 92 or (ascii_code >= 0 and ascii_code <= 32):
                result = result.replace(ascii_char.group(), chr(ascii_code))
            ascii_char = re.search(r"([\\][0-9][0-9][0-9])", result)

        print(result, end='')

class Read(Instruction):
    def __init__(self, number, input_file):
        super().__init__("READ", number)
        self.input_file = input_file

    def execute(self):
        if len(self.args) != 2:
            stderr.write("wrong number of arguments")
            exit(32)

        arg_value_type = self.args[1].get_argument_value()
        symb_type = self.args[1].get_argument_type()
        
        if symb_type != "type":
            exit(32)
        if not(re.match(r"string|bool|int", arg_value_type)):
            stderr.write("[READ] wrong type")
            exit(32)

        if self.input_file is None:
            read_value = input()
        else:
            try:        
                _input_file = open(self.input_file[0], "r")
                input_src = _input_file.read().splitlines()
            except FileNotFoundError:
                stderr.write("file not found\n")
                exit(11)

        global read_line
        try:
            read_value = input_src[read_line]
        except IndexError:
            read_value = ""
        read_line +=1

        if read_value == "":
            read_value = "nil"
            arg_value_type = "nil"

        if arg_value_type == "bool":
            if read_value.lower() == "true":
                read_value = "true"
            else:
                read_value = "false"

        if arg_value_type == "int":
            if not(re.match(r"^[-0-9]+$", read_value)):
                read_value = "nil"
                arg_value_type = "nil"

        frames.set_var(self.args[0], arg_value_type, read_value)

class Concat(Instruction):
    def __init__(self, number):
        super().__init__("CONCAT", number)

    def execute(self):
        if (len(self.args) != 3):
            stderr.write("missing argument")
            exit(32)

         # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)

        # check supported types
        if not(re.match(r"string", symb1_type)):
            exit(53)

        # get type of symbol and value
        symb2, symb2_type = self.get_symb(2)

        # check supported types
        if not(re.match(r"string", symb2_type)):
            exit(53)
        
        result = symb1 + symb2
        
        # save result
        frames.set_var(self.args[0], "string", str(result))


class Strlen(Instruction):
    def __init__(self, number):
        super().__init__("STRLEN", number)

    def execute(self):
        if (len(self.args) != 2):
            stderr.write("missing argument")
            exit(32)

         # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)

        # check supported types
        if not(re.match(r"string", symb1_type)):
            exit(53)

        result = len(symb1)

        # save result
        frames.set_var(self.args[0], "int", str(result))

class Getchar(Instruction):
    def __init__(self, number):
        super().__init__("GETCHAR", number)

    def execute(self):
        if (len(self.args) != 3):
            stderr.write("missing argument")
            exit(32)

         # get type of symbol adn value
        symb1, symb1_type = self.get_symb(1)

        # check supported types
        if not(re.match(r"string", symb1_type)):
            exit(53)

        # get type of symbol and value
        symb2, symb2_type = self.get_symb(2)

        # check type compatibility
        if not(re.match(r"int", symb2_type)):
            exit(53)
        if not(re.match(r"^[-0-9]+$", symb2)):
            exit(32)
        symb2 = int(symb2)
        
        if len(symb1) < symb2 or symb2 < 0:
            exit(58)
            
        result = symb1[symb2]
        
        # save result
        frames.set_var(self.args[0], "string", str(result))

class Setchar(Instruction):
    def __init__(self, number):
        super().__init__("SETCHAR", number)

    def execute(self):
        if (len(self.args) != 3):
            stderr.write("missing argument")
            exit(32)

        # get type of symbol and value
        symb1, symb1_type = self.get_symb(1)

        # check type compatibility
        if not(re.match(r"int|var", symb1_type)):
            exit(53)
        if not(re.match(r"^[-0-9]+$", symb1)):
            exit(32)
        symb1 = int(symb1)

        symb2, symb2_type = self.get_symb(2)

        # check supported types
        if not(re.match(r"string|var", symb2_type)):
            exit(53)

        length = len(symb2)
        if length == 0:
            exit(58)
        if length > 1:
            symb2 = symb2[0]
        
        var, var_type = self.get_symb(0)
        if not(re.match(r"string", var_type)):
            exit(53)

        if (len(var) < symb1) or (symb1 < 0):
            exit(58)

        result = var.replace(var[symb1], symb2)
        frames.set_var(self.args[0], "string", str(result))

class Type(Instruction):
    def __init__(self, number):
        super().__init__("TYPE", number)

    def execute(self):
        if (len(self.args) != 2):
            stderr.write("missing argument")
            exit(32)

         # get type of symbol adn value
        if self.args[1].arg_type == "var": # is variable
            var, var_type = self.get_symb(1)           
            if var == "":
                result_type = ""
            else:
                result_type = var_type
        else:                               # is constant
            result_type = self.args[1].arg_type

        result = result_type
        frames.set_var(self.args[0], "string", str(result))

        
        
class Dprint(Instruction):
    def __init__(self, number):
        super().__init__("DPRINT", number)

    def execute(self):
        if (len(self.args) != 1):
            stderr.write("missing argument")
            exit(32)

        symb, _ = self.get_symb(0)
        stderr.write(symb + "\n")

class Break(Instruction):
    def __init__(self, number):
        super().__init__("BREAK", number)

    def execute(self):
        if (len(self.args) != 0):
            stderr.write("missing argument")
            exit(32)

        global position
        stderr.write("[BREAK] instruction number" + position + "\n")

class Label(Instruction):
    def __init__(self, opcode,  number, order):
        super().__init__(opcode, number)
        self.order = order
        self.label_name = ""
    
    def set_name(self):
        if (len(self.args) != 1):
            stderr.write("missing argument labrl ")
            exit(32)
        self.label_name= self.args[0].value
    
    def execute(self):
        if (len(self.args) != 1):
            stderr.write("missing argument labr")
            exit(32)
    
    def get_position(self):
        return self.order
    def get_label_name(self):
        return self.label_name
    
class ConditionalJump(Instruction):
    def __init__(self, opcode, number):
        super().__init__(opcode, number)

    def execute(self):
        if (len(self.args) != 3):
            stderr.write("missing argument")
            exit(32)

        symb1, symb1_type = self.get_symb(1)

        symb2, symb2_type = self.get_symb(2)

        if symb1_type != symb2_type:
            if symb1_type != "nill" or symb2_type != "nill":
                exit(53)   

        global position
        if self.name == "JUMPIFEQ":
            if symb1 == symb2:
                lab = self.find_label(0)
                if lab == -1: 
                    stderr.write("lable doesnt exists\n")
                    exit(52)
                jump_to = lab.get_position()
                position = int(jump_to)-1
        else:
            if symb1 != symb2:
                lab = self.find_label(0)
                if lab == -1: 
                    stderr.write("lable doesnt exists\n")
                    exit(52)
                jump_to = lab.get_position()
                position = int(jump_to)-1

class Jump(Instruction):
    def __init__(self, number):
        super().__init__("JUMP", number)

    def execute(self):
        if (len(self.args) != 1):
            stderr.write("missing argument")
            exit(32)

        global position
        lab = self.find_label(0)
        if lab == -1: 
            stderr.write("lable doesnt exists\n")
            exit(52)
        jump_to = lab.get_position()
        position = int(jump_to)-1
class Exit(Instruction):
    def __init__(self, number):
        super().__init__("EXIT", number)

    def execute(self):
        if (len(self.args) != 1):
            stderr.write("missing argument")
            exit(32)

        symb, symb_type = self.get_symb(0)
        if symb_type != "int":
            exit(53)

        if not(re.match(r"^[0-9]+$", symb)):
            exit(57)

        symb = int(symb)
        if symb > 49:
            exit(57)

        exit(symb)

class Empty:
    def __init__(self):
        pass
    
    def execute(self):
        pass

    

''' list of instruction '''
instructions = []
def sortFun(e):
    return e.number

if __name__ == "__main__":

    # parsovanie argumentov
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, nargs=1, help="Usage: ")
    parser.add_argument("--input", type=str, nargs=1, help="Usage: ")

    args = parser.parse_args()
    input_file = args.input

    read_line = 0
    if input_file is not None:
        pass
    if args.source is None:
        source_file = sys.stdin
    else:
        source_file = args.source[0]

    ''' reading from file '''
    try:
        tree = ET.parse(source_file) # add input
    except ET.ParseError as e:
        message = getattr(e, 'message', str(e))
        message = message.split(":")
        if message[0] == "XML or text declaration not at start of entity":
            exit(32)
        stderr.write("catching exeption parsing\n")
        exit(31)

    root = tree.getroot()
    if root.tag != 'program':
        stderr.write("mising root tag\n")
        exit(32) 

    # sort instruction by order
    try:
        root[:] = sorted(root, key=lambda child: int(child.get("order"))) # sort by order pridar INT !!!!!!!!!
    except TypeError:
        stderr.write("catching exeption\n")
        exit(32)
    except ValueError:
        stderr.write("catching exeption wrong order\n")
        exit(32)

    '''check xml''' 
    last_instruction_order = 0
    for child in root:
        if child.tag != 'instruction':
            stderr.write("missing instruction\n")
            exit(32)

        if not ('order' in child.attrib) or not ('opcode' in child.attrib):
                stderr.write("missing order or opcode")
                exit(32)

        instruction_order = child.attrib["order"]
        if not(re.match(r"^[ 0-9]+$", instruction_order)):
            stderr.write("must be int\n")
            exit(32)
        else:
            instruction_order = int(instruction_order)

        if last_instruction_order >= instruction_order: 
            stderr.write("wrong order\n")
            exit(32)
        
        # add empty class
        while (last_instruction_order+1) != instruction_order:
            instructions.append(Empty())
            last_instruction_order += 1

        last_instruction_order = instruction_order

        instruction_opcode = child.attrib["opcode"].upper()

        ''' add instruction to list '''
        if instruction_opcode == "DEFVAR":
            instructions.append(Defvar(1))
        elif instruction_opcode == "MOVE":
            instructions.append(Move(2))
        elif instruction_opcode == "CREATEFRAME":
            instructions.append(Createframe(0))
        elif instruction_opcode == "PUSHFRAME":
            instructions.append(Pushframe(0))
        elif instruction_opcode == "POPFRAME":
            instructions.append(Popframe(0))
        elif instruction_opcode == "CALL":
            instructions.append(Call(1, child.attrib["order"]))
        elif instruction_opcode == "RETURN":
            instructions.append(Return(0))
        elif instruction_opcode == "PUSHS":
            instructions.append(Pushs(1))
        elif instruction_opcode == "POPS":
            instructions.append(Pops(1))
        elif instruction_opcode == "ADD" or instruction_opcode == "SUB" or instruction_opcode == "MUL" or instruction_opcode == "IDIV":
            instructions.append(ArithmeticOperations(instruction_opcode ,3))       
        elif instruction_opcode == "LT" or instruction_opcode == "GT":
            instructions.append(RelationalOperators(instruction_opcode, 3))
        elif instruction_opcode == "EQ":
            instructions.append(Eq(3))
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
            instructions.append(Read(2, input_file))    
        elif instruction_opcode == "CONCAT":
            instructions.append(Concat(3))
        elif instruction_opcode == "STRLEN":
            instructions.append(Strlen(2))
        elif instruction_opcode == "GETCHAR":
            instructions.append(Getchar(3))
        elif instruction_opcode == "SETCHAR":
            instructions.append(Setchar(3))
        elif instruction_opcode == "SETCHAR":
            instructions.append(Setchar(3))
        elif instruction_opcode == "TYPE":
            instructions.append(Type(2))
        elif instruction_opcode == "LABEL":
            instructions.append(Label(instruction_opcode, 1, child.attrib["order"]))
        elif instruction_opcode == "JUMP":
            instructions.append(Jump(1))
        elif instruction_opcode == "JUMPIFEQ" or instruction_opcode == "JUMPIFNEQ":
            instructions.append(ConditionalJump(instruction_opcode, 3))
        elif instruction_opcode == "EXIT":
            instructions.append(Exit(1))
        elif instruction_opcode == "DPRINT":
            instructions.append(Dprint(3))
        elif instruction_opcode == "BREAK":
            instructions.append(Break(3))
        else:
            stderr.write("wrong opcode\n")
            exit(32)

        # iter trough child
        for instr_arg in child:
            if not(re.match(r"arg[123][ ]*", instr_arg.tag)):
                stderr.write("wrong argument format\n")
                exit(32)

            # add arguments to instruction
            argumen_value = child.find(instr_arg.tag).text
            if argumen_value is None:
                if instr_arg.attrib['type'] == "string":
                    argumen_value = " "
                else:
                    stderr.write("wrong argumetn type\n")
                    exit(32)
            
            try:        
                instructions[instruction_order-1].add_argument(int(instr_arg.tag[3:]), instr_arg.attrib['type'], argumen_value.strip())
            except KeyError:
                stderr.write("wrong type\n")
                exit(32)

            # sort by argument order
            instructions[instruction_order-1].args.sort(key=sortFun)

            # save label
            if instruction_opcode == "LABEL":
                _label = instructions[instruction_order-1].find_label(0)
                if _label != -1:
                    stderr.write("label aleready exists\n")
                    exit(52)
                instructions[instruction_order-1].set_name()
                labels.append(instructions[instruction_order-1])

        # check arguments number
        args_length = len(instructions[instruction_order-1].args)
        if args_length == 1:
            if instructions[instruction_order-1].args[0].get_argument_number() != 1:
                stderr.write("missing argument 1\n")
                exit(32)
        elif args_length > 1:
            if instructions[instruction_order-1].args[1].get_argument_number() != 2:
                stderr.write("missing argument 2\n")
                exit(32)

    position = 0
    while position < len(instructions):
        instructions[position].execute()
        position += 1

    
