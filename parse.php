<?php
ini_set('display_errors', 'stderr');


/**
 * print instruction and save instruction order
 */
function printInstruction($order, $instruction) {
    echo("\t<instruction order=\"".$order."\" opcode=\"".$instruction."\">\n");
    return $order + 1;
}

// spracovanie parametrov
if ($argc > 1){
    if ($argv[1] == "--help") {
        echo("Skript typu filtr nacita za standartneho vstupu zdrojovy kod v IPPcode23, zkontroluje lexikalnu
        a syntakticku spravnost kodu a vypise na standartny vystup XML reprezentace programu.\n");
        exit(0);
    }
    exit(10);
} 
 
$order = 1;
$header = false;

echo("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
while($line = fgets(STDIN)) {
    echo($line);
    if ($line == ". IPPcode23") {
        $header = true;
        echo("<program language=\"IPPcode23\">\n");
    }
    $splitted_line = explode(' ', trim($line, "\n")); 
    // check trim
    // oddelit komentar strip
    echo($splitted_line[0])."\n";

    switch(strtoupper($splitted_line[0])) {
        // 1 var
        case 'POPS':
        case 'DEFVAR':
            $order = printInstruction($order, $splitted_line[0]);
            if (preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*/", $splitted_line[1])) {
                echo("\t\t<arg1 type=\"var\">$splitted_line[1]</arg1>\n");
            }
            echo("\t</instruction>\n");
        // label
        case 'CALL':
        case 'LABEL':
        case 'JUMP':
            $order = printInstruction($order, $splitted_line[0]);
            // check if is defined?
            echo("\t</instruction>\n");
        case 'MOVE':
            
        case 'PUSHS':
        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'NOT':
        case 'INT2CHAR':
        case 'STRI2INT':
        case 'READ':
        case 'WRITE':
        case 'CONCAT':
        case 'STRLEN':
        case 'GETCHAR':
        case 'SETCHAR':
        case 'TYPE':
        case 'JUMPIFEQ':            
        case 'JUMPIFNEQ': 
        //           
        case 'EXIT':
        case 'DPRINT':
        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
            $order = printInstruction($order, $splitted_line[0]);
            echo("\t</instruction>\n");
    }
}
echo("</program>\n");


?>