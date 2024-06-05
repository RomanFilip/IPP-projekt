## Implementačná dokumentácia k 1. úlohe do IPP 2022/2023

Meno a priezvisko: Filip Roman \
Login: xroman16

### 1. Úvod
Úloha bola naimplementovať skript typu filter načitá zo štandartného vstupu zdrojový kód a vypíše na štandartný výstup XML reprezentaci programu podľa špecifikácií.

### 2. Implementácia
Skript parse.php zo štandartného vstupu zdrojový kód a spraví syntaktickú a lexikálnu analýzu. Chybové hlášenia vypisuje na štandartný chybový výstup podľa špecifikácie v zadaní. Lexika a syntax operátorov sa kontrolujú vo funkcií <code>check_operators()</code> a argumenty sa kontrolujú vo funkciach <code>check_var()</code>, <code>check_label()</code>, <code>check_symb()</code>, podľa ich typu kde následne prebieha kontrola pomocou regexou. Potom po úspešnej kontrole sa generujú inštrukcie a argumenty vo funkciach <code>printInstruction()</code>, <code>printArguments()</code>.




