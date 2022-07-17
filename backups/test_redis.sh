for N in $(seq 1 1000); do echo "SADD test $N"; done > data.txt
cat data.txt | sh redis-pipe.sh | redis-cli --pipe
echo "SCARD test" | redis-cli