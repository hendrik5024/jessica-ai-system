import psutil
from typing import Dict, Any


def get_system_health() -> Dict[str, Any]:
    """Return current system health metrics useful for Jessica's runtime decisions."""
    vm = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.2)
    disk = psutil.disk_usage('/')
    processes = len(psutil.pids())

    return {
        "cpu_percent": cpu_percent,
        "memory": {
            "total": vm.total,
            "available": vm.available,
            "percent": vm.percent,
            "used": vm.used,
            "free": getattr(vm, 'free', None),
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        },
        "processes": processes,
    }


def can_run_heavy_task(min_available_bytes: int = 1_000_000_000,
                       max_cpu_percent: float = 90.0) -> Dict[str, Any]:
    """
    Simple gate to decide whether it's safe to run heavy work.
    - min_available_bytes: minimum RAM recommended to be available
    - max_cpu_percent: max current CPU percentage to allow
    Returns decision and current metrics.
    """
    metrics = get_system_health()
    ok = (metrics["memory"]["available"] >= min_available_bytes) and (
        metrics["cpu_percent"] <= max_cpu_percent
    )

    return {
        "ok": ok,
        "reason": None if ok else "Insufficient resources",
        "metrics": metrics,
        "thresholds": {
            "min_available_bytes": min_available_bytes,
            "max_cpu_percent": max_cpu_percent,
        }
    }
