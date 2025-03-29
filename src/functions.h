#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct date {
    int *operatori;
} date;

typedef struct expresie {
    date *paranteze;
    int nr_p; // nr paranteze
    int nr_op; // nr operatori
} expresie;

int next_numar (char **string);
expresie citire();
int verif_paranteza(date *paranteza, int *satisf, int nr_op);
int verif(expresie ex,int *satisf);
int unit_propag(expresie ex, int *satisf);
int bkt(expresie ex, int *satisf, int p);
void afisare(expresie ex, int solv, int *satisf);