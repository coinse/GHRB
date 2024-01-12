cd /root/framework

BUGS="
jsoup-5
nacos-6
jackson-databind-4
rocketmq-13
rocketmq-14
rocketmq-15
rocketmq-16
rocketmq-17
rocketmq-18
"

for BUG in $BUGS; do
    BUG_SPLIT=($(echo $BUG | tr "-" "\n"))
    PID=${BUG_SPLIT[0]}
    BID=${BUG_SPLIT[1]}

    if [ "$PID" = "jackson" ] ; then
        PID+=${BUG_SPLIT[1]}
        BID=${BUG_SPLIT[2]}
    fi


    rm -rf testing
    ./cli.py checkout -p $PID -v "${BID}"b -w /root/framework/testing
    ./cli.py compile -w /root/framework/testing
    echo "${PID}_${BID}" >> /root/framework/buggy.txt
    ./cli.py test -w /root/framework/testing -q >> /root/framework/buggy.txt
    
    rm -rf testing
    ./cli.py checkout -p $PID -v "${BID}"f -w /root/framework/testing
    ./cli.py compile -w /root/framework/testing
    echo "${PID}_${BID}" >> /root/framework/fixed.txt
    ./cli.py test -w /root/framework/testing -q >> /root/framework/fixed.txt
done
