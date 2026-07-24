"""
Thin wrapper around python-binance's Client, pinned to the Binance Futures
Testnet (USDT-M). Keeping this isolated means orders.py and cli.py never
talk to the network directly — everything goes through here, which is
where auth, base-URL, and connectivity concerns live.
"""

import os

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException
from dotenv import load_dotenv

from bot.logging_config import logger

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the client cannot be created or a request fails at the network level."""


def load_credentials() -> tuple[str, str]:
    """
    Load API key/secret from environment variables (via .env or the shell).
    Never hard-code credentials — see README.md for setup.
    """
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise BinanceClientError(
            "Missing BINANCE_API_KEY / BINANCE_API_SECRET. Set them in a .env file "
            "or as environment variables. See README.md for setup steps."
        )
    return api_key, api_secret


def get_futures_testnet_client() -> Client:
    """
    Build a python-binance Client pointed at the Futures Testnet.

    python-binance's `testnet=True` flag switches the *futures* endpoints to
    the testnet host, but we also set FUTURES_URL explicitly so behaviour is
    correct even if the installed library version handles the flag
    differently.
    """
    api_key, api_secret = load_credentials()

    try:
        client = Client(api_key, api_secret, testnet=True)
        client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"
        logger.info("Initialized Binance Futures Testnet client (base_url=%s)", client.FUTURES_URL)
        return client
    except Exception as exc:  # noqa: BLE001 - surface any client construction failure clearly
        logger.error("Failed to initialize Binance client: %s", exc)
        raise BinanceClientError(f"Failed to initialize Binance client: {exc}") from exc


# Re-exported so callers (orders.py) can catch a single, well-known set of
# exceptions without importing the binance package directly.
API_EXCEPTIONS = (BinanceAPIException, BinanceOrderException, BinanceRequestException)
