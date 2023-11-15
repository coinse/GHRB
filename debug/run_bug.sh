cd /root/framework
for PID in $(./cli.py pid -q); do
    for BID in $(cut -f1 -d',' "/root/framework/commit_db/${PID}_bugs.csv"); do
    
    if [ $BID == "bug_id" ]
        then
            continue
    fi

    if [[ ! $PID == "checkstyle" ]]
        then
            continue
    fi
    
    if [ $PID == "javaparser" ]
        then
            continue
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
done