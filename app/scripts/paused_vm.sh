#!/bin/bash

# Vérification du nombre de paramètres
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <chemin_vers_le_socket> <etat>"
  echo "Etat : Paused ou Resumed"
  exit 1
fi

# Récupération du chemin vers le socket
SOCKET_PATH=$1

# Récupération de l'état
STATE=$2

# Vérification de l'état
if [ "$STATE" != "Paused" ] && [ "$STATE" != "Resumed" ]; then
  echo "Erreur: L'état doit être Paused ou Resumed"
  exit 1
fi

# Vérification de l'existence du socket
if [ ! -S "$SOCKET_PATH" ]; then
  echo "Erreur: Le socket $SOCKET_PATH n'existe pas"
  exit 1
fi

# Exécution de la commande curl pour interagir avec le socket
curl --unix-socket "$SOCKET_PATH" -i \
  -X PATCH 'http://localhost/vm' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
        \"state\": \"$STATE\"
  }"