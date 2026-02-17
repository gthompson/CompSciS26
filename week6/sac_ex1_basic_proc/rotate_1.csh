#! /bin/csh -f

set nf = `ls 2*.HHN.sac`
set ef = `ls 2*.HHE.sac`

sac rotate.m FILES $nf $ef
