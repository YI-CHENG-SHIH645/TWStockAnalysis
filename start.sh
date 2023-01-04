cd compute || exit
sh routine.sh

cd ../backend_api || exit
if docker ps --format "{{.Image}}" | grep -q backend_api;  then
  docker stop backend_api
  docker rm backend_api
fi
if ! docker image ls --format "{{.Repository}}" | grep -q backend_api; then
   docker build . -t backend_api
fi
docker run --name backend_api -p 3000:3000 -v "$PWD/public:/home/node/app/public" -d backend_api

cd ../frontend || exit
if docker ps --format "{{.Image}}" | grep -q frontend;  then
  docker stop frontend
  docker rm frontend
fi
if ! docker image ls --format "{{.Repository}}" | grep -q frontend; then
  docker build . -t frontend
fi
docker run --name frontend -p 3001:3001 -d frontend
