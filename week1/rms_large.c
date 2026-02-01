#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(void) {
    const int n = 10000000;  // 10 million samples
    double *signal;
    double sumsq = 0.0;
    double rms;

    // Allocate memory
    signal = (double *)malloc(n * sizeof(double));
    if (signal == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    // Fill signal
    for (int i = 0; i < n; i++) {
        signal[i] = sin(0.001 * (i + 1));
    }

    // Compute RMS
    for (int i = 0; i < n; i++) {
        sumsq += signal[i] * signal[i];
    }

    rms = sqrt(sumsq / n);

    printf("Samples: %d\n", n);
    printf("RMS amplitude: %.6f\n", rms);

    free(signal);
    return 0;
}