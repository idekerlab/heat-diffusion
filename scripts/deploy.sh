echo $PWD
docker run -d --name heat-diffusion --expose 8080 ericsage/heat-diffusion-service
docker run -d --name cxmate -v $(pwd):/cxmate -p 80:80 cxmate/cxmate
