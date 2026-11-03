"""Prototype for styling narrow wall remainders at explicitly known roof ends.

The generator must render ``trim`` as a plain, seamless fascia, and coordinate
node materials with adjacent walls. This function only partitions and labels.
"""

def vertical_modules(values, roof_elevations, trim_limit=1.0):
    """Yield (bottom, top, kind), preserving 3 m modules and all span ends.

    ``roof_elevations`` must contain only actual ceiling ends applicable to the
    wall or node being partitioned. Gate endpoints are not ceilings.
    """
    roofs = tuple(roof_elevations)
    for start, end in values:
        a = start
        while end - a > 1e-7:
            b = min(end, round(a + 3.0, 7))
            is_top = abs(b - end) < 1e-7
            is_roof = any(abs(end - roof) < 1e-6 for roof in roofs)
            kind = 'trim' if is_top and is_roof and b - a <= trim_limit + 1e-7 else 'panel'
            yield a, b, kind
            a = b
