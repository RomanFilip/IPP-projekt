"""@file interpret.py

Interpret XML reprezentace kódu
"""

import re
import argparse
from sys import stderr
import fileinput
import xml.etree.ElementTree as ET

# stderr.write("example of stderr\n")
# exit(0)

class argument:
    def __init__(self, arg_type, value):
        self.type = arg_type
        self.value = value

class instruction:
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.args = []

    def add_argument(self, arg_type, value):
        self.args.append(argument(arg_type, value))


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

# missing root tag
if root.tag != 'program':
    exit(52) 

for child in root:
    print(child.tag, child.attrib)

# #  check xml 
# if root.tag != 'program':
#     exit(1)

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
