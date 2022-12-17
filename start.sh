cd compute || exit
sh routine.sh

cd backend_api || exit
sudo docker build . -t backend_api
sudo docker run -p 3000:3000 -v "$PWD/public:/home/node/app/public" -d backend_api

cd ../frontend || exit
sudo docker build . -t frontend
sudo docker run -p 3001:3001 -d frontend
