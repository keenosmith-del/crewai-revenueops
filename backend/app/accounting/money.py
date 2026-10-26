from decimal import Decimal, InvalidOperation

# Explicitly supported ISO 4217 subset. No conversion or implicit rounding.
PRECISION = {"ZAR": 2, "USD": 2, "EUR": 2, "GBP": 2, "JPY": 0, "KWD": 3}


def money(value, currency):
    if currency not in PRECISION:
        raise ValueError("Unsupported ISO currency")
    if not isinstance(value, (str, Decimal, int)) or isinstance(value, bool):
        raise ValueError("Money must be decimal text")
    try:
        amount = Decimal(value)
        unit = Decimal(10) ** -PRECISION[currency]
        if not amount.is_finite() or abs(amount) >= Decimal("1000000000000"):
            raise ValueError("Amount outside supported range")
        if amount.quantize(unit) != amount:
            raise ValueError("Unsupported currency precision")
        return amount.quantize(unit)
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal amount") from exc
