# IaaS4Firecracker - Service d'Hébergement de Machines Virtuelles

Ce projet est destiné aux hôtes qui vont héberger des machines virtuelles. Il s'agit d'un service backend permettant la gestion, le déploiement et la supervision des VM, facilitant la communication entre le serveur principal (VM-Service) et les hôtes. Ce README vous guide à travers l'installation, la configuration et l'exécution du service.

---

## Table des Matières

- [Introduction](#introduction)
- [🚀 Fonctionnalités](#-fonctionnalités)
- [🧱 Prérequis](#-prérequis)
- [Configuration](#configuration)
  - [Configuration Master](#configuration-master)
  - [Configuration de l'Hôte](#configuration-de-lhôte)
  - [Configuration Réseau](#configuration-réseau)
  - [Configuration des Machines Virtuelles](#configuration-des-machines-virtuelles)
  - [Répertoire des Scripts](#répertoire-des-scripts)
- [Installation](#installation)
- [Exécution du Service](#exécution-du-service)
- [Structure du Projet](#structure-du-projet)
- [Notes Complémentaires](#notes-complémentaires)
- [Licence](#licence)

---

## Introduction

Le service IaaS4Firecracker est conçu pour être déployé sur des hôtes hébergeant des machines virtuelles. Il permet :

- La communication et la coordination entre un serveur principal (VM-Service) et plusieurs hôtes.
- La collecte et l'enregistrement des métriques des VM via l’intégration avec Firebase.
- La configuration et le contrôle des paramètres réseau et des ressources associées aux VM.

Le système est construit en Python et utilise des scripts Bash pour automatiser certaines configurations réseau.

---

## 🚀 Fonctionnalités

- **Exécution, configuration et arrêt de VM Firecracker**
- **Configuration dynamique de l’environnement réseau**  
  (bridge, TAP, etc.)
- **Envoi de métriques vers Firebase**
- **API REST** pour le contrôle local ou via le serveur maître
- **Intégration Prometheus** (via node_exporter) pour la supervision des ressources hôtes

---

## 🧱 Prérequis

- **Python 3.8+**
- **node_exporter** installé et lancé sur l’hôte
- **Firecracker** installé
- **Outils réseau requis :** bridge-utils, iproute2, iptables, etc.
- **Accès root** requis pour lancer le service

---

## Configuration

La configuration se trouve dans le fichier `config/settings.py`. Adaptez les variables suivantes à votre environnement :

### Configuration Master

- **`MASTER_IP`**  
  _Adresse IP du serveur principal (VM-Service)._  
  _Utilité :_ Gérer les requêtes et la communication entre les hôtes.

- **`MASTER_PORT`**  
  _Port d'écoute du serveur principal._  
  _Utilité :_ Faciliter l’échange de données entre le master et les hôtes.

### Configuration de l'Hôte

- **`HOST_IP`**  
  _Adresse IP de l'hôte sur lequel le service est déployé._  
  _Utilité :_ Permettre au service de s’auto-identifier dans le réseau.

- **`LOCATION`**  
  _Localisation géographique de l'hôte._  
  _Utilité :_ À des fins d’information et de configuration au niveau du master.

### Configuration Réseau

- **`HOST_INTERFACE_NAME`**  
  _Nom de l'interface réseau de l'hôte._  
  _Utilité :_ Indispensable pour configurer la connectivité réseau des VM via un bridge.

### Configuration des Machines Virtuelles

- **`TMP_DIR`**  
  _Répertoire temporaire pour stocker les fichiers de socket des VM._  
  _Utilité :_ Gérer la communication inter-processus.

- **`BASE_DIR`**  
  _Répertoire de base pour les fichiers associés aux VM._  
  _Utilité :_ Centraliser les ressources des VM.

- **`SOCKET_PREFIX`**  
  _Préfixe pour nommer les fichiers de socket des VM._  
  _Utilité :_ Standardiser et faciliter l’identification des sockets.

- **`BRIDGE_NAME`**  
  _Nom du pont réseau utilisé pour connecter les VM._  
  _Utilité :_ Permettre aux VM de se connecter au réseau en attachant leurs interfaces virtuelles.

- **`GATEWAY_ADDRESS`**  
  _Adresse IP de la passerelle réseau utilisée par les VM._  
  _Utilité :_ Garantir l’accès réseau extérieur via la passerelle.

### Répertoire des Scripts

- **`SCRIPTS_FOLDER`** (Ne pas modifier)  
  _Répertoire contenant les scripts de configuration et de gestion des VM._  
  _Emplacement :_ `app/scripts/`  
  _Utilité :_ Automatiser les tâches telles que la création de rootfs, la configuration du bridge, et la gestion des interfaces TAP.

---

## Installation

Pour isoler les dépendances et garantir un environnement propre, utilisez un environnement virtuel Python. Dans la racine du projet, exécutez :

1. **Création de l'environnement virtuel :**

   ```sh
   python3 -m venv .env
   ```

2. **Activation de l'environnement virtuel :**

   ```sh
   source .env/bin/activate
   ```

3. **Installation des dépendances :**

   ```sh
   pip install -r requirements.txt
   ```

---

## Exécution du Service

Pour lancer le service, il est nécessaire de disposer des droits root, car certaines opérations (comme la configuration réseau) requièrent des privilèges élevés. **Notez que vous devez lancer le service depuis la racine du projet, sans vous déplacer dans le dossier `app`.**

Exécutez la commande suivante depuis le dossier parent :

```sh
sudo env "PATH=$PATH" uvicorn app.main:app
```

Cette commande démarre le serveur, qui écoute les requêtes et gère les communications entre le master et les hôtes.

---

## Structure du Projet

Voici une vue d'ensemble de la structure du projet, sans inclure les fichiers `.pyc` ni les dossiers `__pycache__` :

```
.
├── app
│   ├── debug.log
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── Rootfs.py
│   │   └── VM.py
│   ├── routes
│   │   ├── download.py
│   │   ├── host.py
│   │   └── vm.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── RootfsDownloadResponse.py
│   │   ├── RootfsRequirementsRequest.py
│   │   ├── VMConfigResponse.py
│   │   └── VMRequirementsRequest.py
│   ├── scripts
│   │   ├── create_rootfs.sh
│   │   ├── __init__.py
│   │   ├── remove_tap.sh
│   │   ├── setup-bridge.sh
│   │   └── setup_tap.sh
│   └── services
│       ├── DownloadService.py
│       ├── HostService.py
│       ├── __init__.py
│       └── VMService.py
├── config
│   ├── iaas4firecracker-firebase-adminsdk-fbsvc-73db0f8ffc.json
│   ├── __init__.py
│   └── settings.py
├── debug.log
├── init_host
│   └── setup-bridge.sh
├── LICENSE
├── README.md
├── requirements.txt
├── uninstall_host
│   └── remove-bridge.sh
└── vm.db
```

### Détails par répertoire :

- **app/** : Contient le cœur de l’application (serveur, modèles de données, routes et services).
- **config/** : Fichiers de configuration, notamment les paramètres du service et le fichier de connexion Firebase.
- **init_host/** et **uninstall_host/** : Scripts pour initialiser et désinstaller la configuration réseau sur l’hôte.
- **vm.db** : Base de données locale utilisée pour le suivi des machines virtuelles.

---

## Notes Complémentaires

- **Privilèges Root :** L'exécution du service nécessite des droits administratifs pour gérer la configuration réseau et les interfaces des VM.
- **Mise à jour des dépendances :** Pensez à mettre à jour régulièrement les dépendances Python et les scripts système pour bénéficier des dernières améliorations et correctifs de sécurité.
- **Personnalisation :** Avant le déploiement, adaptez le fichier `config/settings.py` selon votre infrastructure et vos besoins spécifiques.

---

## Licence

Ce projet est distribué sous licence [...] – veuillez consulter le fichier [LICENSE](./LICENSE) pour plus de détails.

---
