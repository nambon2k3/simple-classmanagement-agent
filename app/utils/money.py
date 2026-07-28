"""VND formatting helpers."""


def format_vnd(amount: int) -> str:
    """Format an integer amount as Vietnamese đồng with dot thousands separators."""
    sign = "-" if amount < 0 else ""
    digits = f"{abs(amount):,}".replace(",", ".")
    return f"{sign}{digits} VND"
