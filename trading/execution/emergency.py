"""
Emergency execution stop.

The emergency stop is intentionally local and persistent.
When active, no new trade may be authorized for execution.
"""

import json
import os


STATE_FILE = ".trading_emergency.json"


def is_emergency_stop_active():
    if not os.path.exists(STATE_FILE):
        return False

    try:
        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return bool(data.get("active", False))

    except Exception:
        # Fail closed.
        return True


def activate_emergency_stop():
    temporary = f"{STATE_FILE}.tmp"

    with open(
        temporary,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "active": True,
            },
            file,
            indent=2,
        )

    os.replace(
        temporary,
        STATE_FILE,
    )


def clear_emergency_stop():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
