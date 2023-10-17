containername="ghrb_framework"

docker ps -aq --filter "name=$containername" | grep -q . && docker stop $containername && docker rm $containername
docker run -dt --name $containername -v $(pwd):/root/framework ghrb_framework:latest
docker exec -it $containername /bin/bash