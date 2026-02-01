import numpy as np
import math

n = 10_000_000

# Create vector [1, 2, 3, ..., n] and compute signal
i = np.arange(1, n + 1, dtype=np.float64)
signal = np.sin(0.001 * i)

# Compute RMS
rms = math.sqrt(np.mean(signal ** 2))

print("Samples:", n)
print("RMS amplitude:", rms)