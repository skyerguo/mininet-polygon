sudo LD_LIBRARY_PATH=/data /data/dispatcher --datacenter 1 --user johnson --password johnson lo 0.0.0.0 4433 /data/server.key /data/server.crt --current_dispatcher_name dispatcher0 -q

# sudo LD_LIBRARY_PATH=~/data ~/data/dispatcher --datacenter ${zone} --user johnson --password johnson bridge 0.0.0.0 $port ~/data/server.key ~/data/server.crt -q