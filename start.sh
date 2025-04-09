#!/bin/bash

# Arrêt en cas d'erreur
set -e

# Fonction d'affichage de l'aide
usage() {
    echo "Usage: $0 -m MASTER_IP [-p MASTER_PORT] -l LOCATION"
    echo "  -m MASTER_IP   : Adresse IP du maître (obligatoire)"
    echo "  -p MASTER_PORT : Port du maître (optionnel, défaut : 8080)"
    echo "  -l LOCATION    : Nom du pays ou du lieu (obligatoire)"
    exit 1
}

# Initialisation des variables
MASTER_IP=""
MASTER_PORT="8000"  # Valeur par défaut
LOCATION=""

# Analyse des options en ligne de commande
while getopts ":m:p:l:" opt; do
    case ${opt} in
        m )
            MASTER_IP=$OPTARG
            ;;
        p )
            MASTER_PORT=$OPTARG
            ;;
        l )
            LOCATION=$OPTARG
            ;;
        \? )
            echo "Option invalide : -$OPTARG" >&2
            usage
            ;;
        : )
            echo "L'option -$OPTARG nécessite un argument." >&2
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Vérification des paramètres obligatoires
if [ -z "$MASTER_IP" ] || [ -z "$LOCATION" ]; then
    echo "Les options -m et -l sont obligatoires."
    usage
fi

# Exportation des variables
export MASTER_IP
export MASTER_PORT
export LOCATION

echo "MASTER_IP=$MASTER_IP"
echo "MASTER_PORT=$MASTER_PORT"
echo "LOCATION=$LOCATION"

# Vérification des privilèges root
if [ "$EUID" -ne 0 ]; then
    echo "Ce script doit être exécuté en tant que root"
    exit 1
fi

# Arrêt en cas d'erreur
set -e

# Variables
NODE_EXPORTER_VERSION="1.6.1"
FIRECRACKER_VERSION="1.5.0"

# Détection automatique de l'interface réseau Ethernet principale
echo "Détection de l'interface réseau Ethernet principale..."
HOST_INTERFACE_NAME=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^e' | head -n 1)
if [ -z "$HOST_INTERFACE_NAME" ]; then
    echo "Aucune interface Ethernet détectée. Vérifiez votre configuration réseau."
    exit 1
fi
echo "Interface Ethernet détectée : $HOST_INTERFACE_NAME"

# Détection automatique de l'adresse IP de la passerelle par défaut
echo "Détection de l'adresse IP de la passerelle par défaut..."
GATEWAY_ADDRESS=$(ip route | awk '/default/ {print $3}')
if [ -z "$GATEWAY_ADDRESS" ]; then
    echo "Impossible de détecter la passerelle par défaut. Vérifiez votre configuration réseau."
    exit 1
fi
echo "Passerelle détectée : $GATEWAY_ADDRESS"

# Détection automatique de l'interface Wi-Fi
echo "Détection de l'interface Wi-Fi..."
WIFI_INTERFACE=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^w' | head -n 1)
if [ -z "$WIFI_INTERFACE" ]; then
    echo "Aucune interface Wi-Fi détectée. Vérifiez votre configuration réseau."
    exit 1
fi
echo "Interface Wi-Fi détectée : $WIFI_INTERFACE"

# Récupération de l'adresse IP associée à l'interface Wi-Fi
echo "Récupération de l'adresse IP de l'interface Wi-Fi..."
HOST_IP=$(ip -4 addr show "$WIFI_INTERFACE" | awk '/inet / {print $2}' | cut -d/ -f1)
if [ -z "$HOST_IP" ]; then
    echo "Impossible de récupérer l'adresse IP de l'interface Wi-Fi. Vérifiez que l'interface est correctement configurée et connectée."
    exit 1
fi
echo "Adresse IP de l'interface Wi-Fi : $HOST_IP"

# Exportation des variables pour qu'elles soient disponibles pour les processus enfants
export HOST_INTERFACE_NAME
export GATEWAY_ADDRESS
export HOST_IP

# Mettre à jour le système et installer les dépendances
echo "Mise à jour du système et installation des dépendances..."
#apt-get update && apt-get upgrade -y
apt-get install -y bridge-utils iproute2 iptables python3 python3-venv python3-pip

# Vérifier si node_exporter est déjà installé ou en cours d'exécution
if ps aux | grep -v grep | grep -q node_exporter; then
    echo "node_exporter est déjà installé et en cours d'exécution."
else
    echo "Installation de node_exporter..."
    
    # Créer l'utilisateur si nécessaire
    useradd --no-create-home --shell /bin/false node_exporter || true

    # Télécharger et installer node_exporter
    mkdir tmp
    cd ./tmp
    curl -LO "https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
    tar xvf "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
    cp "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter" /usr/local/bin/
    chown node_exporter:node_exporter /usr/local/bin/node_exporter
    rm -rf "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz" "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64"
    cd ..
    rm -rf ./tmp/
    # Création du service systemd pour node_exporter
    echo "Configuration du service systemd pour node_exporter..."
    cat <<EOF > /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=default.target
EOF

    # Démarrage et activation de node_exporter
    systemctl daemon-reload
    systemctl start node_exporter
    systemctl enable node_exporter

    echo "node_exporter a été installé et démarré."
fi



if ! [ -x "$(command -v firecracker)" ]; then
  echo "Installation de Firecracker..."
  mkdir tmp
  cd ./tmp
  curl -LO "https://github.com/firecracker-microvm/firecracker/releases/download/v${FIRECRACKER_VERSION}/firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz"
  tar xvf "firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz"
  cp release-v${FIRECRACKER_VERSION}-x86_64/firecracker-v${FIRECRACKER_VERSION}-x86_64 /usr/local/bin/firecracker
  chmod +x /usr/local/bin/firecracker
  rm -rf "firecracker-v${FIRECRACKER_VERSION}-x86_64.tgz" release-v${FIRECRACKER_VERSION}-x86_64
  cd ..
  rm -rf ./tmp/
fi

# Création et activation de l'environnement virtuel Python
echo "Création de l'environnement virtuel Python..."
#cd /chemin/vers/votre/projet # Remplacez par le chemin réel de votre projet
python3 -m venv .env
source .env/bin/activate

# Installation des dépendances Python
echo "Installation des dépendances Python..."
pip install -r requirement.txt

# Lancement du projet
echo "Lancement du projet..."
#sudo env "PATH=$PATH"
uvicorn app.main:app --host 0.0.0.0

