#Master configuration
MASTER_IP = "192.168.1.200"
MASTER_PORT = "8000"

#Host Configuration
HOST_IP = "192.168.1.143"
LOCATION = "Cameroun"

#Network Configuration
HOST_INTERFACE_NAME = "eno1" # Nom de l'interface réseau sur l'hôte pour permettre au VM d'accéder au réseau

#VM Configuration
TMP_DIR = "/tmp/firecracker_sockets"
BASE_DIR = "/tmp/vms"
SOCKET_PREFIX = "firecracker"
BRIDGE_NAME = "br0"
GATEWAY_ADDRESS = "192.168.1.1"

SCRIPTS_FOLDER = "app/scripts/"
