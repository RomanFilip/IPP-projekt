<?php
ini_set('display_errors', 'stderr');


define("SUCCESS", 0);
define("ERROR_MISSING_PARAMETER", 10);
define("ERROR_OPEN_FILE", 12);
define("ERROR_INTERNAL", 99);
define("ERROR_MISSING_HEADER", 21);
define("ERROR_OPERATING_CODE", 22);
define("ERROR_LEX_SYNTAX", 23);

/**
 * print instruction and save instruction order
 */
function printInstruction($order, $instruction) {
    echo("\t<instruction order=\"".$order."\" opcode=\"".strtoupper($instruction)."\">\n");
    return $order + 1;
}

function printArguments($argument, $order, $isLabel=false) {
    if($isLabel) {
        echo("\t\t<arg".$order." type=\"label\">$argument</arg".$order.">\n");
        return;
    }

    if(!strpos($argument, '@')) {
        $type = 'type';
        echo("\t\t<arg".$order." type=\"".$type."\">$argument</arg".$order.">\n");
        return;
    }
    $operation = explode('@', $argument);
    switch($operation[0]) {
        case 'int':
            $type = "int";
            $argument = $operation[1];
            break;
        case 'bool':
            $type = "bool";
            $argument = $operation[1];
            break;
        case 'string':
            $type = "string";
            $argument = $operation[1];
            
            // $argument = preg_replace('/&/', '&amp', $argument);
            break;
        case 'nil':
            $type = "nil";
            $argument = $operation[1];
            break;
        case 'GF':
        case 'LF':
        case 'TF':
            $type = "var";
            $argument = $argument;
            break;
        default:
            exit(ERROR_LEX_SYNTAX);
        }
        $argument = preg_replace('/&/', '&amp;', $argument);
    $argument = preg_replace('/</', '&lt;', $argument);
    $argument = preg_replace('/>/', '&gt;', $argument);
    echo("\t\t<arg".$order." type=\"".$type."\">$argument</arg".$order.">\n");
}

function check_var($var) {
    return preg_match("/^((LF|GF|TF)@[a-zA-Z$&\-_%*!?][a-zA-Z0-9$&\-_%*!?]*)$/", $var);
}
function check_label($label) {
    return preg_match("/^([a-zA-Z$&\-_%*!?][a-zA-Z0-9$&\-_%*!?]*)$/", $label);
}
function check_symb($symb) {
    return preg_match("/^((LF|GF|TF)@[a-zA-Z0-9$&\-_%*!?]*|int@[-+0-9][0-9]*|string@([ -\"$-\[\]-ž]*[\\000-032]*)*|nil@nil|bool@(true|false))$/", $symb);
}
function check_type($type) {
    // return preg_match("/^(int(@[-+0-9][0-9]*)*|string(@([ -\"$-\[\]-ž]*[\\000-032]*)*)*|bool(@(true|false)))*$/", $type);
    return preg_match("/^(int|bool|string)*$/", $type);
}

// function check_header($line, $header) {
//     if (preg_match("/^[\s]*(\.IPPcode23)[\s]*$/", $line)) {
//         if($header) exit(ERROR_OPERATING_CODE);
//         echo("<program language=\"IPPcode23\">\n");
//         return true;
//     } 
//     return false;
// }

function check_arguments_lenght($number_of_arguments, $line) {
    $lenght = count($line);
    if (!$line[$lenght-1]) $lenght--;
    return $number_of_arguments == $lenght;
}


