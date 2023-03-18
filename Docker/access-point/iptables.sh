#/usr/bin/env bash
# see https://fwhibbit.es/en/automatic-access-point-with-docker-and-raspberry-pi-zero-w
#iptables-nft -t nat -C POSTROUTING -o ${INTERFACE_API} -j MASQUERADE || iptables-nft -t nat -A POSTROUTING -o ${INTERFACE_API} -j MASQUERADE
iptables-nft -C FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -p TCP --dport ${API_PORT} -j ACCEPT || iptables-nft -A FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -p TCP --dport ${API_PORT} -j ACCEPT
iptables-nft -C FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -p TCP --dport ${API_PORT} -j ACCEPT || iptables-nft -A FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -p TCP --dport ${API_PORT} -j ACCEPT
