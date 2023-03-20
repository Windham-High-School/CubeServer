# Un-Routing the subnets togeeeeeeether:
iptables-nft -t nat -D POSTROUTING -s ${DHCP_SUBNET}/24 -j MASQUERADE

# Un-Accept outgoing traffic only as responses:
iptables-nft -D FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} \
             -m state --state RELATED,ESTABLISHED \
             -j ACCEPT #-p TCP --dport ${API_PORT} -j ACCEPT
# Un-Accept incoming traffic for DHCP:
iptables-nft -D FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} \
             -p udp --dport 67:68 --sport 67:68 \
             -j ACCEPT
# Un-Accept incoming traffic to API:
iptables-nft -D FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} \
             -p TCP --dport ${API_PORT} \
             -j ACCEPT
