for i in `seq 15`
do
    data_order=$(($i-1))
    cd ~/mininet-polygon/py-scripts && sudo python3 analysis_data.py $data_order ~/mininet-polygon/analysis_results/$data_order.txt
done