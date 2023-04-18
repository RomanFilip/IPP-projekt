## Implementační dokumentace k 2. úloze do IPP 2022/2023
Jméno a příjmení: Filip Roman \
Login: xroman16

### 1. Úvod
Úloha bola naimplementovať skript <code>interpret.py</code> v jazyku Python3.10, ktorý načitá XML reprezentáciu programu s využitím vstupu podľa zadaných parametrov a následne ju interpretuje a generujú výstup.

### 2. Parametre
Môžeme spustiť skript s týmito parametrami, <code>--help</code> pre vypísanie nápovedy, <code>--source=file</code> pre nastavenie vstupného súboru s XML reprezentacie kódu, <code>--input=file</code> pre nastavenie vstupu pre samostatnú interpretaci zadaného zdrojového kódu.        

### 3. Implementácia
Skript číta vstupné data zo súbrou alebo zo vstupu podľa zadaného parametru pri spustení. 

Pri spracovaní vstupu skript používa vstavanú funkciu <code>xml.etree.ElementTree</code> ktorá nám uľahčuje pracovanie s xml.

Skript je zložený z niekoľkých objektov. Základným objektom je trieda <code>Instruction</code> ktorá obsahuje atribúty pre inštrukcie a funkcie na pracovanie s nimi. Z tejo triedy ďalej dedia všetky ďalšie triedy pre jednotlivé inštrukcie v ktoré následne obsahujú funkcie na interpretáciu danej inštrukcie. Nachádzajú sa tam aj trieda <code>Argument</code> ktorá komunikuje s triedou <code>Instruction</code> a sú tam uložené argumenty inštrukcie. Dôležitá trieda je trieda <code>Frames</code>, ktorá obsahuje rámce a funkcie na pracovanie s nimi.

Skript pomocou for cyklu prechádza všetkými inštrukciami a ukláda ich do listu <code>instructions</code> na pozíciu podľa parametru 'order' spoločne aj s ich argumentami. Pri čítaní si taktiež uložíme návestia a ich pozíciu do listu <code>labels</code>. Následne po spracovaní všetkých inštrikcií prechádzame listom <code>instructions</code> a interpetuje jednotlivé inštruckie.