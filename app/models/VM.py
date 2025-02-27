from sqlmodel import Field, SQLModel

class VM(SQLModel, table=True):
  id: int = Field(primary_key=True)
  name: str
  distribution_name: str 
  ram: int 
  cpu: int 
  storage: str #30 Go par exemple
  ip_address: str
  socket_path: str
  kernel_path: str
  rootfs_path: str
  iface_net: str