import psutil


def get_cpu_usage():
    return psutil.cpu_percent(interval=None)


def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent


def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent


def get_system_status():
    cpu = get_cpu_usage()
    mem = get_memory_usage()
    disk = get_disk_usage()

    return {
        "cpu": cpu,
        "memory": mem,
        "disk": disk
    }
