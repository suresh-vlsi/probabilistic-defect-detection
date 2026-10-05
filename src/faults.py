class StuckAtFault:
    """
    Represents a single stuck-at fault.

    Example:

        node = "10"
        value = 0

    means:

        10 / SA0
    """

    def __init__(self, node, value):
        if value not in (0, 1):
            raise ValueError(
                "Stuck-at value must be 0 or 1."
            )

        self.node = str(node)
        self.value = value

    @property
    def name(self):
        return f"{self.node}/SA{self.value}"

    def __repr__(self):
        return self.name


def generate_stuck_at_faults(circuit):
    """
    Generate SA0 and SA1 faults for every circuit node.
    """

    faults = []

    for node in sorted(
        circuit.nodes,
        key=lambda x: int(x) if x.isdigit() else x
    ):

        faults.append(
            StuckAtFault(node, 0)
        )

        faults.append(
            StuckAtFault(node, 1)
        )

    return faults