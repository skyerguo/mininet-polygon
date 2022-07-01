plt_times=`grep "PLT:" /proj/quic-PG0/data/result-logs/client/2022-06-30_22:51:00/2/2_14447_1656601128021_2.txt | wc -l` ## plt出现的次数
# echo "plt_times: " $plt_times >> ${output_file}_2.txt

if [[ $plt_times != 2 ]] ## 失败的请求
then
    echo 1111
    sleep 5  
fi 
echo 22222