#!/bin/sh
# mostly from https://fwhibbit.es/en/automatic-access-point-with-docker-and-raspberry-pi-zero-w

NOCOLOR='\033[0m'
RED='\033[0;31m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'


sigterm_handler () {
  echo -e "${CYAN}[*] Caught SIGTERM/SIGINT!${NOCOLOR}"
  pkill hostapd
  cleanup
  exit 0
}
cleanup () {
  echo -e "${CYAN}[*] Deleting iptables rules...${NOCOLOR}"
  sh /iptables_off.sh || echo -e "${RED}[-] Error deleting iptables rules${NOCOLOR}"
  echo -e "${CYAN}[*] Restarting network interface...${NOCOLOR}"
  ifdown ${AP_INTERFACE}
  ifup ${AP_INTERFACE}
  echo -e "${GREEN}[+] Successfully exited, byebye! ${NOCOLOR}"
}

trap 'sigterm_handler' TERM INT
mkdir -p /run/dhcp/
if [ -f "/run/dhcp/dhcpd.pid" ]; then
  rm /run/dhcp/dhcpd.pid  # Delete PID file in case there is one
  pkill dhcpd
fi
echo -e "${CYAN}[*] Creating routing rules${NOCOLOR}"
sh /iptables.sh || echo -e "${RED}[-] Error creating iptables rules${NOCOLOR}"

echo -e "${CYAN}[*] Starting dhcpd${NOCOLOR}"
dhcpd -4 -f -d ${AP_INTERFACE} &

echo -e "${CYAN}[*] Setting wlan0 settings${NOCOLOR}"
ifdown ${AP_INTERFACE}
ifup ${AP_INTERFACE}

echo -e "${CYAN}[+] Starting hostapd${NOCOLOR}"
hostapd /etc/hostapd/hostapd.conf &
pid=$!
wait $pid

cleanup
