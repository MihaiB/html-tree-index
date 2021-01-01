"""
Express an amount in a different unit.
"""


def approximate(amount, units):
    """
    Express amount in the largest suitable unit using integer division.

    amount: int
    units: {multiple (int): name (string)}, must include the key ‘1’.

    Returns (value, unit_name)

    Fails for negative values
    >>> approximate(-1, {1: 'm'})
    Traceback (most recent call last):
    ValueError: negative values are not supported

    Requires the multiple 1
    >>> approximate(30, {})
    Traceback (most recent call last):
    ValueError: the multiple 1 is missing
    >>> approximate(30, {7: 'week'})
    Traceback (most recent call last):
    ValueError: the multiple 1 is missing

    Rejects a multiple whose value is 0
    >>> approximate(30, {1: 'day', 7: 'week', 0: 'z3r0', 14: 'fortnight'})
    Traceback (most recent call last):
    ValueError: multiple ≤ 0

    Rejects negative multiples
    >>> approximate(6, {1: '1', 8: '8', -2: '-2', 5: '5'})
    Traceback (most recent call last):
    ValueError: multiple ≤ 0

    Returns amount if the only multiple is 1
    >>> approximate(3600, {1: 's'})
    (3600, 's')

    Returns the (0, unit mulitple) if amount=0
    >>> approximate(0, {1: 'm', 1000: 'km'})
    (0, 'm')

    Integer divides to the largest unit at most amount
    >>> approximate(3599,
    ...     {1: 's', 60: 'm', 3600: 'h', 1800: 'nap', 900: '?'})
    (1, 'nap')
    >>> approximate(20, {1: 's', 60: 'm', 3600: 'h'})
    (20, 's')
    >>> approximate(22, {1: 'd', 2: 'bi', 30: 'm', 7: 'w'})
    (3, 'w')
    """
    if amount < 0:
        raise ValueError('negative values are not supported')
    if 1 not in units:
        raise ValueError('the multiple 1 is missing')
    if any(n <= 0 for n in units):
        raise ValueError('multiple ≤ 0')

    multiple = max(m for m in units if m == 1 or m <= amount)
    return amount // multiple, units[multiple]


def approx_file_size(n_bytes):
    """
    approximate() for file size multiples.

    >>> approx_file_size(0)
    (0, 'B')
    >>> approx_file_size(1023)
    (1023, 'B')
    >>> approx_file_size(1024)
    (1, 'KiB')
    >>> approx_file_size(1025)
    (1, 'KiB')
    >>> approx_file_size(1024*1024 - 1)
    (1023, 'KiB')
    >>> approx_file_size(1024*1024 * 3)
    (3, 'MiB')
    >>> approx_file_size(1024*1024 * 3 + 1)
    (3, 'MiB')
    >>> approx_file_size(1024*1024 * 4 - 1)
    (3, 'MiB')
    """
    multiple = 1
    units = {multiple: 'B'}
    for prefix in ('K', 'M', 'G', 'T'):
        multiple *= 1024
        units[multiple] = prefix + 'iB'

    return approximate(n_bytes, units)
