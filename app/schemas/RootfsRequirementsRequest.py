from pydantic import BaseModel

#Cette classe va permettre de contenirs les informations necessaire au téléchargement d'un fichiers rootfs
class RootfsRequirementsRequest(BaseModel):
  rootfs_base_path_on_host: str
  rootfs_url: str