FROM alpine

# Install required packages:
RUN apk update && apk add hostapd iw dhcp iptables gettext moreutils dnsmasq

# Configure Hostapd for open ap
ADD Docker/access-point/hostapd.conf /etc/hostapd/hostapd.conf

# Configure DHCPD
ADD Docker/access-point/dhcpd.conf /etc/dhcp/dhcpd.conf
RUN touch /var/lib/dhcp/dhcpd.leases

# Configure DNS server:
ADD Docker/access-point/dnsmasq.conf /etc/dnsmasq.conf

# Configure networking
ADD Docker/access-point/interfaces /etc/network/interfaces
ADD Docker/access-point/iptables.sh /iptables.sh
ADD Docker/access-point/iptables_off.sh /iptables_off.sh

# Entrypoint
ADD Docker/access-point/start.sh /start.sh
ADD Docker/access-point/entrypoint.sh /entrypoint.sh
ENTRYPOINT /bin/sh /entrypoint.sh
