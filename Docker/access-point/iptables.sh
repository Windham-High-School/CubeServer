#/usr/bin/env bash
# see https://fwhibbit.es/en/automatic-access-point-with-docker-and-raspberry-pi-zero-w

# Routing rules:
#ip addr flush dev ${AP_INTERFACE}
#ip addr add ${DHCP_ROUTER_ADDR}/24 dev ${INTERFACE}
#ip route add ${DHCP_SUBNET}/24 via 127.0.0.1 dev ${INTERFACE_API}

# Routing the subnets togeeeeeeether:
iptables-nft -t nat -A POSTROUTING -s ${DHCP_SUBNET}/24 -o ${INTERFACE_API} -j MASQUERADE

# Drop by default:
iptables-nft -P FORWARD DROP
iptables-nft -A INPUT -i ${AP_INTERFACE} -j DROP
iptables-nft -A INPUT -i ${INTERFACE_API} -j DROP

# Accept outgoing traffic only as responses:
iptables-nft -A FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} \
             -m state --state RELATED,ESTABLISHED \
             -j ACCEPT

# Accept incoming traffic for DHCP:
iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} \
             -p udp --dport 67:68 --sport 67:68 \
             -j ACCEPT
iptables-nft -A INPUT \
             -p udp --dport 67:68 --sport 67:68 \
             -j ACCEPT

# Accept incoming traffic to API & Beacon Server:
iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} \
             -p TCP --match multiport --dport ${API_PORT},${BEACON_PORT} \
             -j ACCEPT
iptables-nft -A INPUT -i ${INTERFACE_API} \
             -p TCP --match multiport --dport ${API_PORT},${BEACON_PORT} \
             -j ACCEPT

#iptables-nft -t nat -C POSTROUTING -o ${INTERFACE_API} -j MASQUERADE || iptables-nft -t nat -A POSTROUTING -o ${INTERFACE_API} -j MASQUERADE
#iptables-nft -C FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -p TCP --dport ${API_PORT} -j ACCEPT || iptables-nft -A FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -p TCP --dport ${API_PORT} -j ACCEPT
#iptables-nft -C FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -p TCP --dport ${API_PORT} -j ACCEPT || iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -p TCP --dport ${API_PORT} -j ACCEPT
