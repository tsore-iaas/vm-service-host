from pydantic import BaseModel

#Cette classe va permettre de contenirs les informations necessaire à la création d'une VM
class VMRequirementsRequest(BaseModel):
  id: int
  name: str
  distribution_name: str
  ram: int
  cpu: int
  storage: str  # Par exemple "30 Go"
  ip_address: str
  password: str  # Correction de l'orthographe : "password"
  kernel_base_path: str
  rootfs_base_path: str
