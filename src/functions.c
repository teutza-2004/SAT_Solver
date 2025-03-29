#include "functions.h"

// extrag urmatorul numar din string
int next_numar (char **string) {
    int i = 0, nr = 0;
    char *s = *string;
    while (s[i] == ' ')
        i++;
    while (s[i] >= '0' && s[i] <= '9') {
        nr *= 10;
        nr += (s[i] - '0');
        i++;
    }
    *string  = s + i;
    return nr;
}

// citirea si parsarea informatiilor din fisier
expresie citire() {
    expresie ex;
    char *string = calloc(100, sizeof(char));

    do {
        fgets(string, 100, stdin);
    } while (*string == 'c'); // sar peste liniile cu comentarii de la inceputul fisierului
    string += 6;
    ex.nr_op = next_numar(&string); // preiau nr operanzilor
    string += 1;
    ex.nr_p = next_numar(&string); // preiau nr clauzelor

    ex.paranteze = calloc(ex.nr_p, sizeof(date));

    for (int i = 0; i < ex.nr_p; i++) {
        fgets(string, 100, stdin);
        if (*string == 'c') { // sar peste liniile cu comentarii
            i--;
            continue;
        }
        (ex.paranteze + i)->operatori = calloc(ex.nr_op, sizeof(int)); // aloc vectorul de operatori al clauzei

        int op; // valorea int a x (al catelea op)
        // extragerea valorilor operanzilor
        // in structura mea sunt salvate doar ca 1 sau -1 in functie de cum apar in input
        for (; *string != '0'; ) {
            if (*string == '-') {
                string += 1;
                op = next_numar(&string) - 1;
                *((ex.paranteze + i)->operatori + op) = -1;
            } else {
                op = next_numar(&string) - 1;
                *((ex.paranteze + i)->operatori + op) = 1;
            }
            while (*string == ' ') {
                string += 1;
            }
        }
    }
    return ex;
}

// verifica daca o singura clauza da 1 pe valorile curente
int verif_paranteza(date *paranteza, int *satisf, int nr_op) {
    for (int i = 0; i < nr_op; i++) {
        if (*(paranteza->operatori + i) == *(satisf + i) && *(satisf + i)) {
            return 1;
        }
    }
    return 0;
}

// verifica daca toata expresia da 1 pe valorile curente
int verif(expresie ex, int *satisf) {
    for (int i = 0; i < ex.nr_p; i++) {
        if (!verif_paranteza(ex.paranteze + i, satisf, ex.nr_op)) {
            return 0;
        }
    }
    return 1;
}

// functia care face unit propagation
int unit_propag(expresie ex, int *satisf) {
    // vector in care salvez indicii parantezelor
    int *indici = (int *)malloc(ex.nr_p * sizeof(int));
    int size = 0;

    // initial adaug in vector indicele fiecarei paranteze
    for (int i = 0; i < ex.nr_p; i++) {
        *(indici + size) = i;
        size++;
    }

    // "parcurg" vectorul de indici
    while (size > 0) {
        size--;
        date *paranteza = ex.paranteze + *(indici + size); // extrag clauza curenta
        int nr = 0, poz = -1, elem = 0; // nr cati operatori am gasit neatribuiti, pozitia sa si valoarea

        for (int i = 0; i < ex.nr_op; i++) {
            if (*(paranteza->operatori + i)) { // daca exista operatorul in clauza curenta
                if (*(satisf + i) == 0) { // verific daca nu este alocata nicio valoare operandului
                    nr++;
                    poz = i;
                    elem = *(paranteza->operatori + i);
                } // daca operatorul are deja alocata valoare si este cea din clauza nu mai caut (clauza este satisfacuta) 
                else if (*(satisf + i) == *(paranteza->operatori + i)) {
                    nr = -1;
                    break;
                }
            }
        }

        if (nr == 1) { // am gasit o clauza unitara
            *(satisf + poz) = elem;
            size = 0;
            for (int j = 0; j < ex.nr_p; j++) { // adaug in lista indicii clauzelor nesatisfacute pana in acest moment
                if (!verif_paranteza(ex.paranteze + j, satisf, ex.nr_op)) {
                    *(indici + size) = j;
                    size++;
                }
            }
        } // toti operanzii au o valoare alocata, iar clauza nu este satisfacuta
        else if (nr == 0 && !verif_paranteza(paranteza, satisf, ex.nr_op)) {
            free(indici);
            return 0;
        }
    }
    free(indici);
    return 1;
}

int bkt(expresie ex, int *satisf, int p) {
    if (p == ex.nr_op) { // am selectat valori pentru toti operanzii
        return verif(ex, satisf);
    }
    // parcurg vectorul de valori ai operanzilor pana gasec unul neatribuit
    while (p < ex.nr_op && *(satisf + p) != 0) {
        p++;
    }
    if (p == ex.nr_op) {
        return verif(ex, satisf);
    }
    
    // salvez starea curenta a vectorului de valori pentru a putea da restore la intoarcerea din recursivitate
    int *saved_satisf = (int *)malloc(ex.nr_op * sizeof(int));
    memcpy(saved_satisf, satisf, ex.nr_op * sizeof(int));

    // pt operanzii care nu sunt in clauze unitare adaug recursiv valori (backtracking)
    *(satisf + p) = 1;
    if (unit_propag(ex, satisf) && bkt(ex, satisf, p + 1)) {
        free(saved_satisf);
        return 1;
    }
    memcpy(satisf, saved_satisf, ex.nr_op * sizeof(int));

    *(satisf + p) = -1;
    if (unit_propag(ex, satisf) && bkt(ex, satisf, p + 1)) {
        free(saved_satisf);
        return 1;
    }
    memcpy(satisf, saved_satisf, ex.nr_op * sizeof(int));

    *(satisf + p) = 0;
    free(saved_satisf);
    return 0;
}


// int bkt(expresie ex, int *satisf, int p) {
//     if (p == ex.nr_op) {
//         return verif(ex, satisf);
//     }

//     *(satisf + p) = 1;
//     if (bkt(ex, satisf, p + 1)) {
//         return 1;
//     }

//     *(satisf + p) = -1;
//     if (bkt(ex, satisf, p + 1)) {
//         return 1;
//     }
//     return 0;
// }

void afisare(expresie ex, int solv, int *satisf) {
    if (solv) {
        printf("s SATISFIABLE\nv ");
        for (int i = 0; i < ex.nr_op; i++) {
            if (*(satisf + i) == -1) {
                printf("%d ", -(i + 1));
            } else {
                printf("%d ", (i + 1));
            }
        }
        printf("0\n");
    } else {
        printf("s UNSATISFIABLE\n");
    }
}