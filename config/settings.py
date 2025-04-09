import os

#Master configuration
MASTER_IP = os.environ.get('MASTER_IP', '192.168.8.163')
MASTER_PORT = os.environ.get('MASTER_PORT', '8000')

#Host Configuration
HOST_IP = os.environ.get('HOST_IP', '192.168.8.163')
LOCATION = os.environ.get('LOCATION', 'Cameroun')


#Network Configuration
HOST_INTERFACE_NAME = os.environ.get('HOST_INTERFACE_NAME', 'eno1') # Nom de l'interface réseau sur l'hôte pour permettre au VM d'accéder au réseau

#VM Configuration
TMP_DIR = "/tmp/firecracker_sockets"
BASE_DIR = "/tmp/vms"
SOCKET_PREFIX = "firecracker"
BRIDGE_NAME = "br0"
GATEWAY_ADDRESS = os.environ.get('GATEWAY_ADDRESS', '192.168.8.1')

SCRIPTS_FOLDER = "app/scripts/"
