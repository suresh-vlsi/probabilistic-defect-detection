def nand_gate(values):
    return int(not all(values))


def and_gate(values):
    return int(all(values))


def or_gate(values):
    return int(any(values))


def nor_gate(values):
    return int(not any(values))


def not_gate(values):
    if len(values) != 1:
        raise ValueError("NOT gate requires exactly one input.")

    return int(not values[0])


def xor_gate(values):
    result = 0

    for value in values:
        result ^= value

    return result


def xnor_gate(values):
    return int(not xor_gate(values))


def buf_gate(values):
    if len(values) != 1:
        raise ValueError("BUF gate requires exactly one input.")

    return values[0]


def evaluate_gate(gate_type, values):

    gate_type = gate_type.upper()

    if gate_type == "NAND":
        return nand_gate(values)

    if gate_type == "AND":
        return and_gate(values)

    if gate_type == "OR":
        return or_gate(values)

    if gate_type == "NOR":
        return nor_gate(values)

    if gate_type == "NOT":
        return not_gate(values)

    if gate_type == "XOR":
        return xor_gate(values)

    if gate_type == "XNOR":
        return xnor_gate(values)

    if gate_type == "BUF":
        return buf_gate(values)

    raise ValueError(
        f"Unsupported gate type: {gate_type}"
    )


def simulate(circuit, input_values):
    """
    Simulate a combinational circuit.

    input_values:
        Dictionary mapping input node -> 0/1

    Returns:
        Dictionary containing all node values.
    """

    values = {}

    # -----------------------------------------
    # 1. Assign primary inputs
    # -----------------------------------------

    for node in circuit.inputs:

        if node not in input_values:
            raise ValueError(
                f"Missing value for input {node}"
            )

        bit = int(input_values[node])

        if bit not in (0, 1):
            raise ValueError(
                f"Input {node} must be 0 or 1."
            )

        values[node] = bit

    # -----------------------------------------
    # 2. Evaluate gates
    # -----------------------------------------

    for gate in circuit.gates:

        gate_inputs = []

        for node in gate.inputs:

            if node not in values:
                raise ValueError(
                    f"Node {node} has not been evaluated "
                    f"before gate {gate.output}."
                )

            gate_inputs.append(values[node])

        values[gate.output] = evaluate_gate(
            gate.gate_type,
            gate_inputs
        )

    return values


def simulate_outputs(circuit, input_values):
    """
    Return only the primary outputs.
    """

    values = simulate(circuit, input_values)

    return {
        output: values[output]
        for output in circuit.outputs
    }