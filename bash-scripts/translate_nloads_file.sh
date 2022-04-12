while getopts ":o:n:" opt
do
    case $opt in
        o)
            old_file_path=$OPTARG
        ;;
        n)
            new_file_path=$OPTARG
        ;;
    esac
done

sed -e "s/\x1b\[[?]*[0-9]*[a-zA-Z]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b\[[?]*[0-9]*\;[0-9]*\;[0-9]*[a-zA-Z=]//g; s/\x1b([a-zA-Z]//g; s/\x1b=//g; s//\r\n/g;" $old_file_path > $new_file_path
