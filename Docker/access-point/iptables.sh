#/usr/bin/env bash
# see https://fwhibbit.es/en/automatic-access-point-with-docker-and-raspberry-pi-zero-w

# Routing the subnets togeeeeeeether:
iptables-nft -t nat -A POSTROUTING -s ${DHCP_SUBNET}/24 -j MASQUERADE

# Accept outgoing traffic only as responses:
iptables-nft -A FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} \
             -m state --state RELATED,ESTABLISHED \
             -j ACCEPT #-p TCP --dport ${API_PORT} -j ACCEPT
# Accept incoming traffic for DHCP:
iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} \
             -p udp --dport 67:68 --sport 67:68 \
             -j ACCEPT
# Accept incoming traffic to API:
iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} \
             -p TCP --dport ${API_PORT} \
             -j ACCEPT

#iptables-nft -t nat -C POSTROUTING -o ${INTERFACE_API} -j MASQUERADE || iptables-nft -t nat -A POSTROUTING -o ${INTERFACE_API} -j MASQUERADE
#iptables-nft -C FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -p TCP --dport ${API_PORT} -j ACCEPT || iptables-nft -A FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -p TCP --dport ${API_PORT} -j ACCEPT
#iptables-nft -C FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -p TCP --dport ${API_PORT} -j ACCEPT || iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -p TCP --dport ${API_PORT} -j ACCEPT
