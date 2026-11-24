"""JARVIS plugin: report basic Windows/PC resource usage."""
PLUGIN = {
    "name": "system_monitor",
    "description": (
        "Report the computer's current CPU usage, RAM usage, and main disk usage "
        "when the user asks how the PC is performing, how much memory is being used, "
        "or asks for a system status. Do not use this for internet searches or app launching."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {},
        "required": [],
    },
}

def run(parameters: dict, player=None, session_memory=None) -> str:
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk_path = "C:\\" if __import__("os").name == "nt" else "/"
        disk = psutil.disk_usage(disk_path)

        result = (
            f"System status: CPU usage {cpu:.0f} percent. "
            f"RAM usage {memory.percent:.0f} percent "
            f"({memory.used / (1024**3):.1f} of {memory.total / (1024**3):.1f} gigabytes). "
            f"Disk usage {disk.percent:.0f} percent "
            f"({disk.free / (1024**3):.1f} gigabytes free)."
        )
        if player:
            try:
                player.write_log(f"JARVIS: {result}")
            except Exception:
                pass
        return result
    except ImportError:
        return "Sir, system monitoring requires the psutil package, which is not available."
    except Exception as exc:
        return f"Sir, I couldn't read the system status: {exc}"
