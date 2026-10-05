import re

from .circuit import Circuit


def parse_bench(filename):
    """
    Parse an ISCAS-style .bench file.

    Supported statements:

        INPUT(...)
        OUTPUT(...)
        node = GATE(input1, input2, ...)
    """

    circuit = Circuit()

    with open(filename, "r") as file:
        for line_number, raw_line in enumerate(file, start=1):

            line = raw_line.strip()

            # Ignore blank lines
            if not line:
                continue

            # Ignore comments
            if line.startswith("#"):
                continue

            # -----------------------------
            # INPUT(...)
            # -----------------------------
            match = re.match(
                r"INPUT\s*\(\s*([^)]+)\s*\)",
                line,
                re.IGNORECASE
            )

            if match:
                node = match.group(1).strip()
                circuit.add_input(node)
                continue

            # -----------------------------
            # OUTPUT(...)
            # -----------------------------
            match = re.match(
                r"OUTPUT\s*\(\s*([^)]+)\s*\)",
                line,
                re.IGNORECASE
            )

            if match:
                node = match.group(1).strip()
                circuit.add_output(node)
                continue

            # -----------------------------
            # GATE assignment
            #
            # Example:
            #
            # 10 = NAND(1, 3)
            # -----------------------------
            match = re.match(
                r"(\S+)\s*=\s*([A-Za-z0-9_]+)"
                r"\s*\(\s*([^)]*)\s*\)",
                line
            )

            if match:
                output = match.group(1).strip()
                gate_type = match.group(2).strip()

                input_string = match.group(3).strip()

                if input_string:
                    inputs = [
                        x.strip()
                        for x in input_string.split(",")
                    ]
                else:
                    inputs = []

                circuit.add_gate(
                    output,
                    gate_type,
                    inputs
                )

                continue

            raise ValueError(
                f"Cannot parse line {line_number}: {line}"
            )

    return circuit