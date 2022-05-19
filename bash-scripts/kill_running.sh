# sudo mn -c
# ps -ef | grep "/proj/quic-PG0/data/client" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/proj/quic-PG0/data/client" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/proj/quic-PG0/data/start_polygon.sh" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/proj/quic-PG0/data/start_anycast.sh" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1

# ps -ef | grep "/proj/quic-PG0/data/server.crt" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "/proj/quic-PG0/data/server.crt" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "sleep" | grep -v grep | awk '{print $3}' | xargs sudo kill -9 > /dev/null 2>&1
# ps -ef | grep "sleep" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1

ps -ef | grep "dns.py" | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty sudo kill -9 > /dev/null
ps -ef | grep "record_cpu" | grep -v grep | awk '{print $2}' | xargs --no-run-if-empty sudo kill -9 > /dev/null
# ps -ef | grep "nload" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null