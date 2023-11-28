## Checkout the api code
  * cd code
  * git clone https://github.com/Windham-High-School/CubeServer.git
 
## Set things up
  * cd code/CubeServer
  * ./generate_certs.sh
  * vi .env
    * set MONGODB_HOSTNAME
    * set MONGODB_PASSWORD
    * set MONGODB_DRIVER=mongodb # used for local mongodb
    * set MONGODB_OPTIONS=authSource=admin # used for local mongodb

## Have the raspberry pi restart nightly
  * sudo crontab -e
  * 15 6 * * * reboot

## Install a version of MongoDB that works on the Pi 
  * reference: https://github.com/themattman/mongodb-raspberrypi-docker
  * wget https://github.com/themattman/mongodb-raspberrypi-docker/releases/download/r7.0.3-mongodb-raspberrypi-docker-unofficial/mongodb.ce.pi4.r7.0.3-mongodb-raspberrypi-docker-unofficial.tar.gz
  * docker load --input mongodb.ce.pi4.r7.0.3-mongodb-raspberrypi-docker-unofficial.tar.gz 

# To just run the api server

## Start so that it will restart on device restart
  * docker compose --profile api up -d

## Create Crontab
  * crontab -e
  * */5 * * * * cd code/CubeServer && bash deploy.sh api 2> /home/admin/error.txt`

# To run a full system

## Start so that it will restart on device restart
  * docker compose --profile full up -d

## Create Crontab
  * crontab -e
  * */5 * * * * cd code/CubeServer && bash deploy.sh full 2> /home/admin/error.txt`

