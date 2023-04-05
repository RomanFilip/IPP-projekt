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
ap = argparse.ArgumentParser()
ap.add_argument("--source", nars=1, help="Usage: ")
ap.add_argument("--input", nars=1, help="Usage: ")

args = vars(ap.parse_args())



# load xml - xml ElementTree
# sort, prečítať, uložiť lable

''' reading from file '''
for f in fileinput.input():
    print(f)

tree = ET.parse(sourceFile) # add input

root = tree.getroot()


#  check xml 
if root.tag != 'program':
    exit(1)

# check childs
for child in root:
    if child.tag != 'instrukce':
        exit(1)
    child_arguments = list(child.attrib.keys)
    if not('order' in child_arguments) or not ('opcode' in child_arguments):
        exit(1)
    for subelem in child:
        # kontrola, regex
        if not(re.match(r"arg[123]", subelem.tag)):
            exit(1)

# xml to instruction
for e in root:
    # class, global var na generovanie instrukcie
    for subelem in e:
        instruction.add_argument(arg_type, value)

for i in instructions:
    interpret(i)

# interpret
