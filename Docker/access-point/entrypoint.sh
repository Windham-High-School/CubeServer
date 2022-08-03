#!/bin/sh
# Start up the access point container!

# Substitute some environment vars into the configuration:
echo "Substituting env vars into config:"
echo "hostapd.conf:"
cat /etc/hostapd/hostapd.conf
envsubst </etc/hostapd/hostapd.conf | sponge /etc/hostapd/hostapd.conf
echo "dhcpd.conf:"
cat /etc/dhcp/dhcpd.conf
envsubst </etc/dhcp/dhcpd.conf | sponge /etc/dhcp/dhcpd.conf
echo "interfaces:"
cat /etc/network/interfaces
envsubst </etc/network/interfaces | sponge /etc/network/interfaces

# Move forward to execute the start script...
/bin/sh /start.sh
