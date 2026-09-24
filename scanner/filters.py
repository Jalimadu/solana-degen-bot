# ============================================================
# TOKEN FILTERS
# ============================================================

def validate_token(token):
    """
    Perform basic safety and quality checks on a newly
    detected token.

    Returns:
        (True, "PASSED") if the token qualifies.
        (False, reason) if it should be rejected.
    """

    # --------------------------------------------------------
    # TOKEN ADDRESS
    # --------------------------------------------------------

    address = token.get("address")

    if not address:
        return False, "Missing token address"

    # --------------------------------------------------------
    # TOKEN NAME
    # --------------------------------------------------------

    name = token.get("name")

    if not name:
        return False, "Missing token name"

    # --------------------------------------------------------
    # TOKEN SYMBOL
    # --------------------------------------------------------

    symbol = token.get("symbol")

    if not symbol:
        return False, "Missing token symbol"

    # --------------------------------------------------------
    # LIQUIDITY
    # --------------------------------------------------------

    liquidity = token.get("liquidity")

    if liquidity is None:
        return False, "Liquidity data unavailable"

    try:
        liquidity = float(liquidity)

    except (TypeError, ValueError):
        return False, "Invalid liquidity value"

    if liquidity <= 0:
        return False, "Zero liquidity"

    # --------------------------------------------------------
    # LISTING TIME
    # --------------------------------------------------------

    listed_at = token.get("liquidityAddedAt")

    if not listed_at:
        return False, "Missing listing timestamp"

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    source = token.get("source")

    if not source:
        return False, "Unknown token source"

    # --------------------------------------------------------
    # PASSED
    # --------------------------------------------------------

    return True, "PASSED"
