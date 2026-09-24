"""
Birdeye Token Overview Client

Fetches detailed Solana token data from Birdeye.

Features:
- API authentication
- Request spacing
- HTTP 429 retry/backoff
- Optional caching
- Force-refresh support for Stage 5 momentum tracking

NO trading execution happens here.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

from config import BIRDEYE_API_KEY


BIRDEYE_OVERVIEW_URL = (
    "https://public-api.birdeye.so/defi/token_overview"
)

CHAIN = "solana"

REQUEST_INTERVAL = 2.5
MAX_RETRIES = 3
CACHE_TTL = 300

_last_request_time = 0.0
_overview_cache = {}


def wait_for_request_slot():
    global _last_request_time

    now = time.monotonic()
    elapsed = now - _last_request_time

    if elapsed < REQUEST_INTERVAL:
        wait_time = REQUEST_INTERVAL - elapsed

        print(
            f"⏳ Birdeye request spacing: "
            f"waiting {wait_time:.1f}s..."
        )

        time.sleep(wait_time)

    _last_request_time = time.monotonic()


def get_token_overview(
    address,
    force_refresh=False,
):
    """
    Retrieve detailed token information from Birdeye.

    force_refresh=True bypasses the local cache.
    """

    if not BIRDEYE_API_KEY:
        raise RuntimeError(
            "BIRDEYE_API_KEY is missing from .env"
        )

    if not address:
        return None

    # --------------------------------------------------------
    # CACHE
    # --------------------------------------------------------

    if not force_refresh:

        cached = _overview_cache.get(address)

        if cached:

            cached_time, cached_data = cached

            age = (
                time.monotonic()
                - cached_time
            )

            if age < CACHE_TTL:

                print(
                    "📦 Using cached token overview."
                )

                return cached_data

            del _overview_cache[address]

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    params = {
        "address": address,
    }

    url = (
        BIRDEYE_OVERVIEW_URL
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

    # --------------------------------------------------------
    # RETRIES
    # --------------------------------------------------------

    for attempt in range(MAX_RETRIES + 1):

        wait_for_request_slot()

        try:

            with urllib.request.urlopen(
                request,
                timeout=20,
            ) as response:

                body = (
                    response
                    .read()
                    .decode("utf-8")
                )

                data = json.loads(body)

                if not data.get(
                    "success",
                    False,
                ):

                    print(
                        "⚠️ Birdeye overview "
                        "returned success=false."
                    )

                    return None

                overview = data.get("data")

                if not overview:

                    print(
                        "⚠️ Birdeye returned "
                        "empty overview data."
                    )

                    return None

                # Save fresh data in cache.
                _overview_cache[address] = (
                    time.monotonic(),
                    overview,
                )

                return overview

        except urllib.error.HTTPError as error:

            if error.code == 429:

                if attempt >= MAX_RETRIES:

                    print()
                    print(
                        "🔴 Birdeye rate limit "
                        "still active after retries."
                    )

                    return None

                backoff = (
                    5 * (2 ** attempt)
                )

                print()
                print(
                    "⚠️ Birdeye rate limit "
                    "(HTTP 429)."
                )

                print(
                    f"⏳ Backing off for "
                    f"{backoff}s..."
                )

                time.sleep(backoff)

                continue

            print()
            print(
                f"⚠️ Overview HTTP error: "
                f"{error.code}"
            )

            return None

        except json.JSONDecodeError:

            print(
                "⚠️ Invalid JSON received "
                "from Birdeye."
            )

            return None

        except Exception as error:

            print()
            print(
                "⚠️ Overview request failed:"
            )

            print(repr(error))

            return None

    return None
