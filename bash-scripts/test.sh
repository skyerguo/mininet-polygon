cat "/data/measurement_log/2022-03-02_14:16:43/competitiveness/competitiveness.txt"
bw_set=`sed -n '1,1p' /data/measurement_log/2022-03-02_14:16:43/competitiveness/competitiveness.txt`
echo $bw_set
dispatcher_bw=(`echo $bw_set`)
echo ${dispatcher_bw[*]}

for i in `seq 0 $((${#dispatcher_bw[*]} - 1))`
do
    echo ${dispatcher_bw[i]}
    # bw_competitiveness[i]=`awk 'BEGIN{print "'${dispatcher_bw[i]}'" / "'$max_dispatcher_bw'"}'`
done