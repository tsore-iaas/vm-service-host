import requests, os

from app.schemas.RootfsRequirementsRequest import RootfsRequirementsRequest
from app.schemas.RootfsDownloadResponse import RootfsDownloadResponse
from app.models.Rootfs import Rootfs
from app.main import SessionDep

def download_rootfs(rootfs_requirements: list[RootfsRequirementsRequest], session: SessionDep) -> list[RootfsDownloadResponse]:
    # Initialisation de la liste vide pour stocker les résultats du téléchargement
    rootfs_download_list = []

    for rootfs in rootfs_requirements:
        # Construction du chemin où le rootfs sera sauvegardé
        rootfs_path = os.path.join(rootfs.rootfs_base_path_on_host)
        print(f"[DEBUG] Lancement du téléchargement")
        
        # Demande HTTP pour télécharger le fichier
        try:
          response = requests.get(rootfs.rootfs_url, timeout=5)
        except ConnectionError as e:
           rootfs_download_list.append(RootfsDownloadResponse(
              rootfs_base_path_on_host=rootfs_path, 
              rootfs_url=rootfs.rootfs_url, 
              downloaded=False, 
              message=f"Rootfs download failed : {e}"
           ))
           continue

        if response.status_code == 200:
            # Si le téléchargement réussit, on l'enregistre dans un fichier
            with open(rootfs_path, "wb") as f:
                f.write(response.content)
            print("[DEBUG] Rootfs downloaded")
            
            # Enregistrer l'entrée dans la base de données
            rootfsSave = Rootfs(rootfs_base_path_on_host=rootfs_path, rootfs_url=rootfs.rootfs_url)
            session.add(rootfsSave)
            session.commit()
            
            # Ajouter un objet RootfsDownloadResponse à la liste des téléchargements réussis
            rootfs_download_list.append(RootfsDownloadResponse(
                rootfs_base_path_on_host=rootfs_path, 
                rootfs_url=rootfs.rootfs_url, 
                downloaded=True, 
                message="Rootfs downloaded"
            ))
        else:
            # Si le téléchargement échoue, on ajoute un objet RootfsDownloadResponse avec un message d'erreur
            rootfs_download_list.append(RootfsDownloadResponse(
                rootfs_base_path_on_host=rootfs_path, 
                rootfs_url=rootfs.rootfs_url, 
                downloaded=False, 
                message="Rootfs not downloaded"
            ))
    print("[Telechargement terminé]")
    # Retourner la liste des téléchargements (réussis ou échoués)
    return rootfs_download_list
