def clip(
    value: int | float,
    lower: int | float,
    upper: int | float):
    return max(lower, min(value, upper))