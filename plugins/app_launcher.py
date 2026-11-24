"""JARVIS plugin: launch a small allowlist of common Windows applications."""
import os
import shutil
from pathlib import Path

PLUGIN = {
    "name": "app_launcher",
    "description": (
        "Open or launch an installed Windows application when the user asks JARVIS "
        "to open, start, or launch Chrome, Edge, Firefox, Discord, Spotify, Steam, "
        "Notepad, Calculator, File Explorer, or Task Manager. Use this tool only "
        "for launching one of those applications; do not use it to execute arbitrary commands."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "application": {
                "type": "STRING",
                "description": "Application to open: chrome, edge, firefox, discord, spotify, steam, notepad, calculator, explorer, or task_manager."
            }
        },
        "required": ["application"],
    },
}

def _log(player, message):
    if player:
        try:
            player.write_log(f"JARVIS: {message}")
        except Exception:
            pass

def run(parameters: dict, player=None, session_memory=None) -> str:
    app = str(parameters.get("application", "")).strip().lower().replace(" ", "_")
    aliases = {
        "google_chrome": "chrome", "microsoft_edge": "edge",
        "file_explorer": "explorer", "task manager": "task_manager",
        "taskmanager": "task_manager", "bloc_de_notas": "notepad",
        "calculadora": "calculator",
    }
    app = aliases.get(app, app)

    commands = {
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "explorer": ["explorer.exe"],
        "task_manager": ["taskmgr.exe"],
    }
    executable_names = {
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "discord": "Discord.exe",
        "spotify": "Spotify.exe",
        "steam": "steam.exe",
    }

    if app not in commands and app not in executable_names:
        return "Sir, that application is not in my approved launch list."

    try:
        import subprocess

        if app in commands:
            subprocess.Popen(commands[app], shell=False)
        else:
            exe = executable_names[app]
            found = shutil.which(exe)
            candidates = []
            local = os.environ.get("LOCALAPPDATA", "")
            program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
            program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
            if app == "chrome":
                candidates = [
                    Path(program_files) / "Google/Chrome/Application/chrome.exe",
                    Path(program_files_x86) / "Google/Chrome/Application/chrome.exe",
                    Path(local) / "Google/Chrome/Application/chrome.exe",
                ]
            elif app == "edge":
                candidates = [
                    Path(program_files_x86) / "Microsoft/Edge/Application/msedge.exe",
                    Path(program_files) / "Microsoft/Edge/Application/msedge.exe",
                ]
            elif app == "firefox":
                candidates = [
                    Path(program_files) / "Mozilla Firefox/firefox.exe",
                    Path(program_files_x86) / "Mozilla Firefox/firefox.exe",
                ]
            elif app == "discord":
                candidates = [
                    Path(local) / "Discord/Update.exe",
                    Path(local) / "Programs/Discord/Discord.exe",
                ]
            elif app == "spotify":
                candidates = [
                    Path(local) / "Microsoft/WindowsApps/Spotify.exe",
                    Path(program_files) / "Spotify/Spotify.exe",
                ]
            elif app == "steam":
                candidates = [
                    Path(program_files_x86) / "Steam/steam.exe",
                    Path(program_files) / "Steam/steam.exe",
                ]

            target = Path(found) if found else next((p for p in candidates if p.is_file()), None)
            if target is None:
                # Windows can resolve registered app execution aliases such as Spotify.
                if os.name == "nt" and app in ("spotify", "discord"):
                    os.startfile(app)
                else:
                    return f"Sir, I couldn't find {app}. Check that it is installed."
            elif app == "discord" and target.name.lower() == "update.exe":
                subprocess.Popen([str(target), "--processStart", "Discord.exe"], shell=False)
            else:
                subprocess.Popen([str(target)], shell=False)

        spoken = f"Opening {app.replace('_', ' ')}."
        _log(player, spoken)
        return spoken
    except Exception as exc:
        return f"Sir, I couldn't open {app}: {exc}"
