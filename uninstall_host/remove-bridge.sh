#!/bin/bash

# Vérification des arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <interface_physique> <nom_pont>"
    echo "Example: $0 eth0 br0"
    exit 1
fi

# Vérification des privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "Ce script doit être exécuté en tant que root"
    exit 1
fi

INTERFACE="$1"
BRIDGE_NAME="$2"

# Suppression de la règle de pare-feu
iptables --delete FORWARD --in-interface "$BRIDGE_NAME" -j ACCEPT
sudo iptables -t nat -D POSTROUTING -o "$BRIDGE_NAME" -j MASQUERADE

# Désactivation du routage IP
sysctl -w net.ipv4.ip_forward=0

# Arrêt et suppression du pont
ip link set "$BRIDGE_NAME" down
ip link delete "$BRIDGE_NAME"

# Réinitialisation de l'interface
ip link set "$INTERFACE" nomaster
ip addr flush dev "$INTERFACE"

# Suppression des paquets installés
#apt autoremove -y bridge-utils

echo "Réinitialisation terminée !"
echo "Le pont $BRIDGE_NAME a été supprimé et l'interface $INTERFACE a été réinitialisée"