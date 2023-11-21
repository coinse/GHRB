containername=$1

if [ -z "$containername" ]; then
    containername="ghrb_framework"
fi

docker ps -aq --filter "name=$containername" | grep -q . && docker stop $containername && docker rm $containername
docker run -dt --name $containername -v $(pwd):/root/framework ghrb_framework:latest
docker exec -it $containername /bin/bash
