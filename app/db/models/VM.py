from sqlmodel import Field, SQLModel

class VM(SQLModel, table=True):
  id: int = Field(primary_key=True)
  name: str = Field()
  distribution_name: str = Field()
  ram: int = Field()
  cpu: int = Field()
  storage: int = Field()
  ip_address: int = Field()
  password: str