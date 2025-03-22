from app.main import SessionDep, firestore_db
from app.schemas.VMRequirementsRequest import VMRequirementsRequest
from app.schemas.VMConfigResponse import VMConfigResponse
from fastapi import HTTPException
from app.models.VM import VM

import os, shutil, subprocess, json, time, paramiko, io
import config.settings as config
import threading

def create_vm(vm_requirements: VMRequirementsRequest, session: SessionDep) -> VMConfigResponse:
    #On verifie que l'id n'est pas déjà utilisé
    if session.get(VM, vm_requirements.id):
      raise HTTPException(status_code=409, detail="ID already exists")
    

    vm_config = VMConfigResponse(id=vm_requirements.id,
            name=vm_requirements.name,
            cpu=vm_requirements.cpu,
            ram=vm_requirements.ram,
            distribution_name=vm_requirements.distribution_name,
            ip_address=vm_requirements.ip_address,)
    vm = VM(id=vm_requirements.id,
            name=vm_requirements.name,
            cpu=vm_requirements.cpu,
            ram=vm_requirements.ram,
            distribution_name=vm_requirements.distribution_name,
            ip_address=vm_requirements.ip_address,
            storage=vm_requirements.storage)

    # Création du répertoire VM
    vm_dir = os.path.join(config.BASE_DIR,f"vm_{vm_requirements.id}")
    print(f"[DEBUG] Répertoire VM : {vm_dir}")
    if not os.path.exists(vm_dir):
      os.makedirs(vm_dir)
    
    #Chemins des fichiers
    vm.kernel_path = os.path.join(vm_dir, os.path.basename(vm_requirements.kernel_base_path))
    vm.rootfs_path = os.path.join(vm_dir, os.path.basename(vm_requirements.rootfs_base_path))
    print(f"[DEBUG] Kernel path : {vm.kernel_path}")
    print(f"[DEBUG] Rootfs path : {vm.rootfs_path}")

    # Copie des fichiers
    shutil.copy(vm_requirements.kernel_base_path, vm.kernel_path)
    shutil.copy(vm_requirements.rootfs_base_path, vm.rootfs_path)
    print(f"[DEBUG] Fichiers copiés")

    # Création du socket en se rassurant qu'il n'existe pas déjà
    socket_path = os.path.join(vm_dir, f"{config.SOCKET_PREFIX}_{vm_requirements.id}.sock")
    if os.path.exists(socket_path):
        os.remove(socket_path)
        print(f"[DEBUG] Ancien socket supprimé : {socket_path}")
    print(f"[DEBUG] Socket path généré : {socket_path}")
    vm.socket_path = socket_path

    # Création de l'interface tap pour la connexion externe
    vm.iface_net = f"tap{vm_requirements.id}"
    #vm_iface = VMIface()
    #vm_iface.name = f"tap{vm_requirements.id}"
    #vm.vms_iface.append(vm_iface)
    #session.add(vm_iface)
    #session.commit()
    #session.refresh(vm_iface)

    # Configuration du réseau pour la microVM
    print("[DEBUG] Configuration du réseau")
    #for iface in vm.vms_iface:
    subprocess.run(["sudo", "bash", config.SCRIPTS_FOLDER+"setup_tap.sh", 
        vm.iface_net, config.BRIDGE_NAME],
        check=True,  # Lève une exception si le code de retour n'est pas 0
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
      
    #Géneration de la clé ssh
    print("[DEBUG] Generation de la clé ssh")
    private_key = paramiko.RSAKey.generate(2048)
    private_key_str = io.StringIO()
    private_key.write_private_key(private_key_str)
    vm_config.ssh_private_key = private_key_str.getvalue()
    public_key_str = f"{private_key.get_name()} {private_key.get_base64()}"

    private_key.write_private_key_file("/home/daniel/Documents/Hackathon24/rsakey")

    print("[DEBUG] Configuration du réseau et de l'espace de stockage")
    subprocess.run(["sudo", "bash", config.SCRIPTS_FOLDER+"create_rootfs.sh", 
                    vm.rootfs_path, 
                    f"{vm_dir}/disk.ext4", 
                    vm_requirements.storage,
                    vm_requirements.ip_address, # 192.168.5.8/24
                    config.GATEWAY_ADDRESS,
                    vm_requirements.name,
                    public_key_str,
                    vm_requirements.password],
        check=True,  # Lève une exception si le code de retour n'est pas 0
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    
    #Création du pipe pour les metrics
    metrics_path = os.path.join(vm_dir, "metrics.fifo")
    subprocess.run(["sudo", "mkfifo", metrics_path], check=True)
    vm.metrics_path = metrics_path
    
    # Configuration
    config_path = os.path.join(vm_dir, "vm_config.json")
    print(f"[DEBUG] Chemin config : {config_path}")
    
    vm_config_json = {
        "boot-source": {
            "kernel_image_path": str(vm.kernel_path),  # Conversion explicite en string
            "boot_args": "console=ttyS0 reboot=k panic=1 pci=off"
        },
        "network-interfaces": [
            {
                "iface_id": "eth0",
                "host_dev_name": vm.iface_net#vm_iface.name
            }
        ],
        "drives": [
            {
                "drive_id": "rootfs",
                "path_on_host": str(f"{vm_dir}/disk.ext4"),#str(rootfs_path),  # Conversion explicite en string
                "is_root_device": True,
                "is_read_only": False
            }
        ],
        "machine-config": {
            "vcpu_count": vm_requirements.cpu,
            "mem_size_mib": vm_requirements.ram
        },
        "metrics":{
           "metrics_path": vm.metrics_path
        }
    }

    with open(config_path, "w") as config_file:
        json.dump(vm_config_json, config_file, indent=4)
    print("[DEBUG] Configuration écrite")

    print(f"[DEBUG] Lancement de Firecracker avec socket : {vm.socket_path}")
    firecracker_process = subprocess.Popen([
          "firecracker",
          "--api-sock", vm.socket_path,
          "--config-file", config_path
      ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(1)
    if firecracker_process.poll() is not None:
      error_output = firecracker_process.stderr.read().decode('utf-8')
      print(f"[DEBUG] Erreur Firecracker : {error_output}")
      raise Exception(f"Firecracker startup failed: {error_output}")

    session.add(vm)
    session.commit()
    session.refresh(vm)

    print("[DEBUG] Configuration terminée")
    
    store_metrics_pthread = threading.Thread(target=save_metrics, args=(vm,))
    store_metrics_pthread.start()
    print("[DEUG] Démarrage de Firecracker")
    
    return vm_config


def delete_vm(id: int, session: SessionDep) -> VM:
    vm = session.get(VM, id)
    if not vm:
      raise HTTPException(status_code=404, detail="VM not found")
    
    #On efface l'interface tap
    print("[DEBUG] Destruction de l'interface tap")
    #for iface in vm.vms_iface:
    subprocess.run(["sudo", "bash", config.SCRIPTS_FOLDER+"remove_tap.sh",
        vm.iface_net, config.BRIDGE_NAME],
        check=True,  # Lève une exception si le code de retour n'est pas 0
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    
    #Destruction du dossier de la vm
    vm_dir = os.path.join(config.BASE_DIR,f"vm_{vm.id}")
    try:
        shutil.rmtree(vm_dir)
        print(f"Le fichier ou répertoire {vm_dir} a été supprimé avec succès.")
    except PermissionError:
        raise HTTPException(status_code=401, detail=f"Permission refusée : vous devez exécuter ce script avec des privilèges administratifs.")
    except FileNotFoundError:
        raise HTTPException(status_code=403, detail=f"Le fichier ou répertoire {vm_dir} n'existe pas.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Une erreur s'est produite : {e}")

    session.delete(vm)
    session.commit()
    return vm

def save_metrics(vm: VM) -> None:
   print("[DEBUG] Envoi de metrics")
   while True:
    subprocess.run(["sudo", "curl", "--unix-socket", vm.socket_path, "-i", "-X", "PUT", "http://localhost/actions",
                    "-d", "{ \"action_type\": \"FlushMetrics\" }"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True)
    print("On entre lire le fichiers")
    with open(vm.metrics_path, "r") as fifo:
        while True:
            body = fifo.readline()
            print(body, "\n\n\n Test \n\n\n")
            try:
                data = json.loads(body)
                firestore_db.collection("micro_vm_metrics").document(str(vm.id+time.time())).set(data)
                print("[DEBUG] Metrics envoyé avec succès")
            except json.JSONDecodeError:
                print("[DEBUG] Erreur de parsing JSON, ignorée")
            stat = os.fstat(fifo.fileno())
            if stat.st_size == 0:
                break
    time.sleep(5)
