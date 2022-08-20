#!/bin/sh
# Start up the access point container!

# Substitute some environment vars into the configuration:
echo "Substituting env vars into config:"
echo "hostapd.conf:"
envsubst </etc/hostapd/hostapd.conf | sponge /etc/hostapd/hostapd.conf
cat /etc/hostapd/hostapd.conf
echo "dhcpd.conf:"
envsubst </etc/dhcp/dhcpd.conf | sponge /etc/dhcp/dhcpd.conf
cat /etc/dhcp/dhcpd.conf
echo "interfaces:"
envsubst </etc/network/interfaces | sponge /etc/network/interfaces
cat /etc/network/interfaces
echo "dnsmasq:"
envsubst </etc/dnsmasq.conf | sponge /etc/dnsmasq.conf
cat /etc/dnsmasq.conf

# Move forward to execute the start script...
/bin/sh /start.sh
