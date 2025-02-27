from fastapi import APIRouter, Query
from app.services.HostService import get_node_exporter_metrics

host_router = APIRouter()

@host_router.get("/host/metrics")
def get_node_exporter_metrics_for_host(to_gb: bool = Query(False, description="Convert RAM and disk size to GB")):
  return get_node_exporter_metrics(to_gb=to_gb)