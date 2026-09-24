from datetime import datetime, timezone


# ============================================================
# HELPERS
# ============================================================

def number(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def integer(value, default=0):
    """
    Safely convert a value to integer.
    """

    try:
        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# TOKEN AGE
# ============================================================

def get_token_age_minutes(token):
    """
    Calculate approximate age using last trade time.

    This is intentionally conservative because the token
    overview endpoint doesn't provide the original listing
    timestamp.
    """

    last_trade = token.get(
        "lastTradeUnixTime"
    )

    if not last_trade:
        return None

    try:

        now = datetime.now(
            timezone.utc
        ).timestamp()

        age_seconds = max(
            0,
            now - float(last_trade),
        )

        return age_seconds / 60

    except (TypeError, ValueError):

        return None


# ============================================================
# BUY/SELL PRESSURE
# ============================================================

def calculate_buy_pressure(token):
    """
    Calculate the percentage of recent trades that were buys.

    Uses 5-minute data.
    """

    buys = integer(
        token.get("buy5m")
    )

    sells = integer(
        token.get("sell5m")
    )

    total = buys + sells

    if total <= 0:
        return None

    return (
        buys / total
    ) * 100


# ============================================================
# SCORE
# ============================================================

def analyze_token(token):
    """
    Analyze a Birdeye token overview.

    Returns a structured risk/quality analysis.
    """

    score = 0
    reasons = []
    warnings = []

    # --------------------------------------------------------
    # LIQUIDITY — 20 POINTS
    # --------------------------------------------------------

    liquidity = number(
        token.get("liquidity")
    )

    if liquidity >= 10000:
        score += 20

    elif liquidity >= 5000:
        score += 16

    elif liquidity >= 2500:
        score += 12

    elif liquidity >= 1000:
        score += 8

    elif liquidity >= 500:
        score += 4

    else:
        reasons.append(
            "Very low liquidity"
        )

    # --------------------------------------------------------
    # BUY / SELL PRESSURE — 20 POINTS
    # --------------------------------------------------------

    buy_pressure = calculate_buy_pressure(
        token
    )

    if buy_pressure is None:

        warnings.append(
            "Insufficient 5m buy/sell data"
        )

    elif buy_pressure >= 70:

        score += 20

    elif buy_pressure >= 60:

        score += 16

    elif buy_pressure >= 50:

        score += 10

    elif buy_pressure >= 40:

        score += 5

    else:

        reasons.append(
            "Strong selling pressure"
        )

    # --------------------------------------------------------
    # TRADING ACTIVITY — 15 POINTS
    # --------------------------------------------------------

    trades_5m = integer(
        token.get("trade5m")
    )

    if trades_5m >= 50:
        score += 15

    elif trades_5m >= 25:
        score += 12

    elif trades_5m >= 10:
        score += 9

    elif trades_5m >= 5:
        score += 5

    elif trades_5m >= 1:
        score += 2

    else:

        reasons.append(
            "No recent trading activity"
        )

    # --------------------------------------------------------
    # UNIQUE WALLETS — 15 POINTS
    # --------------------------------------------------------

    wallets_5m = integer(
        token.get("uniqueWallet5m")
    )

    if wallets_5m >= 50:
        score += 15

    elif wallets_5m >= 25:
        score += 12

    elif wallets_5m >= 10:
        score += 9

    elif wallets_5m >= 5:
        score += 5

    elif wallets_5m >= 2:
        score += 2

    else:

        reasons.append(
            "Very few active wallets"
        )

    # --------------------------------------------------------
    # VOLUME — 10 POINTS
    # --------------------------------------------------------

    volume_5m = number(
        token.get("v5mUSD")
    )

    if volume_5m >= 10000:
        score += 10

    elif volume_5m >= 5000:
        score += 8

    elif volume_5m >= 2500:
        score += 6

    elif volume_5m >= 1000:
        score += 4

    elif volume_5m >= 100:
        score += 2

    else:

        reasons.append(
            "Very low 5m volume"
        )

    # --------------------------------------------------------
    # HOLDER ACTIVITY — 10 POINTS
    # --------------------------------------------------------

    holders = integer(
        token.get("holder")
    )

    if holders >= 500:
        score += 10

    elif holders >= 250:
        score += 8

    elif holders >= 100:
        score += 6

    elif holders >= 50:
        score += 4

    elif holders >= 10:
        score += 2

    else:

        reasons.append(
            "Very low holder count"
        )

    # --------------------------------------------------------
    # MARKET ACTIVITY — 5 POINTS
    # --------------------------------------------------------

    markets = integer(
        token.get("numberMarkets")
    )

    if markets >= 5:
        score += 5

    elif markets >= 3:
        score += 4

    elif markets >= 2:
        score += 2

    elif markets == 0:

        warnings.append(
            "No active markets reported"
        )

    # --------------------------------------------------------
    # SOURCE / TOKEN DATA — 5 POINTS
    # --------------------------------------------------------

    if token.get("address"):
        score += 2

    if token.get("symbol"):
        score += 1

    if token.get("name"):
        score += 1

    if token.get("decimals") is not None:
        score += 1

    # --------------------------------------------------------
    # AGE
    # --------------------------------------------------------

    age_minutes = get_token_age_minutes(
        token
    )

    if age_minutes is not None:

        if age_minutes < 5:

            warnings.append(
                "Extremely new token"
            )

        elif age_minutes > 1440:

            warnings.append(
                "Token is older than 24 hours"
            )

    # --------------------------------------------------------
    # FINAL CLASSIFICATION
    # --------------------------------------------------------

    if score >= 80:

        rating = "STRONG"

    elif score >= 65:

        rating = "WATCH"

    elif score >= 50:

        rating = "WEAK"

    else:

        rating = "REJECT"

    return {
        "score": score,
        "rating": rating,
        "liquidity": liquidity,
        "buy_pressure": buy_pressure,
        "trades_5m": trades_5m,
        "wallets_5m": wallets_5m,
        "volume_5m": volume_5m,
        "holders": holders,
        "markets": markets,
        "age_minutes": age_minutes,
        "reasons": reasons,
        "warnings": warnings,
    }


# ============================================================
# DISPLAY
# ============================================================

def print_analysis(token, analysis):
    """
    Print the token analysis in a readable format.
    """

    print()
    print(
        "=" * 60
    )

    print(
        "🧠 TOKEN ANALYSIS"
    )

    print(
        "=" * 60
    )

    print(
        f"Name:          {token.get('name', 'UNKNOWN')}"
    )

    print(
        f"Symbol:        {token.get('symbol', 'UNKNOWN')}"
    )

    print(
        f"Address:       {token.get('address', 'UNKNOWN')}"
    )

    print(
        f"Liquidity:     ${analysis['liquidity']:,.2f}"
    )

    print(
        f"5m Trades:     {analysis['trades_5m']}"
    )

    print(
        f"5m Wallets:    {analysis['wallets_5m']}"
    )

    print(
        f"5m Volume:     ${analysis['volume_5m']:,.2f}"
    )

    print(
        f"Holders:       {analysis['holders']}"
    )

    print(
        f"Markets:       {analysis['markets']}"
    )

    if analysis["buy_pressure"] is None:

        print(
            "Buy Pressure:  N/A"
        )

    else:

        print(
            f"Buy Pressure:  {analysis['buy_pressure']:.1f}%"
        )

    if analysis["age_minutes"] is None:

        print(
            "Age:            N/A"
        )

    else:

        print(
            f"Approx. Age:    {analysis['age_minutes']:.1f} min"
        )

    print()
    print(
        f"🎯 DEGEN SCORE: {analysis['score']}/100"
    )

    if analysis["rating"] == "STRONG":

        print(
            "🟢 STRONG CANDIDATE"
        )

    elif analysis["rating"] == "WATCH":

        print(
            "🟡 WATCH"
        )

    elif analysis["rating"] == "WEAK":

        print(
            "🟠 WEAK"
        )

    else:

        print(
            "🔴 REJECT"
        )

    if analysis["reasons"]:

        print()
        print(
            "Reasons:"
        )

        for reason in analysis["reasons"]:

            print(
                f"  • {reason}"
            )

    if analysis["warnings"]:

        print()
        print(
            "Warnings:"
        )

        for warning in analysis["warnings"]:

            print(
                f"  ⚠️ {warning}"
            )

    print()
    print(
        "🔴 LIVE TRADING: OFF"
    )

    print(
        "=" * 60
    )
