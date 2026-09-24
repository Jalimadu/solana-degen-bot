import asyncio
import json

import websockets
from websockets.exceptions import (
    ConnectionClosed,
    WebSocketException,
)

from config import BIRDEYE_API_KEY


# ============================================================
# CONFIGURATION
# ============================================================

BIRDEYE_WS_URL = (
    "wss://public-api.birdeye.so/socket/solana"
)

ORIGIN = "ws://public-api.birdeye.so"

RECONNECT_DELAY = 10


# ============================================================
# BIRDEYE WEBSOCKET CONNECTION
# ============================================================

async def connect_to_birdeye():
    """
    Connect to Birdeye's Solana WebSocket.
    """

    if not BIRDEYE_API_KEY:
        raise RuntimeError(
            "BIRDEYE_API_KEY is missing from .env"
        )

    websocket_url = (
        f"{BIRDEYE_WS_URL}"
        f"?x-api-key={BIRDEYE_API_KEY}"
    )

    print("🔌 Connecting to Birdeye...")

    websocket = await websockets.connect(
        websocket_url,
        origin=ORIGIN,
        subprotocols=["echo-protocol"],
        proxy=None,
        ping_interval=20,
        ping_timeout=20,
        open_timeout=15,
    )

    print("🟢 Birdeye WebSocket connected.")

    return websocket


# ============================================================
# SUBSCRIBE TO NEW TOKEN LISTINGS
# ============================================================

async def subscribe_to_new_tokens(websocket):
    """
    Subscribe to Birdeye's new-token-listing stream.
    """

    subscription = {
        "type": "SUBSCRIBE_TOKEN_NEW_LISTING"
    }

    message = json.dumps(subscription)

    await websocket.send(message)

    print("🟢 New-token subscription sent.")
    print(
        "🔎 Waiting for new Solana token listings..."
    )
    print("🔴 Live trading remains OFF.")


# ============================================================
# PROCESS BIRDEYE MESSAGES
# ============================================================

async def process_message(message):
    """
    Process one message received from Birdeye.
    """

    # --------------------------------------------------------
    # Convert message to JSON
    # --------------------------------------------------------

    try:
        data = json.loads(message)

    except json.JSONDecodeError:
        print(
            "⚠️ Received a non-JSON message:"
        )
        print(message)
        return

    # --------------------------------------------------------
    # Identify event type
    # --------------------------------------------------------

    event_type = data.get("type")

    print(
        f"📡 Event: {event_type}"
    )

    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    if event_type == "WELCOME":

        print(
            "🤝 Birdeye welcome received."
        )

        return

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if event_type == "ERROR":

        print()
        print(
            "❌ BIRDEYE RETURNED AN ERROR"
        )
        print(
            "=" * 60
        )

        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            )
        )

        print(
            "=" * 60
        )

        return

    # --------------------------------------------------------
    # NEW TOKEN LISTING
    # --------------------------------------------------------

    if event_type == "TOKEN_NEW_LISTING_DATA":

        print()
        print(
            "🚨 NEW TOKEN LISTING"
        )
        print(
            "=" * 60
        )

        token_data = data.get(
            "data",
            {}
        )

        print(
            json.dumps(
                token_data,
                indent=2,
                ensure_ascii=False,
            )
        )

        print(
            "=" * 60
        )

        return

    # --------------------------------------------------------
    # OTHER EVENTS
    # --------------------------------------------------------

    print(
        "📦 Full event:"
    )

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
    )


# ============================================================
# LISTEN FOR EVENTS
# ============================================================

async def listen_for_events(websocket):
    """
    Continuously listen for messages from Birdeye.
    """

    while True:

        try:

            message = await websocket.recv()

            await process_message(
                message
            )

        except ConnectionClosed as error:

            print()
            print(
                "⚠️ Birdeye WebSocket connection closed."
            )

            print(
                f"Close code: {error.code}"
            )

            print(
                f"Close reason: {error.reason}"
            )

            raise

        except WebSocketException:

            raise

        except Exception as error:

            print()
            print(
                "⚠️ Error processing WebSocket message:"
            )

            print(
                f"{type(error).__name__}: {error}"
            )


# ============================================================
# MAIN SCANNER
# ============================================================

async def run_scanner():

    print()
    print(
        "🤖 Solana Degen Bot — Launch Scanner"
    )

    print(
        "=" * 60
    )

    while True:

        websocket = None

        try:

            # ------------------------------------------------
            # CONNECT
            # ------------------------------------------------

            websocket = (
                await connect_to_birdeye()
            )

            # ------------------------------------------------
            # SUBSCRIBE
            # ------------------------------------------------

            await subscribe_to_new_tokens(
                websocket
            )

            # ------------------------------------------------
            # LISTEN
            # ------------------------------------------------

            await listen_for_events(
                websocket
            )

        except KeyboardInterrupt:

            print()
            print(
                "🛑 Scanner stopped by user."
            )

            break

        except Exception as error:

            print()
            print(
                "⚠️ Scanner connection problem:"
            )

            print(
                f"{type(error).__name__}: {error}"
            )

            print()
            print(
                f"🔄 Retrying in {RECONNECT_DELAY} seconds..."
            )

            await asyncio.sleep(
                RECONNECT_DELAY
            )

        finally:

            if websocket is not None:

                try:
                    await websocket.close()

                except Exception:
                    pass


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

def main():

    try:

        asyncio.run(
            run_scanner()
        )

    except KeyboardInterrupt:

        print()
        print(
            "🛑 Scanner stopped."
        )


if __name__ == "__main__":

    main()