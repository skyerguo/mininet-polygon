## 清除后台指令
ps -ef | grep "/proj/quic-PG0/data/server.crt" | grep -v grep | awk '{print $3}' | xargs sudo kill -9 > /dev/null 2>&1
ps -ef | grep "/proj/quic-PG0/data/server.crt" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
ps -ef | grep "/proj/quic-PG0/data/client" | grep -v grep | awk '{print $3}' | xargs sudo kill -9 > /dev/null 2>&1
ps -ef | grep "/proj/quic-PG0/data/client" | grep -v grep | awk '{print $2}' | xargs sudo kill -9 > /dev/null 2>&1
