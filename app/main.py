from typing import Annotated
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine

from app.services.HostService import join_host, init_host

import threading

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

#Initialisation de firestore
from google.cloud import firestore
# Initialize Firestore client
firestore_db = firestore.Client.from_service_account_json('./config/iaas4firecracker-firebase-adminsdk-fbsvc-73db0f8ffc.json')

def on_startup():
  thread = threading.Thread(target=join_host)
  thread.start()

# FastAPI setup
app = FastAPI()
#Mise sur pied des évènement
app.add_event_handler("startup", init_host)
app.add_event_handler("startup", create_db_and_tables)
app.add_event_handler("startup", on_startup)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modifiez en fonction de vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes.vm import vm_router;
from app.routes.download import download_router;
from app.routes.host import host_router;
app.include_router(vm_router)
app.include_router(download_router)
app.include_router(host_router)
