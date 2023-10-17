# GHRB_framework
```
cd Docker
docker build -t ghrb_framework .
```

For AMD64:

```
sh run_docker_container.sh
```

Inside the docker:

```
cd /root/framework
chmod +x cli.py

cd debug
python collector.py
cd ..
```

Check whether cli.py runs correctly  
`./cli.py -h`  

All directory paths given to the tool need to be absolute paths within the container.

Example:  

```
./cli.py checkout -p gson -v 1b -w /root/framework/testing
./cli.py compile -w /root/framework/testing
./cli.py test -w /root/framework/testing
```

