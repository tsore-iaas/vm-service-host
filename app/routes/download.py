from fastapi import APIRouter
from app.main import SessionDep
from app.schemas.RootfsDownloadResponse import RootfsDownloadResponse
from app.schemas.RootfsRequirementsRequest import RootfsRequirementsRequest
from app.services.DownloadService import download_rootfs
download_router = APIRouter()

@download_router.post("/download/rootfs")
def download_rootfs_on_host(rootfs_requirements: list[RootfsRequirementsRequest], session: SessionDep) -> list[RootfsDownloadResponse]:
  return download_rootfs(rootfs_requirements=rootfs_requirements, session=session)