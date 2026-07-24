"""
Order placement logic.

This module knows how to turn a validated OrderRequest into a Binance
Futures API call, log the request/response, and normalize the result into
a plain dict the CLI can print — regardless of order type.
"""

from typing import Any, Dict

from binance.client import Client

from bot.client import API_EXCEPTIONS, BinanceClientError
from bot.logging_config import logger
from bot.validators import OrderRequest


class OrderExecutionError(Exception):
    """Raised when the exchange rejects an order or a network error occurs."""


def _summarize_request(order: OrderRequest) -> Dict[str, Any]:
    summary = {
        "symbol": order.symbol,
        "side": order.side,
        "type": order.order_type,
        "quantity": order.quantity,
    }
    if order.price is not None:
        summary["price"] = order.price
    if order.stop_price is not None:
        summary["stopPrice"] = order.stop_price
    return summary


def _summarize_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Pull out the fields the task explicitly asks us to display."""
    return {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
    }


def place_order(client: Client, order: OrderRequest) -> Dict[str, Any]:
    """
    Submit a MARKET, LIMIT, or STOP (stop-limit) order to Binance Futures
    Testnet. Returns a dict with 'request', 'response', and 'success' keys
    so the CLI layer can print a consistent report regardless of outcome.
    """
    request_summary = _summarize_request(order)
    logger.info("Order request: %s", request_summary)

    try:
        kwargs: Dict[str, Any] = {
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
        }

        if order.order_type == "LIMIT":
            kwargs["price"] = order.price
            kwargs["timeInForce"] = "GTC"  # Good-Til-Cancelled: required for LIMIT orders
        elif order.order_type == "STOP":
            # Bonus order type: stop-limit. Triggers a LIMIT order once
            # stopPrice is reached.
            kwargs["price"] = order.price
            kwargs["stopPrice"] = order.stop_price
            kwargs["timeInForce"] = "GTC"

        response = client.futures_create_order(**kwargs)
        logger.info("Order response: %s", response)

        return {
            "request": request_summary,
            "response": _summarize_response(response),
            "raw_response": response,
            "success": True,
            "error": None,
        }

    except API_EXCEPTIONS as exc:
        # Exchange-level rejection: bad symbol, insufficient margin,
        # invalid price/quantity precision, rate limits, etc.
        logger.error("Binance API rejected order %s: %s", request_summary, exc)
        return {
            "request": request_summary,
            "response": None,
            "raw_response": None,
            "success": False,
            "error": str(exc),
        }

    except BinanceClientError as exc:
        logger.error("Client configuration error for order %s: %s", request_summary, exc)
        return {
            "request": request_summary,
            "response": None,
            "raw_response": None,
            "success": False,
            "error": str(exc),
        }

    except Exception as exc:  # noqa: BLE001 - network drops, timeouts, DNS issues, etc.
        logger.error("Unexpected/network error placing order %s: %s", request_summary, exc)
        return {
            "request": request_summary,
            "response": None,
            "raw_response": None,
            "success": False,
            "error": f"Network or unexpected error: {exc}",
        }
