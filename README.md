# VM Service Host

Ce service est destiné à être installé sur les hôtes qui vont héberger les machines virtuelles (VMs). Il permet de définir les endpoints vers les hôtes et de configurer divers éléments essentiels pour le bon fonctionnement des microVMs.

## Prérequis

Avant de lancer ce service, assurez-vous que votre machine répond aux exigences suivantes.

### 1. Vérifier la compatibilité avec Firecracker

Assurez-vous que votre machine prend en charge la virtualisation matérielle en exécutant la commande suivante :

```sh
[ -r /dev/kvm ] && [ -w /dev/kvm ] && echo "OK" || echo "FAIL"
```

- Si la commande retourne `OK`, votre machine est compatible.
- Si elle retourne `FAIL`, la virtualisation matérielle n'est pas activée ou votre machine ne la prend pas en charge.

### 2. Installer Firecracker

Installez Firecracker dans `/usr/bin` en exécutant les commandes suivantes :

```sh
ARCH="$(uname -m)"
RELEASE_URL="https://github.com/firecracker-microvm/firecracker/releases"
LATEST=$(basename $(curl -fsSLI -o /dev/null -w %{url_effective} ${RELEASE_URL}/latest))

curl -L ${RELEASE_URL}/download/${LATEST}/firecracker-${LATEST}-${ARCH}.tgz | tar -xz
mv release-${LATEST}-$(uname -m)/firecracker-${LATEST}-${ARCH} /usr/bin/firecracker
```

Vérifiez ensuite l'installation avec :

```sh
firecracker --version
```

### 3. Installer et configurer le bridge réseau

Un bridge réseau est nécessaire pour permettre aux VMs de communiquer avec le réseau hôte. Utilisez le script d'installation inclus :

```sh
sudo ./init_host/setup-bridge.sh <interface_physique> <nom_pont>
```

Exemple :

```sh
sudo ./init_host/setup-bridge.sh eth0 br0
```

Ce script crée un pont réseau utilisable par les VMs.

### 4. Créer un environnement virtuel Python et installer les dépendances

Ce projet utilise un environnement Python virtuel pour isoler les dépendances. Exécutez les commandes suivantes :

```sh
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

### 5. Configuration et exécution du service

Avant de lancer le programme, assurez-vous de définir les variables suivantes dans `app/main.py` :

- **BRIDGE_NAME** : Nom du pont réseau défini lors de l'installation.
- **GATEWAY_ADDRESS** : Adresse de la passerelle.

Lancez ensuite le programme en mode root :

```sh
cd app
sudo env "PATH=$PATH" uvicorn app.main:app
```

https://cloud-images.ubuntu.com/minimal/daily/noble/current/noble-minimal-cloudimg-amd64.squashfs
