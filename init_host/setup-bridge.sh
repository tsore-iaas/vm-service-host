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

# Vérification de l'existence de l'interface
if ! ip link show "$INTERFACE" &> /dev/null; then
    echo "Erreur: L'interface $INTERFACE n'existe pas"
    exit 1
fi

echo "Installation des paquets nécessaires..."
apt update
apt install -y bridge-utils

echo "Création du pont $BRIDGE_NAME..."
ip link add name "$BRIDGE_NAME" type bridge

echo "Ajout de l'interface $INTERFACE au pont..."
ip link set "$INTERFACE" master "$BRIDGE_NAME"

echo "Configuration des interfaces..."
ip addr flush dev "$INTERFACE"
ip link set "$BRIDGE_NAME" up
ip link set "$INTERFACE" up

echo "Demande d'une adresse IP pour le pont..."
#ip addr add 192.168.8.1/24  dev "$BRIDGE_NAME"
dhclient "$BRIDGE_NAME"

echo "Configuration terminée !"
echo "Le pont $BRIDGE_NAME a été créé et configuré avec l'interface $INTERFACE"
