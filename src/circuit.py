class Gate:
    """Represents a single logic gate."""

    def __init__(self, output, gate_type, inputs):
        self.output = output
        self.gate_type = gate_type.upper()
        self.inputs = inputs

    def __repr__(self):
        return (
            f"Gate(output={self.output}, "
            f"type={self.gate_type}, "
            f"inputs={self.inputs})"
        )


class Circuit:
    """Represents a combinational digital circuit."""

    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.gates = []

        # All named nodes in the circuit
        self.nodes = set()

    def add_input(self, node):
        node = str(node)
        self.inputs.append(node)
        self.nodes.add(node)

    def add_output(self, node):
        node = str(node)
        self.outputs.append(node)
        self.nodes.add(node)

    def add_gate(self, output, gate_type, inputs):
        output = str(output)
        inputs = [str(x) for x in inputs]

        gate = Gate(output, gate_type, inputs)

        self.gates.append(gate)

        self.nodes.add(output)

        for node in inputs:
            self.nodes.add(node)

    def __repr__(self):
        return (
            f"Circuit("
            f"inputs={self.inputs}, "
            f"outputs={self.outputs}, "
            f"gates={len(self.gates)})"
        )

    def summary(self):
        print("\n========== CIRCUIT SUMMARY ==========")

        print(f"Primary inputs  : {self.inputs}")
        print(f"Primary outputs : {self.outputs}")
        print(f"Number of gates: {len(self.gates)}")
        print(f"Number of nodes: {len(self.nodes)}")

        print("\nGates:")

        for gate in self.gates:
            print(
                f"  {gate.output} = "
                f"{gate.gate_type}({', '.join(gate.inputs)})"
            )

        print("=====================================\n")