# CubeServer-beaconserver
This package contains the code for the beacon server

## Components
- Scheduler
    - Packets are scheduled based on database documents
- Beacon Server
    - An encrypted SSL socket server that accepts incoming socket connections from the beacon
    - According to the scheduler, packets will be given to the beacon for transmission to be sent via the aforementioned socket connection

---------------------------------
## A Note on Maintainability
**To future CubeServer maintainers-**

I acknowledge that the code here is really pretty poorly written due to the rush in which it was originally written.

Please fix it without breaking something.

:)

-Joseph R. Freeston
