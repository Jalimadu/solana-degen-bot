"""
Solana Degen Bot — REST Launch Scanner

Stage 1:
    Discover newly listed Solana tokens.

Stage 2:
    Validate/filter candidates.

Stage 3:
    Risk and quality analysis.

Stage 4:
    Degen signal generation.

Stage 5:
    Momentum tracking and watchlist management.

IMPORTANT:
    LIVE TRADING IS DISABLED.
"""

import asyncio
import json
import time
import urllib.error
import urllib.parse
import urllib.request

from config import BIRDEYE_API_KEY

from scanner.filters import validate_token
from scanner.overview import get_token_overview
from scanner.risk import analyze_token, print_analysis
from scanner.signals import generate_signal, print_signal
from scanner.momentum import (
    analyze_momentum,
    print_momentum,
)
from scanner.watchlist import (
    add_token,
    get_due_tokens,
    get_token,
    update_token,
    remove_token,
    print_watchlist,
    size as watchlist_size,
)


# ============================================================
# CONFIGURATION
# ============================================================

BIRDEYE_LIST_URL = (
    "https://public-api.birdeye.so/defi/v2/tokens/new_listing"
)

CHAIN = "solana"

POLL_INTERVAL = 10

MAX_WATCHLIST_RECHECKS = 2

# Enable meme-platform discovery such as pump.fun.
MEME_PLATFORM_ENABLED = True

# Maximum number of new listings returned by Birdeye.
LISTING_LIMIT = 20


# ============================================================
# STATE
# ============================================================

seen_tokens = set()


# ============================================================
# FETCH NEW LISTINGS
# ============================================================

