* rotate seismograms -- SAC macro
*
* read 2025.355.16.59.01.0000.WW.IRMR.00.HHN.sac 2025.355.16.59.01.0000.WW.IRMR.00.HHE.sac
$KEYS FILES
read $FILES

lh

rotate to gcp

plot1
pause period off

read more $FILES
p1
pause

ppk

q
