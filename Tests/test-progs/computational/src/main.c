/**
 * main.c
 * Computational program which computes the fibonacci sequence
 */

#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    unsigned int N = 1000000000;

    if (argc > 1)
    {
        int temp_N = atoi(argv[1]);

        if (temp_N > 2)
        {
            N = temp_N;
        }
    }

    unsigned long int X_2 = 1;
    unsigned long int X_1 = 1;
    unsigned long int X;
    unsigned int i = 2;

    while (i++ < N)
    {
        X = X_2 + X_1;
        X_2 = X_1;
        X_1 = X;
    }

    printf("%u - %lu\n", i - 1, X);
    
    return 0;
}
