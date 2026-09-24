"""
Stage 5 — Token Watchlist

Stores promising tokens from Stage 4 so they can be
re-checked periodically by the Momentum Tracker.

NO trading execution happens here.
"""

import time


# ============================================================
# CONFIGURATION
# ============================================================

RECHECK_INTERVAL = 60
MAX_WATCHLIST_SIZE = 20


# ============================================================
# WATCHLIST STORAGE
# ============================================================

watchlist = {}


# ============================================================
# ADD TOKEN
# ============================================================

def add_token(
    address,
    token,
    overview,
    signal_data,
):
    """
    Add a promising token to the watchlist.
    """

    if not address:
        return False

    if len(watchlist) >= MAX_WATCHLIST_SIZE:
        print()
        print("⚠️ Watchlist is full.")
        return False

    if address in watchlist:
        return False

    classification = signal_data.get(
        "signal",
        "UNKNOWN",
    )

    if classification not in (
        "SETUP",
        "STRONG SETUP",
    ):
        return False

    watchlist[address] = {
        "address": address,
        "symbol": token.get("symbol", "UNKNOWN"),
        "name": token.get("name", "UNKNOWN"),
        "source": token.get("source", "UNKNOWN"),
        "added_at": time.monotonic(),
        "last_checked": time.monotonic(),
        "overview": overview,
        "signal": signal_data,
        "checks": 0,
        "momentum": None,
    }

    print()
    print("👀 TOKEN ADDED TO WATCHLIST")
    print(
        f"   {token.get('symbol', 'UNKNOWN')} "
        f"— {classification}"
    )
    print(
        f"   Watchlist size: "
        f"{len(watchlist)}/{MAX_WATCHLIST_SIZE}"
    )

    return True


# ============================================================
# GET DUE TOKENS
# ============================================================

def get_due_tokens(limit=2):
    """
    Return tokens that are due for a fresh overview request.
    """

    now = time.monotonic()

    due = []

    for address, item in watchlist.items():

        elapsed = (
            now - item["last_checked"]
        )

        if elapsed >= RECHECK_INTERVAL:
            due.append(address)

    due.sort(
        key=lambda address:
        watchlist[address]["last_checked"]
    )

    return due[:limit]


# ============================================================
# UPDATE TOKEN
# ============================================================

def update_token(
    address,
    overview,
    momentum_result,
):
    """
    Store the newest overview and momentum result.
    """

    if address not in watchlist:
        return False

    item = watchlist[address]

    item["overview"] = overview
    item["momentum"] = momentum_result
    item["last_checked"] = time.monotonic()
    item["checks"] += 1

    return True


# ============================================================
# REMOVE TOKEN
# ============================================================

def remove_token(
    address,
    reason="",
):
    """
    Remove a token from the watchlist.
    """

    if address not in watchlist:
        return False

    item = watchlist[address]

    print()
    print("🗑️ TOKEN REMOVED FROM WATCHLIST")
    print(
        f"   {item['symbol']} "
        f"— {item['name']}"
    )

    if reason:
        print(
            f"   Reason: {reason}"
        )

    del watchlist[address]

    return True


# ============================================================
# GET TOKEN
# ============================================================

def get_token(address):
    """
    Return watchlist data for a token.
    """

    return watchlist.get(address)


# ============================================================
# PRINT WATCHLIST
# ============================================================

def print_watchlist():
    """
    Display the current watchlist.
    """

    print()
    print("=" * 60)
    print("👀 STAGE 5 — WATCHLIST")
    print("=" * 60)

    if not watchlist:
        print("Watchlist: EMPTY")
        print("=" * 60)
        return

    print(
        f"Watching {len(watchlist)} "
        f"token(s)"
    )

    print()

    for address, item in watchlist.items():

        momentum = item.get(
            "momentum"
        )

        if momentum:
            classification = momentum.get(
                "classification",
                "UNKNOWN",
            )

            score = momentum.get(
                "score",
                0,
            )
        else:
            classification = "WAITING"
            score = 0

        print(
            f"🪙 {item['symbol']} "
            f"— {classification} "
            f"({score:+d})"
        )

        print(
            f"   Checks: {item['checks']}"
        )

        print(
            f"   Address: {address}"
        )

    print()
    print("=" * 60)


# ============================================================
# WATCHLIST SIZE
# ============================================================

def size():
    """
    Return current watchlist size.
    """

    return len(watchlist)
