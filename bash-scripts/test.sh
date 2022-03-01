nload_path='/data/measurement_log/2022-02-28_11:03:00/nload/'
server_id=1
for file_name in `ls ${nload_path}*$server_id.txt`
do
    # echo $file_name
    new_file_name=${file_name//txt}"log"
    # cat -A $file_name | grep "Curr: "
    sed -e "s/\x1b\[[?]*[0-9]*[a-zA-Z]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b([a-zA-Z]//g; s/\x1b=//g; s//\r\n/g;"  $file_name > $new_file_name
done
