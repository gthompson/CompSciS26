import math

n = 10_000_000
signal = [0.0] * n  # allocate list

# Fill signal
for i in range(n):
    signal[i] = math.sin(0.001 * (i + 1))

# Compute RMS
sumsq = 0.0
for x in signal:
    sumsq += x * x

rms = math.sqrt(sumsq / n)

print("Samples:", n)
print("RMS amplitude:", rms)