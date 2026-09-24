"""
Stage 5 — Momentum Tracker

Tracks changes in a token's metrics over time.

NO trading execution happens here.
"""

from scanner.risk import number, integer


# ============================================================
# METRIC EXTRACTION
# ============================================================

def snapshot(data):
    """
    Extract the metrics we care about.
    """

    buys = integer(
        data.get("buy5m", 0)
    )

    sells = integer(
        data.get("sell5m", 0)
    )

    total_trades = (
        buys + sells
    )

    if total_trades > 0:
        buy_pressure = (
            buys / total_trades
        ) * 100
    else:
        buy_pressure = None

    return {
        "liquidity": number(
            data.get("liquidity", 0)
        ),

        "volume_5m": number(
            data.get("v5mUSD", 0)
        ),

        "trades_5m": integer(
            data.get("trade5m", 0)
        ),

        "wallets_5m": integer(
            data.get("uniqueWallet5m", 0)
        ),

        "holders": integer(
            data.get("holder", 0)
        ),

        "buy_pressure": buy_pressure,
    }


# ============================================================
# PERCENTAGE CHANGE
# ============================================================

def percent_change(old, new):
    """
    Calculate percentage change safely.
    """

    if old is None or new is None:
        return None

    if old == 0:

        if new > 0:
            return 100.0

        return 0.0

    return (
        (new - old)
        / abs(old)
    ) * 100


# ============================================================
# COMPARE SNAPSHOTS
# ============================================================

def compare_snapshots(old, new):
    """
    Compare two token snapshots.
    """

    changes = {}

    for field in [
        "liquidity",
        "volume_5m",
        "trades_5m",
        "wallets_5m",
        "holders",
        "buy_pressure",
    ]:

        changes[field] = percent_change(
            old.get(field),
            new.get(field),
        )

    return changes


# ============================================================
# MOMENTUM SCORE
# ============================================================

def calculate_momentum(
    old,
    new,
    changes,
):
    """
    Calculate momentum score from -100 to +100.
    """

    score = 0

    # --------------------------------------------------------
    # LIQUIDITY
    # --------------------------------------------------------

    liquidity_change = changes[
        "liquidity"
    ]

    if liquidity_change is not None:

        if liquidity_change >= 20:
            score += 15

        elif liquidity_change >= 5:
            score += 8

        elif liquidity_change <= -20:
            score -= 15

        elif liquidity_change <= -5:
            score -= 8

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_change = changes[
        "volume_5m"
    ]

    if volume_change is not None:

        if volume_change >= 50:
            score += 25

        elif volume_change >= 20:
            score += 15

        elif volume_change >= 5:
            score += 7

        elif volume_change <= -30:
            score -= 20

        elif volume_change <= -10:
            score -= 10

    # --------------------------------------------------------
    # TRADES
    # --------------------------------------------------------

    trade_change = changes[
        "trades_5m"
    ]

    if trade_change is not None:

        if trade_change >= 50:
            score += 20

        elif trade_change >= 20:
            score += 12

        elif trade_change >= 5:
            score += 5

        elif trade_change <= -30:
            score -= 15

    # --------------------------------------------------------
    # WALLETS
    # --------------------------------------------------------

    wallet_change = changes[
        "wallets_5m"
    ]

    if wallet_change is not None:

        if wallet_change >= 50:
            score += 20

        elif wallet_change >= 20:
            score += 12

        elif wallet_change >= 5:
            score += 5

        elif wallet_change <= -30:
            score -= 15

    # --------------------------------------------------------
    # HOLDERS
    # --------------------------------------------------------

    holder_change = changes[
        "holders"
    ]

    if holder_change is not None:

        if holder_change >= 20:
            score += 10

        elif holder_change >= 5:
            score += 5

        elif holder_change <= -10:
            score -= 10

    # --------------------------------------------------------
    # BUY PRESSURE
    # --------------------------------------------------------

    old_pressure = old.get(
        "buy_pressure"
    )

    new_pressure = new.get(
        "buy_pressure"
    )

    if (
        old_pressure is not None
        and new_pressure is not None
    ):

        pressure_delta = (
            new_pressure
            - old_pressure
        )

        if pressure_delta >= 10:
            score += 15

        elif pressure_delta >= 5:
            score += 8

        elif pressure_delta <= -10:
            score -= 15

        elif pressure_delta <= -5:
            score -= 8

    # Keep score bounded.
    return max(
        -100,
        min(100, score)
    )


# ============================================================
# MOMENTUM CLASSIFICATION
# ============================================================

def classify_momentum(score):

    if score >= 50:
        return "ACCELERATING"

    if score >= 20:
        return "IMPROVING"

    if score <= -40:
        return "COLLAPSING"

    if score <= -15:
        return "WEAKENING"

    return "FLAT"


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def analyze_momentum(old_data, new_data):

    old = snapshot(
        old_data
    )

    new = snapshot(
        new_data
    )

    changes = compare_snapshots(
        old,
        new
    )

    score = calculate_momentum(
        old,
        new,
        changes
    )

    classification = (
        classify_momentum(score)
    )

    return {
        "old": old,
        "new": new,
        "changes": changes,
        "score": score,
        "classification": classification,
    }


# ============================================================
# PRINT
# ============================================================

def print_momentum(result):

    print()
    print("=" * 60)
    print("📈 STAGE 5 — MOMENTUM")
    print("=" * 60)

    print(
        f"Momentum:    {result['classification']}"
    )

    print(
        f"Momentum Score: {result['score']}/100"
    )

    changes = result["changes"]

    labels = {
        "liquidity": "Liquidity",
        "volume_5m": "5m Volume",
        "trades_5m": "5m Trades",
        "wallets_5m": "5m Wallets",
        "holders": "Holders",
        "buy_pressure": "Buy Pressure",
    }

    for key, label in labels.items():

        value = changes.get(key)

        if value is None:
            continue

        sign = "+" if value >= 0 else ""

        print(
            f"{label:15}: {sign}{value:.1f}%"
        )

    print()

    if result["classification"] == "ACCELERATING":

        print(
            "🚀 MOMENTUM ACCELERATING"
        )

    elif result["classification"] == "IMPROVING":

        print(
            "🟢 MOMENTUM IMPROVING"
        )

    elif result["classification"] == "WEAKENING":

        print(
            "🟠 MOMENTUM WEAKENING"
        )

    elif result["classification"] == "COLLAPSING":

        print(
            "🔴 MOMENTUM COLLAPSING"
        )

    else:

        print(
            "⚪ MOMENTUM FLAT"
        )

    print()
    print(
        "🔴 LIVE TRADING: OFF"
    )

    print("=" * 60)
