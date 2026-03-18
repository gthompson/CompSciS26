* remove the instrument response ...
*
* use either the RESP or the SAC_PZ file
*
SETBB RESP "RESP.WW.IRMR.00.HHZ"
read WW.IRMR.00.HHZ.M.2025.355.165901.sac ; rmean ; rtrend ; taper 
TRANSFER FROM EVALRESP FNAME %resp TO NONE FREQLIM 0.05 0.1 1 4
plot
pause period off
write append .respf

* same ... assumes resp file name
read WW.IRMR.00.HHZ.M.2025.355.165901.sac ; rmean ; rtrend ; taper
TRANS FROM EVALRESP TO NONE freq 0.05 0.1 1 4
plot
pause
write append .resp

* or with SAC-PZ file ... -- if none given checks for "SAC_PZs_NETWORK_STATION_CHANNEL_LOCID_*"
setbb pzfile "SAC_PZs_WW_IRMR_00_HHZ_2025-12-21T16:59:01_2025-12-21T17:05:00"
read WW.IRMR.00.HHZ.M.2025.355.165901.sac ; rmean ; rtrend ; taper
TRANS FROM POLEZERO S %pzfile TO NONE FREQ 0.05 0.1 1 4
* transfer from m to nm
* The MUL 1.0e9 command converts the displacement output from the POLEZERO meters to the SAC default of nanometers.
mul 1.0e9
plot
pause
write append .sacpz

* simply plot all three versions together:
read WW.IRMR.00.HHZ.M.2025.355.165901.sac.*
color on increment
line increment on
xlim b 112 136 ; p1
pause

p2
pause

* or simply integrating the raw data (for something similar looking)
read WW.IRMR.00.HHZ.M.2025.355.165901.sac ; rmean ; rtrend ; taper ; int ; bp bu c .09 2. np 2 p 2 ; p
pause
* Sensitivity:                           +3.01720E+08
setbb sens "+3.01720E+08"
div %sens%
* bring back to nm
mul 1E+09

read more WW.IRMR.00.HHZ.M.2025.355.165901.sac.*
p1
pause

p2
pause
quit
