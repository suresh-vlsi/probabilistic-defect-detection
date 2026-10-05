from itertools import product

from .fault_sim import detect_fault


def generate_all_input_vectors(circuit):
    """
    Generate every possible binary input vector.

    For N primary inputs, this produces 2^N vectors.

    Returns:
        [
            ("00000", {"1": 0, "2": 0, ...}),
            ("00001", {"1": 0, "2": 0, ...}),
            ...
        ]
    """

    vectors = []

    for bits in product(
        [0, 1],
        repeat=len(circuit.inputs)
    ):

        vector = "".join(
            str(bit)
            for bit in bits
        )

        input_values = {
            node: bit
            for node, bit in zip(
                circuit.inputs,
                bits
            )
        }

        vectors.append(
            (vector, input_values)
        )

    return vectors


def generate_test_for_fault(
    circuit,
    fault,
    test_vectors=None
):
    """
    Exhaustive-search ATPG.

    Search through all possible input vectors and
    return the first vector that detects the target fault.

    Returns:
        (vector, input_values)

    or

        (None, None)

    if no test exists.
    """

    if test_vectors is None:
        test_vectors = generate_all_input_vectors(
            circuit
        )

    for vector, input_values in test_vectors:

        if detect_fault(
            circuit,
            input_values,
            fault
        ):
            return vector, input_values

    return None, None


def generate_tests_for_all_faults(
    circuit,
    faults,
    test_vectors=None
):
    """
    Generate one detecting test for every fault.

    Returns:
        Dictionary:

        {
            "1/SA0": "00001",
            "1/SA1": "00100",
            ...
        }
    """

    if test_vectors is None:
        test_vectors = generate_all_input_vectors(
            circuit
        )

    tests = {}

    for fault in faults:

        vector, _ = generate_test_for_fault(
            circuit,
            fault,
            test_vectors
        )

        tests[fault.name] = vector

    return tests