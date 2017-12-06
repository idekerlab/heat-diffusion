echo $PWD
docker network create hd
docker run -d --name diffusion --expose 8080 --net hd ericsage/heat-diffusion-service
docker run -d --name cxmate -v $(pwd):/cxmate -p 80:80 --net hd cxmate/cxmate
