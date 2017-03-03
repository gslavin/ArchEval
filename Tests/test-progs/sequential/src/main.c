/**
 * main.c
 * Program which computes the sum of random elements of a matrix.
 */

#include <stdlib.h>
#include <stdio.h>

static unsigned int X[1024][1024];

int main(int argc, char **argv)
{
    unsigned int N = 1000000000;

    if (argc > 1)
    {
        int temp_N = atoi(argv[1]);

        if (temp_N > 0)
        {
            N = temp_N;
        }
    }

    unsigned int sum = 0;
    unsigned int i = 0;

    while (i++ < N)
    {
        sum += X[0][i % 1048576];
    }

    printf("%u\n", sum);
    
    return 0;
}