def fetch_new_listings():
    """
    Fetch newly listed Solana tokens from Birdeye.

    Uses Birdeye's dedicated new-listing endpoint rather than
    token_trending.

    This endpoint provides launch/listing information including
    liquidityAddedAt, which Stage 2 filters can use.
    """

    if not BIRDEYE_API_KEY:
        raise RuntimeError(
            "BIRDEYE_API_KEY is missing from .env"
        )

    params = {
        "limit": LISTING_LIMIT,
        "meme_platform_enabled": str(
            MEME_PLATFORM_ENABLED
        ).lower(),
    }

    url = (
        BIRDEYE_LIST_URL
        + "?"
        + urllib.parse.urlencode(params)
    )

    request = urllib.request.Request(
        url,
        headers={
            "X-API-KEY": BIRDEYE_API_KEY,
            "x-chain": CHAIN,
            "User-Agent": "Solana-Degen-Bot/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            body = response.read().decode("utf-8")

            data = json.loads(body)

            if not data.get("success", False):
                print()
                print(
                    "⚠️ Birdeye new-listing request "
                    "returned success=false."
                )
                return []

            result = data.get("data")

            if not result:
                print(
                    "⚠️ Birdeye returned empty "
                    "new-listing data."
                )
                return []

            # ------------------------------------------------
            # Birdeye normally returns the listings inside
            # data["items"].
            #
            # Keep fallback handling for different response
            # shapes so the scanner does not break if the API
            # wrapper changes slightly.
            # ------------------------------------------------

            if isinstance(result, dict):

                listings = (
                    result.get("items")
                    or result.get("tokens")
                    or result.get("data")
                    or []
                )

            elif isinstance(result, list):

                listings = result

            else:

                listings = []

            if not isinstance(listings, list):
                print(
                    "⚠️ Unexpected new-listing response "
                    "format from Birdeye."
                )
                return []

            return listings

    except urllib.error.HTTPError as error:

        print()
        print(
            f"⚠️ New-listing HTTP error: "
            f"{error.code}"
        )

        if error.code == 429:
            print(
                "⏳ Birdeye rate limit reached."
            )

        elif error.code == 401:
            print(
                "🔴 Birdeye API key is invalid "
                "or missing."
            )

        elif error.code == 403:
            print(
                "🔴 Birdeye rejected this API request."
            )

        return []

    except urllib.error.URLError as error:

        print()
        print(
            "⚠️ Birdeye connection error:"
        )
        print(repr(error))

        return []

    except json.JSONDecodeError:

        print()
        print(
            "⚠️ Birdeye returned invalid JSON."
        )

        return []

    except Exception as error:

        print()
        print(
            "⚠️ New-listing request failed:"
        )
        print(repr(error))

        return []


# ============================================================
# PROCESS ONE NEW TOKEN
# ============================================================

def process_token(token):
    """
    Run a newly discovered token through the full pipeline.

    Stage 1:
        New-listing discovery.

    Stage 2:
        Token validation.

    Stage 3:
        Risk/quality analysis.

    Stage 4:
        Signal generation.

    Stage 5:
        Add qualifying token to watchlist.
    """

    address = token.get("address")

    if not address:
        print()
        print(
            "⚠️ Listing skipped: "
            "missing token address."
        )
        return

    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    if address in seen_tokens:
        return

    # --------------------------------------------------------
    # STAGE 2 — FILTER
    # --------------------------------------------------------

    try:
        valid = validate_token(token)

    except Exception as error:

        print()
        print(
            "⚠️ Filter error:"
        )
        print(repr(error))

        return

    if not valid:
        return

    # --------------------------------------------------------
    # FETCH TOKEN OVERVIEW
    # --------------------------------------------------------

    print()
    print(
        "🔎 Fetching detailed token data..."
    )

    overview = get_token_overview(
        address
    )

    if not overview:

        print(
            "⚠️ Detailed overview unavailable."
        )

        # Do NOT mark it as seen.
        # This allows a later polling cycle to retry.
        return

    # The token has successfully entered
    # the processing pipeline.
    seen_tokens.add(address)

    # --------------------------------------------------------
    # STAGE 3 — RISK / QUALITY
    # --------------------------------------------------------

    print()
    print(
        "============================================================"
    )
    print(
        "🧠 STAGE 3 — RISK / QUALITY ANALYSIS"
    )
    print(
        "============================================================"
    )

    analysis = analyze_token(
        overview
    )

    print_analysis(overview, 
        analysis
    )

    # --------------------------------------------------------
    # STAGE 4 — DEGEN SIGNAL
    # --------------------------------------------------------

    print()
    print(
        "============================================================"
    )
    print(
        "⚡ STAGE 4 — DEGEN SIGNAL ENGINE"
    )
    print(
        "============================================================"
    )

    signal = generate_signal(
        overview,
        analysis,
    )

    print_signal(
        signal
    )

    classification = signal.get(
        "signal",
        "REJECT",
    )

    # --------------------------------------------------------
    # STAGE 5 — WATCHLIST
    # --------------------------------------------------------

    if classification in (
        "SETUP",
        "STRONG SETUP",
    ):

        print()
        print(
            "👀 Adding token to Stage 5 watchlist..."
        )

        added = add_token(
            address=address,
            token=token,
            overview=overview,
            signal_data=signal,
        )

        if added:

            print(
                "🟢 Token added to momentum watchlist."
            )

        else:

            print(
                "⚠️ Token was not added "
                "to the watchlist."
            )

    else:

        print()
        print(
            "⏭️ Token will not enter "
            "the Stage 5 watchlist."
        )

    # --------------------------------------------------------
    # TOKEN SUMMARY
    # --------------------------------------------------------

    print()
    print(
        "============================================================"
    )

    print(
        "🪙 TOKEN:"
    )

    print(
        f"Name: "
        f"{overview.get('name', 'Unknown')}"
    )

    print(
        f"Symbol: "
        f"{overview.get('symbol', 'Unknown')}"
    )

    print(
        f"Address: "
        f"{address}"
    )

    print(
        f"Liquidity: "
        f"${overview.get('liquidity', 0):,.2f}"
    )

    print(
        f"Classification: "
        f"{classification}"
    )

    print(
        f"Watchlist size: "
        f"{watchlist_size()}"
    )

    print(
        "🔴 LIVE TRADING: OFF"
    )

    print(
        "============================================================"
    )


# ============================================================
# PROCESS WATCHLIST
# ============================================================

def process_watchlist():
    """
    Recheck tokens whose momentum interval has expired.
    """

    due_tokens = get_due_tokens(
        limit=MAX_WATCHLIST_RECHECKS
    )

    if not due_tokens:
        return

    print()
    print(
        "============================================================"
    )
    print(
        "📈 STAGE 5 — MOMENTUM RECHECK"
    )
    print(
        "============================================================"
    )

    for address in due_tokens:

        entry = get_token(address)

        if not entry:
            continue

        old_overview = entry.get(
            "overview"
        )

        if not old_overview:
            continue

        print()
        print(
            f"🔄 Rechecking: "
            f"{entry.get('symbol', 'UNKNOWN')}"
        )

        print(
            f"Address: {address}"
        )

        # ----------------------------------------------------
        # FORCE REFRESH
        # ----------------------------------------------------

        new_overview = get_token_overview(
            address,
            force_refresh=True,
        )

        if not new_overview:

            print(
                "⚠️ Could not refresh token overview."
            )

            continue

        # ----------------------------------------------------
        # MOMENTUM ANALYSIS
        # ----------------------------------------------------

        momentum_result = analyze_momentum(
            old_overview,
            new_overview,
        )

        print_momentum(
            momentum_result
        )

        # ----------------------------------------------------
        # UPDATE WATCHLIST
        # ----------------------------------------------------

        update_token(
            address,
            new_overview,
            momentum_result,
        )

        classification = momentum_result.get(
            "signal",
            "FLAT",
        )

        # ----------------------------------------------------
        # COLLAPSING TOKEN
        # ----------------------------------------------------

        if classification == "COLLAPSING":

            print()
            print(
                "🔴 MOMENTUM COLLAPSING"
            )

            print(
                "🗑️ Removing token "
                "from watchlist."
            )

            remove_token(
                address,
                reason="Momentum collapsing",
            )

            continue

        # ----------------------------------------------------
        # MOMENTUM ALERTS
        # ----------------------------------------------------

        if classification == "ACCELERATING":

            print()
            print(
                "🚀 MOMENTUM ALERT: "
                "ACCELERATING"
            )

        elif classification == "IMPROVING":

            print()
            print(
                "🟢 MOMENTUM ALERT: "
                "IMPROVING"
            )

        elif classification == "WEAKENING":

            print()
            print(
                "🟡 MOMENTUM ALERT: "
                "WEAKENING"
            )

        elif classification == "FLAT":

            print()
            print(
                "⚪ MOMENTUM: FLAT"
            )

    print()

    print_watchlist()


# ============================================================
# MAIN SCANNER LOOP
# ============================================================

async def run_scanner():
    """
    Main REST scanner loop.
    """

    print()
    print(
        "🤖 Solana Degen Bot — REST Launch Scanner"
    )

    print(
        "============================================================"
    )

    print(
        "🟢 Birdeye REST API connected."
    )

    print(
        f"🔎 Polling every "
        f"{POLL_INTERVAL} seconds..."
    )

    print(
        "🟢 New-token discovery: ON"
    )

    print(
        "🟢 Meme-platform discovery: ON"
    )

    print(
        "🟢 Stage 5 momentum tracking: ON"
    )

    print(
        "🔴 Live trading: OFF"
    )

    print(
        "============================================================"
    )

    while True:

        try:

            # ------------------------------------------------
            # NEW LISTINGS
            # ------------------------------------------------

            listings = fetch_new_listings()

            print()

            print(
                f"📦 Birdeye returned "
                f"{len(listings)} new listings."
            )

            for token in listings:

                try:

                    process_token(
                        token
                    )

                except Exception as error:

                    print()
                    print(
                        "⚠️ Token processing error:"
                    )
                    print(
                        repr(error)
                    )

            # ------------------------------------------------
            # STAGE 5 WATCHLIST
            # ------------------------------------------------

            try:

                process_watchlist()

            except Exception as error:

                print()
                print(
                    "⚠️ Watchlist processing error:"
                )
                print(
                    repr(error)
                )

            # ------------------------------------------------
            # WAIT
            # ------------------------------------------------

            print()
            print(
                f"⏳ Next scan in "
                f"{POLL_INTERVAL} seconds..."
            )

            await asyncio.sleep(
                POLL_INTERVAL
            )

        except KeyboardInterrupt:

            print()
            print(
                "🛑 Scanner stopped by user."
            )

            print(
                "🔴 LIVE TRADING: OFF"
            )

            break

        except Exception as error:

            print()
            print(
                "⚠️ Scanner loop error:"
            )
            print(
                repr(error)
            )

            await asyncio.sleep(
                POLL_INTERVAL
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        run_scanner()
    )
