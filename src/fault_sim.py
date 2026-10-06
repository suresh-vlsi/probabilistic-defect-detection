from .simulator import evaluate_gate
from .faults import StuckAtFault


def simulate_with_fault(circuit, input_values, fault):
    """
    Simulate a combinational circuit with one
    stuck-at fault injected at a specified node.

    fault:
        StuckAtFault(node, value)

    Returns:
        Dictionary containing all node values.
    """

    if not isinstance(fault, StuckAtFault):
        raise TypeError(
            "fault must be a StuckAtFault object"
        )

    values = {}

    # ---------------------------------------------------------
    # 1. Assign primary inputs
    # ---------------------------------------------------------

    for node in circuit.inputs:

        if node not in input_values:
            raise ValueError(
                f"Missing value for input {node}"
            )

        bit = int(input_values[node])

        if bit not in (0, 1):
            raise ValueError(
                f"Input {node} must be 0 or 1"
            )

        # Inject fault if the primary input itself is faulty
        if node == fault.node:
            values[node] = fault.value
        else:
            values[node] = bit

    # ---------------------------------------------------------
    # 2. Evaluate gates
    # ---------------------------------------------------------

    for gate in circuit.gates:

        gate_inputs = []

        for node in gate.inputs:

            if node not in values:
                raise ValueError(
                    f"Node {node} has not been evaluated "
                    f"before gate {gate.output}"
                )

            gate_inputs.append(values[node])

        output_value = evaluate_gate(
            gate.gate_type,
            gate_inputs
        )

        # Inject stuck-at fault at this gate's output
        if gate.output == fault.node:
            output_value = fault.value

        values[gate.output] = output_value

    return values


def fault_detected(circuit, good_values, faulty_values):
    """
    Determine whether a fault is detected.

    A fault is detected when at least one primary output
    differs between the good and faulty circuits.
    """

    for output in circuit.outputs:

        if good_values[output] != faulty_values[output]:
            return True

    return False


def detect_fault(circuit, input_values, fault):
    """
    Simulate both the good and faulty circuit and determine
    whether the fault is detected.

    Returns:
        True  -> fault detected
        False -> fault not detected
    """

    from .simulator import simulate

    good_values = simulate(
        circuit,
        input_values
    )

    faulty_values = simulate_with_fault(
        circuit,
        input_values,
        fault
    )

    return fault_detected(
        circuit,
        good_values,
        faulty_values
    )


def find_detecting_tests(circuit, test_vectors, fault):
    """
    Find all test vectors that detect a particular fault.

    Returns:
        List of binary-string test vectors.
    """

    detecting_tests = []

    from .simulator import simulate

    for vector, input_values in test_vectors:

        good_values = simulate(
            circuit,
            input_values
        )

        faulty_values = simulate_with_fault(
            circuit,
            input_values,
            fault
        )

        if fault_detected(
            circuit,
            good_values,
            faulty_values
        ):
            detecting_tests.append(vector)

    return detecting_tests

def build_fault_dictionary(circuit, test_vectors, faults):
    """
    Build the fault dictionary.

    Maps:

        fault -> list of detecting test vectors

    Progress is printed periodically because this operation
    can be expensive for large ISCAS benchmarks.
    """

    from .simulator import simulate
    import time

    fault_dictionary = {}

    # --------------------------------------------------------
    # Initialize dictionary
    # --------------------------------------------------------

    for fault in faults:

        fault_name = (
            str(fault.name)
            if hasattr(fault, "name")
            else str(fault)
        )

        fault_dictionary[fault_name] = []

    total_vectors = len(test_vectors)
    total_faults = len(faults)

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # Process test vectors
    # --------------------------------------------------------

    for vector_index, (vector, input_values) in enumerate(
        test_vectors,
        start=1
    ):

        # Good circuit is simulated only once per vector.
        good_values = simulate(
            circuit,
            input_values
        )

        # ----------------------------------------------------
        # Check every fault
        # ----------------------------------------------------

        for fault in faults:

            faulty_values = simulate_with_fault(
                circuit,
                input_values,
                fault
            )

            detected = any(
                good_values[output] != faulty_values[output]
                for output in circuit.outputs
            )

            if detected:

                fault_name = (
                    str(fault.name)
                    if hasattr(fault, "name")
                    else str(fault)
                )

                fault_dictionary[fault_name].append(
                    str(vector)
                )

        # ----------------------------------------------------
        # Progress reporting
        # ----------------------------------------------------

        if (
            vector_index == 1
            or vector_index % 25 == 0
            or vector_index == total_vectors
        ):

            elapsed = time.perf_counter() - start_time

            percent = (
                100.0 * vector_index / total_vectors
                if total_vectors
                else 100.0
            )

            print(
                f"\r    Progress: "
                f"{vector_index}/{total_vectors} "
                f"({percent:6.2f}%) "
                f"| elapsed: {elapsed:8.2f}s",
                end="",
                flush=True
            )

    print()

    return fault_dictionary