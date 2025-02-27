from pydantic import BaseModel

#Ce model sera retourné lors du téléchargement d'une vm pour dire si cela à été fait avec succès ou pas
class RootfsDownloadResponse(BaseModel):
  rootfs_base_path_on_host: str
  rootfs_url: str
  downloaded : bool
  message : str