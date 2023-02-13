<?php
ini_set('display_errors', 'stderr');


/**
 * print instruction and save instruction order
 */
function printInstruction($order, $instruction) {
    echo("\t<instruction order=\"".$order."\" opcode=\"".$instruction."\">\n");
    return $order + 1;
}

function printArguments($argument, $order) {
    echo("\t\t<arg".$order." type=\"var\">$argument</arg".$order.">\n");
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

#### TODO
/*
    dakadicky kod v stringu
    kontrola ci je iba 
*/

echo("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
while($line = fgets(STDIN)) {
    // echo($line);
    $splitted_line = explode(' ', trim($line, "\n")); 
    if ($splitted_line[0] == '.IPPcode23') {
        $header = true;
        echo("<program language=\"IPPcode23\">\n");
    } 
    if ($header == false) {
        exit(21); # chybna hlavicka;
    }
    // check trim
    // oddelit komentar strip
    // echo($splitted_line[0])."\n";
    // echo count($splitted_line)."\n";

    switch(strtoupper($splitted_line[0])) {
        // 1 var
        case 'POPS':
        case 'DEFVAR':
            $order = printInstruction($order, $splitted_line[0]);
            if (preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*/", $splitted_line[1])) {
                printArguments($splitted_line[1], 1);
                // echo("\t\t<arg1 type=\"var\">$splitted_line[1]</arg1>\n");
            } else {
                exit(23);
            }
            echo("\t</instruction>\n");
            break;
        // label
        case 'CALL':
        case 'LABEL':
        case 'JUMP':
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            // check if is defined?
            echo("\t</instruction>\n");
            break;
        case 'MOVE':
            // check if is something after
            // if ($splitted_line[3][0] != '#') {
            //     echo("sorry broooo\n");
            //     exit(99);
            // }
            $order = printInstruction($order, $splitted_line[0]);
            if (preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*|string@[a-zA-Z][a-zA-Z]*|nil@nil|bool@(true|false)/", $splitted_line[1])) {
                printArguments($splitted_line[1], 1);
                if (preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*|string@[a-zA-Z][a-zA-Z]*|nil@nil|bool@(true|false)/", $splitted_line[2])) {
                    // printArguments($splitted_line[2], 2);
                    $newstring = substr($splitted_line[2], -3);
                    echo("\t\t<arg2 type=\"int\">".$newstring."</arg2>\n");
                }
            } 
            echo("\t</instruction>\n");
            break;
        case 'PUSHS':
            $order = printInstruction($order, $splitted_line[0]);
            if (preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*|string@[a-zA-Z][a-zA-Z]*|nil@nil|bool@(true|false)/", $splitted_line[1])) {
                printArguments($splitted_line[1], 1);
                echo("\t</instruction>\n");
            }
            break;
        // var symb1 symb2
        case 'ADD':
        case 'SUB':
        case 'MUL':
            $order = printInstruction($order, $splitted_line[0]);
            if(preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*/", $splitted_line[1]) && 
            preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*/", $splitted_line[2])&&
            preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*/", $splitted_line[3])){
                printInstruction($splitted_line[1], 1);
                printInstruction($splitted_line[2], 2);
                printInstruction($splitted_line[3], 3);
            }
            echo("\t</instruction>\n");
            break;
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'NOT':
        case 'STRI2INT':
            $order = printInstruction($order, $splitted_line[0]);
            printInstruction($splitted_line[1], 1);
            printInstruction($splitted_line[2], 2);
            printInstruction($splitted_line[3], 3);
            echo("\t</instruction>\n");
        //
        case 'INT2CHAR':
        case 'READ':
        case 'CONCAT':
        case 'STRLEN':
        case 'GETCHAR':
        case 'SETCHAR':
        case 'TYPE':
        case 'JUMPIFEQ':            
        case 'JUMPIFNEQ': 
        //  
        case 'WRITE': // todo
        case 'EXIT':
        case 'DPRINT':
        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
            $order = printInstruction($order, $splitted_line[0]);
            echo("\t</instruction>\n");
            break;
    }
}
echo("</program>\n");
exit(0);

?>