from pydantic import BaseModel
from typing import Optional

#Cette classe va contenir les éléments retouné lors de la création d'une VM
class VMConfigResponse(BaseModel):
  id: Optional[int] = None
  name: Optional[str] = None
  distribution_name: Optional[str] = None
  ram: Optional[int] = None
  cpu: Optional[int] = None
  storage: Optional[str] = None  # Par exemple "30 Go"
  ip_address: Optional[str] = None
  ssh_private_key: Optional[str] = None