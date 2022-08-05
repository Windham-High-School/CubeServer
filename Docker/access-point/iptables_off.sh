#/usr/bin/env bash
# see https://fwhibbit.es/en/automatic-access-point-with-docker-and-raspberry-pi-zero-w
iptables-nft -t nat -C POSTROUTING -o ${INTERFACE_API} -j MASQUERADE && iptables-nft -t nat -D POSTROUTING -o ${INTERFACE_API} -j MASQUERADE
iptables-nft -C FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -j ACCEPT && iptables-nft -D FORWARD -i ${INTERFACE_API} -o ${AP_INTERFACE} -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables-nft -C FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -j ACCEPT && iptables-nft -D FORWARD -i ${AP_INTERFACE} -o ${INTERFACE_API} -j ACCEPT