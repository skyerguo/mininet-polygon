# sudo mn -c
# ps -ef | grep "/run/user/20001/data/client" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/run/user/20001/data/client" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/run/user/20001/data/start_polygon.sh" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/run/user/20001/data/start_anycast.sh" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1

# ps -ef | grep "/run/user/20001/data/server.crt" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/run/user/20001/data/server.crt" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "sleep" | grep -v grep | awk '{print $3}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "sleep" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1

ps -ef | grep "dns.py" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1