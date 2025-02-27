from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from typing import Annotated, Optional
from pydantic import BaseModel
from prometheus_client.parser import text_string_to_metric_families

import os, shutil, subprocess, paramiko, io, json, time, requests, re
import config.settings

# Models
from app.models.VM import VM
from app.models.Rootfs import Rootfs

#Importation des Schemas
from app.schemas.VMConfigResponse import VMConfigResponse
from app.schemas.VMRequirementsRequest import VMRequirementsRequest
from app.schemas.RootfsRequirementsRequest import RootfsRequirementsRequest
from app.schemas.RootfsDownloadResponse import RootfsDownloadResponse

# Database setup
DATABASE_URL = "sqlite:///./vm.db"

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session

SessionDep = Annotated[Session, Depends(get_session)]


# FastAPI setup
app = FastAPI()
#Mise sur pied des évènement
app.add_event_handler("startup", create_db_and_tables)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modifiez en fonction de vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


TMP_DIR = "/tmp/firecracker_sockets"
BASE_DIR = "/tmp/vms"
SOCKET_PREFIX = "firecracker"
BRIDGE_NAME = "br0"
GATEWAY_ADDRESS = "192.168.8.1"

from app.routes.vm import vm_router;
from app.routes.download import download_router;
from app.routes.host import host_router;
app.include_router(vm_router)
app.include_router(download_router)
app.include_router(host_router)
