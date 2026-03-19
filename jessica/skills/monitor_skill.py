"""System monitoring skill - provides real-time system information."""
import psutil
from datetime import datetime


def can_handle(intent: dict) -> bool:
    """Check if this skill should handle the intent."""
    return intent.get("intent") == "monitor"


def run(intent: dict, context=None, relevant=None, manager=None):
    """Get system information like time, CPU, memory, disk usage."""
    query = (intent.get("text") or "").lower().strip()
    
    try:
        # Time queries
        if any(kw in query for kw in ["what is the time", "what time", "current time", "what's the time", "tell me the time"]):
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            return {
                "result": {
                    "message": f"The current time is {time_str} on {date_str}."
                }
            }
        
        # CPU usage
        if "cpu" in query or "processor" in query:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            return {
                "result": {
                    "message": f"CPU usage is currently {cpu_percent}%."
                }
            }
        
        # Memory usage
        if "memory" in query or "ram" in query:
            mem = psutil.virtual_memory()
            return {
                "result": {
                    "message": f"Memory usage: {mem.percent}% ({mem.used // (1024**3)}GB used of {mem.total // (1024**3)}GB total)."
                }
            }
        
        # Disk usage
        if "disk" in query or "storage" in query:
            disk = psutil.disk_usage('/')
            return {
                "result": {
                    "message": f"Disk usage: {disk.percent}% ({disk.used // (1024**3)}GB used of {disk.total // (1024**3)}GB total)."
                }
            }
        
        # Process list
        if "processes" in query or "running" in query:
            processes = [p.info['name'] for p in psutil.process_iter(['name'])][:10]
            return {
                "result": {
                    "message": f"Top running processes: {', '.join(processes)}"
                }
            }
        
        # System uptime
        if "uptime" in query or "how long has your computer been running" in query:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes = remainder // 60
            return {
                "result": {
                    "message": f"System uptime: {hours} hours and {minutes} minutes since {boot_time.strftime('%I:%M %p')}."
                }
            }
        
        # General status
        return {
            "result": {
                "message": "System monitoring ready. Ask about: time, CPU, memory, disk, processes, or uptime."
            }
        }
    
    except Exception as e:
        return {
            "result": {
                "error": f"System monitoring error: {str(e)}"
            }
        }
