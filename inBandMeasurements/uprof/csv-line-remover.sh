#!/bin/bash
if find . -type d -name 'AMDuProf-SWP-Timechart_*' -print -quit | grep -q 'AMDuProf-SWP-Timechart_'; then
    directory=$(find . -type d -name 'AMDuProf-SWP-Timechart_*' -print -quit)

    cd "$directory"
    
    sed -i '1,15d' timechart.csv
    mv timechart.csv ../..
    cd ..
    find . -type d -name 'AMDuProf-SWP-Timechart_*' -exec rm -rf {} +
    
else
    echo "not found"
fi




#  /opt/AMDuProf_4.2-850/bin/AMDuProfCLI  timechart --interval 100 --duration 10 --event socket=0,power -o ./amdInfo 
