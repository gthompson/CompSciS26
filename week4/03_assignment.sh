#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# run_rms_benchmark.sh
#
# Usage:
#   bash run_rms_benchmark.sh <username> [remote_host] [remote_dir]
#
# Example:
#   bash run_rms_benchmark.sh thompsong
#   bash run_rms_benchmark.sh thompsong newton.rc.usf.edu ~/compsci2026
# ------------------------------------------------------------

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <username> [remote_host] [remote_dir]"
  exit 1
fi

USER_NAME="$1"
REMOTE_HOST="${2:-newton.rc.usf.edu}"
REMOTE_DIR="${3:-~/compsci2026}"

# Local working directory (where files are created)
WORKDIR="$(pwd)"

echo "Local workdir:  $WORKDIR"
echo "Remote target:  ${USER_NAME}@${REMOTE_HOST}:${REMOTE_DIR}"
echo

# ---------- 1) Create source files locally ----------

cat > rms_large.c <<'EOF'
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
EOF

cat > rms_large.f90 <<'EOF'
program rms_large
  implicit none

  integer, parameter :: n = 10000000
  integer :: i
  real(8), allocatable :: signal(:)
  real(8) :: sumsq, rms

  allocate(signal(n))

  ! Fill signal
  do i = 1, n
     signal(i) = sin(0.001d0 * dble(i))
  end do

  ! Compute RMS
  sumsq = 0.0d0
  do i = 1, n
     sumsq = sumsq + signal(i) * signal(i)
  end do

  rms = sqrt(sumsq / dble(n))

  print *, "Samples:", n
  print *, "RMS amplitude:", rms

  deallocate(signal)
end program rms_large
EOF

cat > rms_large.py <<'EOF'
#!/usr/bin/env python3
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
EOF

chmod +x rms_large.py

echo "Created local files:"
ls -l rms_large.c rms_large.f90 rms_large.py
echo

# ---------- 2) Copy to remote via scp ----------
echo "Copying files to remote..."
scp rms_large.c rms_large.f90 rms_large.py "${USER_NAME}@${REMOTE_HOST}:${REMOTE_DIR}/"
echo "Copy complete."
echo

# ---------- 3) SSH: compile + run timed benchmarks ----------
# Use a timestamped results directory on the remote side.
TS="$(date +%Y%m%d_%H%M%S)"
REMOTE_RESULTS_DIR="${REMOTE_DIR}/results_rms_${TS}"

echo "Running remote compile + benchmarks (this can take a bit for Python)..."
ssh "${USER_NAME}@${REMOTE_HOST}" bash -lc "'
set -euo pipefail

mkdir -p ${REMOTE_DIR}
cd ${REMOTE_DIR}

echo \"Remote pwd: \$(pwd)\"
echo \"Files present:\"
ls -l rms_large.*

mkdir -p ${REMOTE_RESULTS_DIR}

# Compile
echo
echo \"Compiling C...\"
gcc -O3 -o rms_large_c rms_large.c -lm

echo \"Compiling Fortran...\"
gfortran -O3 -o rms_large_f rms_large.f90

# Run with /usr/bin/time -v and capture output
run_one () {
  local label=\"\$1\"
  shift
  local outfile=\"${REMOTE_RESULTS_DIR}/\${label}.txt\"
  echo
  echo \"=== Running: \$label ===\"
  echo \"Command: \$*\"
  echo \"Output -> \$outfile\"
  {
    echo \"=== \$label ===\"
    echo \"Host: \$(hostname)\"
    echo \"Date: \$(date)\"
    echo \"Command: \$*\"
    echo
    /usr/bin/time -v \"\$@\"
  } &> \"\$outfile\"
}

run_one c       ./rms_large_c
run_one fortran ./rms_large_f
run_one python  ./rms_large.py

echo
echo \"Done. Results directory:\"
echo \"${REMOTE_RESULTS_DIR}\"
ls -l ${REMOTE_RESULTS_DIR}
'"

echo
echo "All done."
echo "To fetch results back to your laptop, run:"
echo "  scp -r ${USER_NAME}@${REMOTE_HOST}:${REMOTE_RESULTS_DIR} ."
