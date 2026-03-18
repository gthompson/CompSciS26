* process.m -- SAC macro: basic preprocessing + bandpass + write outputs
* Usage (from bash): sac process.m
*
* Edit these variables:
*   - INPUT_GLOB: which files to process
*   - FREQMIN/FREQMAX: bandpass corners
*
echo on
wild echo off

* ---- user settings ----
setbb INPUT_GLOB "*.SAC"
setbb FREQMIN "1"
setbb FREQMAX "10"

* ---- read and process ----
r %INPUT_GLOB%
rmean
rtr
taper

* 4-pole, zero-phase bandpass (p 2)
bp c %FREQMIN% %FREQMAX% n 4 p 2

* overwrite inputs (change to "w append .bp" if you prefer new files)
w over

q
