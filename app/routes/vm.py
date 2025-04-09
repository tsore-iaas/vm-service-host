from typing import Literal
from fastapi import APIRouter, Depends, Response
from app.main import SessionDep
from app.schemas.VMRequirementsRequest import VMRequirementsRequest
from app.schemas.VMConfigResponse import VMConfigResponse
from app.models.VM import VM
from app.services.VMService import create_vm, delete_vm, paused_or_resumed_vm

vm_router = APIRouter()

@vm_router.post("/vm")
def create_vm_on_host(vm_requirements: VMRequirementsRequest, session: SessionDep) -> VMConfigResponse:
  return create_vm(vm_requirements=vm_requirements, session=session)

@vm_router.delete("/vm/{id}")
def delete_vm_on_host(id: int, session: SessionDep) -> VM:
  return delete_vm(id=id, session=session)

@vm_router.put("/vm/state/{id}")
def paused_or_resume_user_vm(id: int, state: Literal["Resumed", "Paused"], session: SessionDep) -> Response:
    result = paused_or_resumed_vm(id, state, session)
    if result:
        return Response(status_code=200)
    else:
        return Response(status_code=400)