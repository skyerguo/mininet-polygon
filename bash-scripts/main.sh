cp ~/mininet-polygon/json-files/topo_large.json ~/mininet-polygon/json-files/topo.json
for i in `seq 5`
do
    sleep 10
    cd ~/mininet-polygon/py-scripts && sudo timeout 7000 python3 main.py Polygon
    sleep 60
    cd ~/mininet-polygon/py-scripts && sudo timeout 7000 python3 main.py Anycast
    sleep 60
    cd ~/mininet-polygon/py-scripts && sudo timeout 7000 python3 main.py FastRoute
    sleep 60
    new_thread=$(($i+1))
    echo "i: " $i
    sed -i 's/"client_thread": '$i'/"client_thread": '$new_thread'/g' ~/mininet-polygon/json-files/topo.json
done