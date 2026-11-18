from statistics import mean


def mae(predicted: list[float], reference: list[float]) -> float:
    _check(predicted, reference)
    return round(mean(abs(p - r) for p, r in zip(predicted, reference)), 3)


def exact_agreement(predicted: list[int], reference: list[int]) -> float:
    _check(predicted, reference)
    return round(sum(p == r for p, r in zip(predicted, reference)) / len(predicted), 3)


def within_one_agreement(predicted: list[int], reference: list[int]) -> float:
    _check(predicted, reference)
    return round(sum(abs(p - r) <= 1 for p, r in zip(predicted, reference)) / len(predicted), 3)


def pearson(x: list[float], y: list[float]) -> float:
    _check(x, y)
    mx, my = mean(x), mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return round(num / den, 3) if den else 0.0


def evidence_rate(verified_flags: list[bool]) -> float:
    return round(sum(verified_flags) / len(verified_flags), 3) if verified_flags else 0.0


def summary(predicted: list[int], reference: list[int]) -> dict:
    return {
        "n": len(predicted),
        "mae": mae(predicted, reference),
        "exact": exact_agreement(predicted, reference),
        "within_one": within_one_agreement(predicted, reference),
        "pearson": pearson(predicted, reference),
    }


def _check(a: list, b: list) -> None:
    if not a or len(a) != len(b):
        raise ValueError("Lists must be non-empty and of equal length")
