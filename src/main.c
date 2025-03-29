#include "functions.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        return 0;
    }
    const char *in = argv[1];
    const char *out = argv[2];
    freopen(in, "r", stdin);
    freopen(out, "w", stdout);

    expresie ex = citire();
    int *satisf = calloc(ex.nr_op, sizeof(int));

    int solv = bkt(ex, satisf, 0);
    afisare(ex, solv, satisf);

    free(satisf);
    
    return 0;
}