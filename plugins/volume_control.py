"""JARVIS plugin: control Windows master volume using multimedia keys."""
PLUGIN = {
    "name": "volume_control",
    "description": (
        "Raise, lower, mute, or unmute the Windows master volume when the user "
        "asks to change the PC volume or mute sound. Use only for volume controls, "
        "not for changing individual application audio settings."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "One of: volume_up, volume_down, mute."
            },
            "steps": {
                "type": "INTEGER",
                "description": "Optional number of volume steps, from 1 to 10. Default is 2."
            }
        },
        "required": ["action"],
    },
}

def run(parameters: dict, player=None, session_memory=None) -> str:
    try:
        import ctypes
        import os

        if os.name != "nt":
            return "Sir, this volume plugin currently works only on Windows."

        action = str(parameters.get("action", "")).strip().lower()
        try:
            steps = int(parameters.get("steps", 2))
        except (TypeError, ValueError):
            steps = 2
        steps = max(1, min(10, steps))

        user32 = ctypes.windll.user32
        key_up = 0x0002
        keys = {
            "volume_up": 0xAF,
            "volume_down": 0xAE,
            "mute": 0xAD,
        }
        if action not in keys:
            return "Sir, choose volume_up, volume_down, or mute."

        presses = 1 if action == "mute" else steps
        for _ in range(presses):
            user32.keybd_event(keys[action], 0, 0, 0)
            user32.keybd_event(keys[action], 0, key_up, 0)

        spoken = {
            "volume_up": f"Volume increased by {steps} steps.",
            "volume_down": f"Volume decreased by {steps} steps.",
            "mute": "Toggled mute.",
        }[action]
        if player:
            try:
                player.write_log(f"JARVIS: {spoken}")
            except Exception:
                pass
        return spoken
    except Exception as exc:
        return f"Sir, I couldn't change the volume: {exc}"
