## Checkout the api code
  * cd code
  * git clone https://github.com/Windham-High-School/CubeServer.git
 
## Set things up
  * cd code/CubeServer
  * ./generate_certs.sh
  * vi .env
    * set MONGODB_HOSTNAME
    * set MONGODB_PASSWORD

## Have the raspberry pi restart nightly
  * sudo crontab -e
  * 15 6 * * * reboot

# To just run the api server

## Start so that it will restart on device restart
  * docker compose --profile api up -d

## Create Crontab
  * crontab -e
  */5 * * * * cd code/CubeServer && bash deploy.sh api 2> /home/admin/error.txt`

# To run a full system

## Start so that it will restart on device restart
  * docker compose --profile full up -d

## Create Crontab
  * crontab -e
  */5 * * * * cd code/CubeServer && bash deploy.sh full 2> /home/admin/error.txt`

