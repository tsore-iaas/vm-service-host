from sqlmodel import SQLModel, Field
class Rootfs(SQLModel, table=True):
  id: int = Field(primary_key=True)
  rootfs_base_path_on_host: str
  rootfs_url: str