for vardir in */
do
    echo $vardir
    mkdir ${vardir}fvs
    mkdir ${vardir}rx
    mv ${vardir}*_FVS/* ${vardir}fvs
    mv ${vardir}*_STD/ ${vardir}fvs
    rmdir ${vardir}*_FVS/
    rmdir ${vardir}*_STD/
done
