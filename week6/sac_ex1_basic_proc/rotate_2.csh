#! /bin/csh -f

set files = `ls 2*sac | grep "HH[N,E]"`

foreach file ($files)
echo $file
set nf = $file".copy"
cp $file $nf

set ew = `echo $nf | grep "HHE" | wc -l`
echo $ew
if ($ew == 1) sacset -cmpaz=90 -cmpinc=90 $nf
if ($ew != 1) sacset -cmpaz=0 -cmpinc=90 $nf

end

set nfiles = `ls 2*sac* | grep "HH[N,E]" | grep ".copy"`

sac rotate.m FILES $nfiles
