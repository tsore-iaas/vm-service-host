from fastapi import Query
import requests, re, subprocess
import config.settings as config

#On installe un bridge pour la connexion au réseau des VM et on le démarre à l'aide du script approprié
def init_host():
    print("[DEBUG] Configuration du réseau sur le host")
    subprocess.run(["sudo", "bash", config.SCRIPTS_FOLDER+"setup-bridge.sh", 
                    config.HOST_INTERFACE_NAME, config.BRIDGE_NAME ],
        check=True,  # Lève une exception si le code de retour n'est pas 0
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    print("[DEBUG] Bridge configuré avec succès")

def get_node_exporter_metrics(to_gb: bool = False):
    url = "http://localhost:9100/metrics"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch metrics"}
    
    data = response.text
    metrics = {}

    def extract_value(pattern):
        """Extrait une valeur (entière ou en notation scientifique) et la convertit en int."""
        match = re.search(pattern, data)
        return int(float(match.group(1))) if match else None

    def convert_to_gb(value):
        """Convertit les bytes en Go si l'option est activée."""
        return round(value / (1024**3), 2) if to_gb else value

    # Mémoire
    mem_total = extract_value(r'node_memory_MemTotal_bytes (\d+\.\d+e[+-]?\d+|\d+)')
    mem_available = extract_value(r'node_memory_MemAvailable_bytes (\d+\.\d+e[+-]?\d+|\d+)')

    if mem_total is not None and mem_available is not None:
        mem_used = mem_total - mem_available
        metrics["memory"] = {
            "total": convert_to_gb(mem_total),
            "used": convert_to_gb(mem_used),
            "unit": "GB" if to_gb else "bytes"
        }

    # CPU
    cpu_times = {}
    for match in re.finditer(r'node_cpu_seconds_total{.*mode="(\w+)"} (\d+\.\d+e[+-]?\d+|\d+\.\d+)', data):
        mode, value = match.groups()
        cpu_times[mode] = float(value)

    if "idle" in cpu_times and cpu_times:
        total_cpu_time = sum(cpu_times.values())
        if total_cpu_time > 0:
            cpu_usage = 100 * (1 - (cpu_times["idle"] / total_cpu_time))
            metrics["cpu_usage_percent"] = round(cpu_usage, 2)

    # Disque
    disk_total = extract_value(r'node_filesystem_size_bytes{.*mountpoint="/".*} (\d+\.\d+e[+-]?\d+|\d+)')
    disk_available = extract_value(r'node_filesystem_avail_bytes{.*mountpoint="/".*} (\d+\.\d+e[+-]?\d+|\d+)')

    if disk_total is not None and disk_available is not None:
        disk_used = disk_total - disk_available
        metrics["disk"] = {
            "total": convert_to_gb(disk_total),
            "used": convert_to_gb(disk_used),
            "unit": "GB" if to_gb else "bytes"
        }

    return metrics


def join_host():
    host_url = "http://" + config.MASTER_IP + ":" + config.MASTER_PORT + "/vm-manager/hosts/"
    data = {
        "location": config.LOCATION,
        "ip_address" : config.HOST_IP
    }
    print("[DEBUG]", host_url)
    response = requests.post(url=host_url, json=data)
 
    if response.status_code == 200:
        print("[DEBUG] Cluster rejoins avec succès")
    else:
        print("[DEBUG] ", response.text)
        print("[DEBUG] Problème lors de l'essaie de la jonction avec le cluster")
