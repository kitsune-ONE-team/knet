def lerp(a: float, b: float, factor: float) -> float:
    return a * (1 - factor) + b * factor


def lerp3(a: tuple[float], b: tuple[float], factor: float) -> tuple[float]:
    return (
        lerp(a[0], b[0], factor),
        lerp(a[1], b[1], factor),
        lerp(a[2], b[2], factor),
    )


def add3(a: tuple[float], b: tuple[float]) -> tuple[float]:
    return (
        a[0] + b[0],
        a[1] + b[1],
        a[2] + b[2],
    )


def div3(a: tuple[float], b: tuple[float]) -> tuple[float]:
    return (
        a[0] / b[0],
        a[1] / b[1],
        a[2] / b[2],
    )
