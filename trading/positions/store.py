"""
Persistent lightweight position tracking.

This stores bot-owned position metadata locally.
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


POSITIONS_FILE = ".trading_positions.json"


@dataclass
class Position:
    token_address: str
    symbol: str
    entry_price: float
    quantity: float
    invested_usd: float
    take_profit_multiple: float
    stop_loss_percent: float
    entry_signature: str = ""
    opened_at: str = ""


def _load_raw():
    if not os.path.exists(POSITIONS_FILE):
        return []

    try:
        with open(
            POSITIONS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except Exception:
        return []


def _save_raw(data):
    temporary = f"{POSITIONS_FILE}.tmp"

    with open(
        temporary,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
        )

    os.replace(
        temporary,
        POSITIONS_FILE,
    )


def load_positions():
    return _load_raw()


def open_position(
    token_address,
    symbol,
    entry_price,
    quantity,
    invested_usd,
    take_profit_multiple,
    stop_loss_percent,
    entry_signature="",
):
    positions = _load_raw()

    position = Position(
        token_address=token_address,
        symbol=symbol,
        entry_price=float(entry_price),
        quantity=float(quantity),
        invested_usd=float(invested_usd),
        take_profit_multiple=float(
            take_profit_multiple
        ),
        stop_loss_percent=float(
            stop_loss_percent
        ),
        entry_signature=entry_signature,
        opened_at=datetime.now(
            timezone.utc
        ).isoformat(),
    )

    positions.append(asdict(position))
    _save_raw(positions)

    return position


def remove_position(token_address):
    positions = [
        position
        for position in _load_raw()
        if position.get("token_address")
        != token_address
    ]

    _save_raw(positions)


def position_count():
    return len(_load_raw())
