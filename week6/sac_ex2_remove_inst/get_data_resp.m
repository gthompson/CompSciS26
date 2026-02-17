* get_data.m -- SAC macro: getting data from IRIS
* main commands: event to find events, e.g., event time 2025-12-21T17:00:00 2025-12-21T18:00:00 region -120 -110 40 50
*                station to find stations or networks
*                data to get data, e.g., data sta IRMR cha HH? usgs:us6000rwcj duration +30m -- gives list
*                                        data sta IRMR cha HH? usgs:us6000rwcj duration +30m sac -- download in SAC adds EV metadata
*                                        data sta IRMR cha HH? usgs:us6000rwcj duration +30m mseed
*                                        data sta IRMR cha HH? usgs:us6000rwcj duration +30m read -- loads data in sac
*
*                                        data sta IRMR cha HH? usgs:us6000rwcj time 2025-12-21T16:59:01 2025-12-21T17:05:01 read
* same:
*                                        data sta IRMR cha HH? time 2025-12-21T16:59:01 2025-12-21T17:05:01 read
*                                        metadata usgs:us6000rwcj
*
* response:
* read WW.IRMR.00.HHZ.M.2025.355.165901.sac * file already downloaded, now find response that goes with it:
* response sacpz
* or
* response evalresp
*
* Usage (from bash): sac get_data.m

* 
event time 2025-12-21T17:00:00 2025-12-21T17:30:00 region -120 -110 40 50

*
station network WW channel HH? time 2025-12-21T17:00:00 1day

*
data sta IRMR cha HH? usgs:us6000rwcj time 2025-12-21T16:59:01 2025-12-21T17:05:01 sac

* ---- user settings ----
setbb INPUT_GLOB "*.sac"

*
do FILE list %INPUT_GLOB%
read $FILE
plot
response sacpz
response evalresp
enddo

