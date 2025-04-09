from sqlmodel import Field, SQLModel
from enum import Enum
class VMState(str, Enum):
    STOP = "STOP"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"

class VM(SQLModel, table=True):
  id: int = Field(primary_key=True)
  name: str
  distribution_name: str 
  ram: int 
  cpu: int 
  storage: str #30 Go par exemple
  state: VMState
  ip_address: str
  socket_path: str
  kernel_path: str
  rootfs_path: str
  iface_net: str
  metrics_path: str
  metrics_path: str