function check_operators($splitted_line, $order) {
    switch(strtoupper($splitted_line[0])) {
        // 1 var
        case 'POPS':
        case 'DEFVAR':
            if (!check_var($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(2, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            // array_push($variables, $splitted_line[1]);
            break;
        // label
        case 'LABEL':
        case 'CALL':
        case 'JUMP':
            // if (!array_search($splitted_line[1], $labelList)) exit(ERROR_LEX_SYNTAX);
            if (!check_label($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(2, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1, true);
            // check if is defined?
            break;
        case 'MOVE':
            if (!check_var($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[2])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(3, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            printArguments($splitted_line[2], 2);
            break;
        case 'PUSHS':
        case 'WRITE': 
            if (!check_symb($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(2, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            break;
        // var symb1 symb2
        case 'NOT':
            if (!check_var($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[2])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(3, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            printArguments($splitted_line[2], 2);
            break;
        case 'ADD':
        case 'SUB':
        case 'MUL':
            // $order = printInstruction($order, $splitted_line[0]);
            // if(preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*/", $splitted_line[1]) && 
            // preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*/", $splitted_line[2])&&
            // preg_match("/(Lf|GF|TF)@[a-zA-Z#&*$][a-zA-Z#&*$0-9]*|int@[-+0-9][0-9]*/", $splitted_line[3])){
            //     printInstruction($splitted_line[1], 1);
            //     printInstruction($splitted_line[2], 2);
            //     printInstruction($splitted_line[3], 3);
            // } exit(ERROR_LEX_SYNTAX);
            // break;
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'CONCAT':
        case 'STRI2INT':
        case 'SETCHAR':
        case 'GETCHAR':
            if (!check_var($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[2])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[3])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(4, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            printArguments($splitted_line[2], 2);
            printArguments($splitted_line[3], 3);
            break;
        //
        case 'JUMPIFEQ':            
        case 'JUMPIFNEQ': 
            if (!check_label($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[2])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[3])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(4, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1, true);
            printArguments($splitted_line[2], 2);
            printArguments($splitted_line[3], 3);
            // check if is defined?
            break;
        case 'TYPE':
        case 'STRLEN':
        case 'INT2CHAR':
            if (!check_var($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_symb($splitted_line[2])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(3, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            printArguments($splitted_line[2], 2);
            break;
        case 'READ':
            // syntax todo
            if (!check_var($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (count($splitted_line) < 3) exit(ERROR_LEX_SYNTAX);
            // if (!check_var($splitted_line[2])) exit(ERROR_LEX_SYNTAX);
            // if (!check_arguments_lenght(2, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            for ($i = 2; $i < count($splitted_line); $i++) {
                if(!check_type($splitted_line[$i])) exit(ERROR_LEX_SYNTAX);
                printArguments($splitted_line[$i], $i);
                
            }
            break;
        //  

        case 'EXIT':
        case 'DPRINT':
            if (!check_symb($splitted_line[1])) exit(ERROR_LEX_SYNTAX);
            if (!check_arguments_lenght(2, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            printArguments($splitted_line[1], 1);
            break;
        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
            if (!check_arguments_lenght(1, $splitted_line)) exit(ERROR_LEX_SYNTAX);
            $order = printInstruction($order, $splitted_line[0]);
            break;
        case '#':
        case '.IPPCODE23':
            break;
        default:
            if ($splitted_line[0][0] != '#') exit(ERROR_OPERATING_CODE);
    }
    if($splitted_line[0] != '.IPPcode23' && $splitted_line[0][0] != '#') echo("\t</instruction>\n");
    return $order;
}

// spracovanie parametrov
if ($argc > 1){
    if ($argv[1] == "--help") {
        echo("Skript typu filtr nacita za standartneho vstupu zdrojovy kod v IPPcode23, zkontroluje lexikalnu
        a syntakticku spravnost kodu a vypise na standartny vystup XML reprezentace programu.\n");
        exit(SUCCESS);
    }
    exit(ERROR_MISSING_PARAMETER);
} 
 
$order = 1;
$header = false;

$variables = [];
// $labelList = [];

#### TODO
/*
    dakadicky kod v stringu
    kontrola ci je iba 
*/

echo("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
while($line = fgets(STDIN)) {
    // echo($line);
    $line = preg_replace('/(?<!^)#.*/', '', $line);
    $line = preg_replace('/\s+/', ' ', $line);
    
    // if ($splitted_line[0] == '.IPPcode23') {
    if (preg_match("/^[\s]*(\.IPPcode23)[\s]*$/", $line)) {
        if($header) exit(ERROR_OPERATING_CODE);
        $header = true;
        echo("<program language=\"IPPcode23\">\n");
    } 

    $splitted_line = explode(' ', trim($line, "\n")); 
        
    if ($splitted_line[0][0] != '#' && $splitted_line[0]) {
        if ($header == false) {
            exit(ERROR_MISSING_HEADER); # chybna hlavicka;
        }
        // kontrola operatorov
        $order = check_operators($splitted_line, $order);
    }
    
    // if($operators != SUCCESS) exit($operators);

}
echo("</program>\n");
exit(SUCCESS);

?>