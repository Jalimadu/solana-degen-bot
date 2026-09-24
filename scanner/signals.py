"""
Stage 4 — Degen Signal Engine

This module generates trading candidates only.
It DOES NOT place trades.
LIVE TRADING remains OFF.
"""

from scanner.risk import number, integer


# ============================================================
# CONFIGURATION
# ============================================================

MIN_LIQUIDITY = 1000
MIN_5M_VOLUME = 500
MIN_5M_TRADES = 5
MIN_5M_WALLETS = 5

STRONG_LIQUIDITY = 5000
STRONG_VOLUME = 5000
STRONG_TRADES = 25
STRONG_WALLETS = 25


# ============================================================
# BUY PRESSURE
# ============================================================

def get_buy_pressure(data):
    """
    Calculate 5-minute buy pressure.
    """

    buys = integer(
        data.get("buy5m", 0)
    )

    sells = integer(
        data.get("sell5m", 0)
    )

    total = buys + sells

    if total <= 0:
        return None

    return (
        buys / total
    ) * 100


# ============================================================
# SIGNAL ENGINE
# ============================================================

def generate_signal(data, analysis):
    """
    Generate a Stage 4 degen signal.

    Returns a dictionary containing:
        signal
        confidence
        reasons
        warnings
    """

    liquidity = number(
        data.get("liquidity", 0)
    )

    volume_5m = number(
        data.get("v5mUSD", 0)
    )

    trades_5m = integer(
        data.get("trade5m", 0)
    )

    wallets_5m = integer(
        data.get("uniqueWallet5m", 0)
    )

    holders = integer(
        data.get("holder", 0)
    )

    markets = integer(
        data.get("numberMarkets", 0)
    )

    buy_pressure = get_buy_pressure(
        data
    )

    score = analysis.get(
        "score",
        0
    )

    reasons = []
    warnings = []

    points = 0

    # --------------------------------------------------------
    # LIQUIDITY
    # --------------------------------------------------------

    if liquidity >= STRONG_LIQUIDITY:

        points += 20

        reasons.append(
            "Strong liquidity"
        )

    elif liquidity >= MIN_LIQUIDITY:

        points += 10

        reasons.append(
            "Acceptable liquidity"
        )

    else:

        warnings.append(
            "Liquidity too low"
        )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    if volume_5m >= STRONG_VOLUME:

        points += 20

        reasons.append(
            "Strong 5m volume"
        )

    elif volume_5m >= MIN_5M_VOLUME:

        points += 10

        reasons.append(
            "5m volume is active"
        )

    else:

        warnings.append(
            "5m volume is weak"
        )

    # --------------------------------------------------------
    # TRADE ACTIVITY
    # --------------------------------------------------------

    if trades_5m >= STRONG_TRADES:

        points += 15

        reasons.append(
            "High trade activity"
        )

    elif trades_5m >= MIN_5M_TRADES:

        points += 8

        reasons.append(
            "Trade activity present"
        )

    else:

        warnings.append(
            "Very low trade activity"
        )

    # --------------------------------------------------------
    # WALLET ACTIVITY
    # --------------------------------------------------------

    if wallets_5m >= STRONG_WALLETS:

        points += 15

        reasons.append(
            "Strong wallet participation"
        )

    elif wallets_5m >= MIN_5M_WALLETS:

        points += 8

        reasons.append(
            "Multiple active wallets"
        )

    else:

        warnings.append(
            "Few active wallets"
        )

    # --------------------------------------------------------
    # BUY PRESSURE
    # --------------------------------------------------------

    if buy_pressure is not None:

        if buy_pressure >= 70:

            points += 20

            reasons.append(
                f"Strong buying pressure ({buy_pressure:.1f}%)"
            )

        elif buy_pressure >= 60:

            points += 12

            reasons.append(
                f"Positive buying pressure ({buy_pressure:.1f}%)"
            )

        elif buy_pressure >= 50:

            points += 5

            reasons.append(
                f"Buying pressure slightly positive ({buy_pressure:.1f}%)"
            )

        else:

            warnings.append(
                f"Selling pressure dominant ({buy_pressure:.1f}%)"
            )

    else:

        warnings.append(
            "Buy/sell pressure unavailable"
        )

    # --------------------------------------------------------
    # HOLDER CHECK
    # --------------------------------------------------------

    if holders >= 100:

        reasons.append(
            "Healthy holder count"
        )

    elif holders < 10:

        warnings.append(
            "Very low holder count"
        )

    # --------------------------------------------------------
    # MARKET CHECK
    # --------------------------------------------------------

    if markets >= 3:

        reasons.append(
            "Multiple markets detected"
        )

    elif markets == 0:

        warnings.append(
            "No market information"
        )

    # --------------------------------------------------------
    # COMBINE WITH STAGE 3 SCORE
    # --------------------------------------------------------

    combined_score = (
        int(score * 0.40)
        + int(points * 0.60)
    )

    # --------------------------------------------------------
    # SIGNAL DECISION
    # --------------------------------------------------------

    signal = "REJECT"

    if (
        combined_score >= 75
        and liquidity >= MIN_LIQUIDITY
        and volume_5m >= MIN_5M_VOLUME
        and trades_5m >= MIN_5M_TRADES
        and wallets_5m >= MIN_5M_WALLETS
        and buy_pressure is not None
        and buy_pressure >= 60
    ):

        signal = "STRONG SETUP"

    elif (
        combined_score >= 65
        and liquidity >= MIN_LIQUIDITY
        and volume_5m >= MIN_5M_VOLUME
        and buy_pressure is not None
        and buy_pressure >= 55
    ):

        signal = "SETUP"

    elif combined_score >= 50:

        signal = "WATCH"

    else:

        signal = "REJECT"

    return {
        "signal": signal,
        "confidence": combined_score,
        "buy_pressure": buy_pressure,
        "reasons": reasons,
        "warnings": warnings,
    }


# ============================================================
# PRINT SIGNAL
# ============================================================

def print_signal(signal_data):
    """
    Display Stage 4 signal.
    """

    print()
    print("=" * 60)
    print("🎯 STAGE 4 — DEGEN SIGNAL")
    print("=" * 60)

    signal = signal_data["signal"]
    confidence = signal_data["confidence"]

    print(
        f"Signal:       {signal}"
    )

    print(
        f"Confidence:   {confidence}/100"
    )

    pressure = signal_data[
        "buy_pressure"
    ]

    if pressure is not None:

        print(
            f"Buy Pressure: {pressure:.1f}%"
        )

    print()

    if signal_data["reasons"]:

        print("Positive Factors:")

        for reason in signal_data["reasons"]:

            print(
                f"  ✅ {reason}"
            )

    if signal_data["warnings"]:

        print()

        print("Warnings:")

        for warning in signal_data["warnings"]:

            print(
                f"  ⚠️ {warning}"
            )

    print()

    if signal == "STRONG SETUP":

        print(
            "🔥 STRONG DEGEN SETUP DETECTED"
        )

    elif signal == "SETUP":

        print(
            "🟢 POTENTIAL DEGEN SETUP"
        )

    elif signal == "WATCH":

        print(
            "🟡 KEEP ON WATCHLIST"
        )

    else:

        print(
            "🔴 NO TRADE SIGNAL"
        )

    print()

    # Safety lock.
    print(
        "🔴 LIVE TRADING: OFF"
    )

    print("=" * 60)
