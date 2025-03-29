În fișierul funcțions.c:
- am definit două structuri pentru a stoca datele despre expresie
- structura date conține doar un vector de int în care se salvează valorile pentru operanzii unei paranteze
- structura expresie conține un vector din tipul date (va fi de lungimea nr de clauze din expresie; un element al acestui vector reprezită operatorii clauzei respecive), un întreg pentru stocarea numărului de paranteze și un întreg pentru numărul total de operanzi al expresiei

În fișierul functions.c:
- next_numar:
    - primește ca argument un string, calculează primul număr existent în acesta și îl returnează

- citire:
    - citesc inițial toate liniile care încep cu caracterul 'c'
    - din prima linie necomentată extrag nr de operanzi și pe cel al clauzelor
    - citesc următoarele linii pe rand, daca încep cu caracterul 'c', sar peste ele
    - daca sunt linii cu informații despre clauze le parcurg până întâlnesc caracterul '0' și extrag valorile operanzilor: dacă întâlnesc un '-' salvez la poziția respectivă în vectorul de operanzi ai clauzei valoarea -1, altfel salvez valoarea 1
    - la finalul funcției returnez structura care conține informațiile despre expresie

- verif_paranteza:
    - parcurg operanzii unei clauze și în cazul în care valoarea operatorului din vectorul de valori este egală cu cea din vectorul clauzei de la aceeași poziție (dă valoarea 1), este returnat 1 (clauza este satisfăcută)
    - dacă trec prin toți operanzii și niciunul nu dă 1, clauza nu este satisfăcută și returnez 0

- verif:
    - parcurg toate parantezele și verific satisfibilitatea fiecăreia, iar atunci când una nu este satisfăcută, returnez 0 (toata expresia nu este satisfăcută)
    - daca toate clauzele sunt în regulă, returnez 1

- unit_propag:
    - declar un vector în care voi salva indicii parantezelor nesatisfăcute până în momentul actual și dimensiunea acestuia
    - inițial adaug toți indicii pentru a putea verifica toate clauzele
    - parcurg vectorul de indici iar pentru fiecare clauză o salvez și îi parcurg operanzii
    - declar și 3 valori pentru a număra câți operatori nu au valoare atribuită, poziția ultimului, respectiv valoarea acestuia
    - daca operandul curent se află în clauza curentă, verific dacă este setat, iar în cazul în care nu este incrementez nr de operatori neatribuiți și salvez poziția și valoarea acestuia
    - altfel, daca operatorul este setat si are aceași valoare ca și în clauză înseamnă ca clauza este satisfăcută și nu mai are rost să continui căutarea
    - în cazul în care clauza este unitară, atribui vectorului de valori, valoarea elementului nesetat (pentru a putea satisface clauza) și actualizez vectorul de indici (adaug în acesta numai indicii clauzelor nesatisfăcute)
    - dacă toți operanzii implicați în clauză au o valoare alocată, dar clauza nu este satisfăcută, încetez propagarea

- bkt: (practic DPLL-ul)
    - condiția de oprire: am ajuns la finalul vectorului de valori (<=> valori pentru toți operanzii) și verific satisfiabilitatea expresiei
    - posibil ca prin unit_propag să fi setat valori care se află după poziția curentă din vector așa că iterez prin vector până ajung la sfârșit (caz în care verific satisfiabilitatea expresiei) sau până întâlnesc un operator nesetat
    - înainte de apelurile recursive salvez starea curentă a vectorului de valori pentru a putea da restore la întoarcerea din recursivitate
    - dau inițial valoarea 1 (true) operandului curent și verific dacă atât propagarea cât și backtracking-ul au returnat 1, iar în caz afirmativ returnez 1 (am găsit o soluție care satisface)
    - altfel copiez in vectorul de valori, informația care se afla în acesta înainte de apelul recursiv
    - aplic același procedeu și pentru valoarea -1 (false)
    - iar în cazul în care nici această valoare nu satisface, dau operandului curent valoarea 0 (starea de nesetat) și returnez 0 (fac revenirea din recursivitate pt cazul de nesatisfiabilitate)

- afisare:
    - dacă a fost găsită p soluție care satisface, afisez "s SATISFIABLE" și iterez prin vectorul de operatori
    - în cazul în care în care la poziția i am valoarea -1 afisez -(i+1), altfel i+1 -- iterația începe de la 0 (pt cazul în care este nesetat un operand, îi dau implicit valoarea true)
    - în cazul în care nu există o combinație care să satisfacă expresia afișez "s UNSATISFIABLE"

În fișierul main.c:
- preiau calea fișierului de intrare și a celui de ieșire, date ca argumente în linia de comandă și le deschid
- apalez funcția de citire și aloc memoria pentru vectorul de valori ale operanzilor
- apelez funcția de backtracking și rezultatul returnat de aceasta îl transmit ca parametru în funcția de afișare