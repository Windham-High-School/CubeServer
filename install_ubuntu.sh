#!/usr/bin/bash
# Installation script for CubeServer
# Created 10-10-22 by Joseph R. Freeston
#

# Constants
SOFTWARE_NAME="CubeServer"
INTERACTIVE_BACKTITLE="${SOFTWARE_NAME} Installation Script by Joseph R. Freeston"


# Update:
sudo apt-get update

# Check if interactive shell:
INTERACTIVE=0
[[ $- == *i* ]] && INTERACTIVE=1 && sudo apt-get install dialog


pipe_output () {
    [[ $INTERACTIVE -ne 0 ]] && dialog --backtitle "${INTERACTIVE_BACKTITLE}" --title "$1" --progressbox 15 75 || cat
}

message () {
    [[ $INTERACTIVE -ne 0 ]] && dialog --backtitle "${INTERACTIVE_BACKTITLE}" --title "$1" --infobox "$2" 15 75 || echo -e "$1\n$2"
}


# Install Docker and Docker-Compose
sudo apt-get -y install curl gnupg ca-certificates lsb-release | pipe_output "Installing PGP Cert Tools"
sudo mkdir -p /etc/apt/keyrings
echo "Downloading keyring..." && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update | pipe_output "Updating Package Lists"
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose | pipe_output "Installing Docker"

docker-compose build --no-cache | pipe_output "Building With Docker-Compose"

# Create system service
message "Installing" "Creating Systemd Service..."
cat > /etc/systemd/system/cubeserver.service << EOF
[Unit]
Description=${SOFTWARE_NAME} WebApp, API, Backend, etc.
PartOf=docker.service
After=docker.service

[Service]
Restart=always
User=root
Group=docker
WorkingDirectory=$(pwd)
# Shutdown container (if running) when unit is started
ExecStartPre=$(which docker-compose) -f docker-compose.yml down
# Start container when unit is started
ExecStart=$(which docker-compose) -f docker-compose.yml up
# Stop container when unit is stopped
ExecStop=$(which docker-compose) -f docker-compose.yml down

[Install]
WantedBy=multi-user.target
EOF

message "Installing" "Enabling & Starting Systemd Service..."
sudo systemctl enable cubeserver.service
sudo systemctl start cubeserver.service

message "Finished!" "The ${SOFTWARE_NAME} installation is complete!\nThe server should be started and should start itself on boot."
