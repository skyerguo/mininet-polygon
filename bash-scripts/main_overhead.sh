sleep 10
sudo mn -c && cd ~/mininet-polygon/py-scripts && sudo timeout 1000 python3 main.py Polygon
sleep 60
sudo mn -c && sed -i 's/FAKE_SERVER_NUMBER = 100/FAKE_SERVER_NUMBER = 1000/g' /users/myzhou/mininet-polygon/py-scripts/main.py && cd ~/mininet-polygon/py-scripts && sudo timeout 1000 python3 main.py Polygon
sleep 60
sudo mn -c && sed -i 's/FAKE_SERVER_NUMBER = 1000/FAKE_SERVER_NUMBER = 10000/g' /users/myzhou/mininet-polygon/py-scripts/main.py && cd ~/mininet-polygon/py-scripts && sudo timeout 1000 python3 main.py Polygon
sleep 60
sudo mn -c && sed -i 's/FAKE_SERVER_NUMBER = 10000/FAKE_SERVER_NUMBER = 20000/g' /users/myzhou/mininet-polygon/py-scripts/main.py && cd ~/mininet-polygon/py-scripts && sudo timeout 1000 python3 main.py Polygon
sleep 60
sudo mn -c && sed -i 's/FAKE_SERVER_NUMBER = 20000/FAKE_SERVER_NUMBER = 120000/g' /users/myzhou/mininet-polygon/py-scripts/main.py && cd ~/mininet-polygon/py-scripts && sudo timeout 1000 python3 main.py Polygon
sleep 60
