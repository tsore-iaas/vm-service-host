#!/bin/bash

# Valeurs par défaut
DEFAULT_BRIDGE="br0"

# Vérification des arguments
if [ "$#" -ne 1 ] && [ "$#" -ne 2 ]; then
    echo "Usage: $0 <nom_interface_tap> [nom_pont]"
    echo "Example: $0 tap0 [br0]"
    echo "Note: Si le nom du pont n'est pas spécifié, br0 sera utilisé par défaut"
    exit 1
fi

# Vérification des privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "Ce script doit être exécuté en tant que root"
    exit 1
fi

TAP_NAME="$1"
BRIDGE_NAME="${2:-$DEFAULT_BRIDGE}"

# Vérification de l'existence du pont
if ! ip link show "$BRIDGE_NAME" &> /dev/null; then
    echo "Erreur: Le pont $BRIDGE_NAME n'existe pas"
    exit 1
fi

# Vérification de l'existence de l'interface tap
if ! ip link show "$TAP_NAME" &> /dev/null; then
    echo "Erreur: L'interface tap $TAP_NAME n'existe pas"
    exit 1
fi

echo "Désactivation de l'interface tap..."
ip link set "$TAP_NAME" down

echo "Retrait de l'interface tap du pont $BRIDGE_NAME..."
ip link set "$TAP_NAME" nomaster

echo "Suppression de l'interface tap..."
ip link delete "$TAP_NAME"

echo "Configuration terminée !"
echo "L'interface $TAP_NAME a été supprimée et dissociée du pont $BRIDGE_NAME"