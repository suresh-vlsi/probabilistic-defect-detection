"""
Five-valued D-algorithm logic.

Values:

    0  -> good=0, faulty=0
    1  -> good=1, faulty=1
    X  -> unknown
    D  -> good=1, faulty=0
    D' -> good=0, faulty=1
"""


def decode(value):
    """
    Convert a D-algorithm value into
    (good, faulty).
    """

    if value == "0":
        return 0, 0

    if value == "1":
        return 1, 1

    if value == "X":
        return None, None

    if value == "D":
        return 1, 0

    if value == "D'":
        return 0, 1

    raise ValueError(
        f"Invalid D value: {value}"
    )


def encode(good, faulty):
    """
    Convert (good, faulty) into
    five-valued D notation.
    """

    if good is None or faulty is None:
        return "X"

    if good == 0 and faulty == 0:
        return "0"

    if good == 1 and faulty == 1:
        return "1"

    if good == 1 and faulty == 0:
        return "D"

    if good == 0 and faulty == 1:
        return "D'"

    raise ValueError(
        f"Invalid pair: {(good, faulty)}"
    )


def nand(values):
    """
    NAND using five-valued logic.
    """

    decoded = [
        decode(value)
        for value in values
    ]

    good_values = [
        x[0] for x in decoded
    ]

    faulty_values = [
        x[1] for x in decoded
    ]

    # GOOD circuit
    if 0 in good_values:
        good = 1
    elif all(x == 1 for x in good_values):
        good = 0
    else:
        good = None

    # FAULTY circuit
    if 0 in faulty_values:
        faulty = 1
    elif all(x == 1 for x in faulty_values):
        faulty = 0
    else:
        faulty = None

    return encode(good, faulty)


def and_gate(values):
    """
    AND using five-valued logic.
    """

    decoded = [
        decode(value)
        for value in values
    ]

    good_values = [x[0] for x in decoded]
    faulty_values = [x[1] for x in decoded]

    if 0 in good_values:
        good = 0
    elif all(x == 1 for x in good_values):
        good = 1
    else:
        good = None

    if 0 in faulty_values:
        faulty = 0
    elif all(x == 1 for x in faulty_values):
        faulty = 1
    else:
        faulty = None

    return encode(good, faulty)


def or_gate(values):
    """
    OR using five-valued logic.
    """

    decoded = [
        decode(value)
        for value in values
    ]

    good_values = [x[0] for x in decoded]
    faulty_values = [x[1] for x in decoded]

    if 1 in good_values:
        good = 1
    elif all(x == 0 for x in good_values):
        good = 0
    else:
        good = None

    if 1 in faulty_values:
        faulty = 1
    elif all(x == 0 for x in faulty_values):
        faulty = 0
    else:
        faulty = None

    return encode(good, faulty)