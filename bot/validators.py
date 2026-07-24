"""
Input validation for order requests.

Keeping validation separate from the CLI and API layers means the same
rules can be reused (e.g. by a future web UI) and are easy to unit test.
"""

import re
from dataclasses import dataclass
from typing import Optional


class ValidationError(Exception):
    """Raised when user-supplied order input fails validation."""


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP"}  # STOP = bonus stop-limit order
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None


def validate_symbol(symbol: str) -> str:
    if not symbol:
        raise ValidationError("Symbol is required (e.g. BTCUSDT).")
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected an uppercase alphanumeric "
            f"pair like 'BTCUSDT'."
        )
    return symbol


def validate_side(side: str) -> str:
    if not side:
        raise ValidationError("Side is required (BUY or SELL).")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    if not order_type:
        raise ValidationError("Order type is required (MARKET, LIMIT, or STOP).")
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price, required: bool, field_name: str = "price") -> Optional[float]:
    if price is None:
        if required:
            raise ValidationError(f"{field_name} is required for this order type.")
        return None
    try:
        value = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number, got '{price}'.")
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0, got {value}.")
    return value


def build_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
    stop_price=None,
) -> OrderRequest:
    """
    Validate all raw CLI inputs together and return a clean OrderRequest.
    Raises ValidationError on the first failure encountered.
    """
    v_symbol = validate_symbol(symbol)
    v_side = validate_side(side)
    v_type = validate_order_type(order_type)
    v_qty = validate_quantity(quantity)

    v_price = validate_price(price, required=(v_type in {"LIMIT", "STOP"}), field_name="price")
    v_stop_price = validate_price(
        stop_price, required=(v_type == "STOP"), field_name="stop_price"
    )

    return OrderRequest(
        symbol=v_symbol,
        side=v_side,
        order_type=v_type,
        quantity=v_qty,
        price=v_price,
        stop_price=v_stop_price,
    )
