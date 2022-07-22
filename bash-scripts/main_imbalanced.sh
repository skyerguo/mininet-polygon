cp ~/mininet-polygon/json-files/topo_imbalanced_case1.json ~/mininet-polygon/json-files/topo.json
sleep 10
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py Polygon
sleep 60
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py Anycast
sleep 60
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py FastRoute
sleep 60

cp ~/mininet-polygon/json-files/topo_imbalanced_case2.json ~/mininet-polygon/json-files/topo.json
sleep 10
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py Polygon
sleep 60
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py Anycast
sleep 60
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py FastRoute
sleep 60

sudo mn -c

# cp ~/mininet-polygon/json-files/topo_imbalanced_case3.json ~/mininet-polygon/json-files/topo.json
# sleep 10
# sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py Polygon
# sleep 60
# sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py Anycast
# sleep 60
# sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 5000 python3 main.py FastRoute
# sleep 60

# sudo mn -c