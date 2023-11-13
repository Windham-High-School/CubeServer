## Checkout the api code
  * cd code
  * git clone https://github.com/Windham-High-School/CubeServer.git
 
## Set things up
  * cd code/CubeServer
  * ./generate_certs.sh
  * vi .env
    * set MONGODB_HOSTNAME
    * set MONGODB_PASSWORD

## Start so that it will restart on device restart
  * docker compose up -d
