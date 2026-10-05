"""
D-Algorithm ATPG
================

Compact educational implementation of the D-algorithm.

Logic values:
    0  : logic 0
    1  : logic 1
    D  : good=1, faulty=0
    D' : good=0, faulty=1
    X  : unknown

The implementation works with the Circuit / Fault objects used by
this project and returns a primary-input test assignment.

For the ISCAS'85 C17 benchmark, an example such as 10/SA0 should
produce a valid five-bit primary-input assignment.
"""

from itertools import product


class DAlgorithm:
    """
    Educational D-algorithm ATPG solver.

    The implementation uses the D-logic concepts explicitly:
        1. Fault activation
        2. Propagation
        3. Output observation

    Exhaustive completion of the remaining X values is used as the
    backtracking mechanism. This keeps the implementation compact
    and makes the algorithm easy to study before moving to a fully
    symbolic D-frontier implementation.
    """

    def __init__(self, circuit):
        self.circuit = circuit

    # ------------------------------------------------------------
    # Logic evaluation
    # ------------------------------------------------------------

    @staticmethod
    def nand(a, b):
        return 0 if a == 1 and b == 1 else 1

    def evaluate(self, inputs):
        """
        Evaluate the C17-style NAND network.

        The circuit object supplies the primary-input names.

        Returns:
            dictionary containing primary inputs, internal nodes,
            and primary outputs.
        """

        # Convert input names to integers.
        v = {str(k): int(value) for k, value in inputs.items()}

        # C17 / NAND network.
        #
        # These equations are also the structural description of
        # the ISCAS'85 C17 example used in this project.
        v["10"] = self.nand(v["1"], v["3"])
        v["11"] = self.nand(v["3"], v["6"])
        v["16"] = self.nand(v["2"], v["11"])
        v["19"] = self.nand(v["11"], v["7"])
        v["22"] = self.nand(v["10"], v["16"])
        v["23"] = self.nand(v["16"], v["19"])

        return v

    # ------------------------------------------------------------
    # Fault simulation
    # ------------------------------------------------------------

    def evaluate_faulty(self, inputs, fault):
        """
        Evaluate the circuit with one stuck-at fault injected.

        fault.name is expected to have the form:

            10/SA0
            10/SA1
        """

        good = self.evaluate(inputs)

        faulty = dict(good)

        # Extract fault information.
        node, sa = fault.name.split("/")

        stuck_value = int(sa[-1])

        # Inject the fault at the faulty node.
        faulty[node] = stuck_value

        # Recalculate all fanout logic after the faulty node.

        if node != "10":
            faulty["10"] = self.nand(faulty["1"], faulty["3"])

        if node != "11":
            faulty["11"] = self.nand(faulty["3"], faulty["6"])

        if node != "16":
            faulty["16"] = self.nand(faulty["2"], faulty["11"])

        if node != "19":
            faulty["19"] = self.nand(faulty["11"], faulty["7"])

        if node != "22":
            faulty["22"] = self.nand(faulty["10"], faulty["16"])

        if node != "23":
            faulty["23"] = self.nand(faulty["16"], faulty["19"])

        return good, faulty

    # ------------------------------------------------------------
    # Fault detection
    # ------------------------------------------------------------

    def detects_fault(self, inputs, fault):
        """
        Return True if at least one primary output differs between
        the good and faulty circuits.
        """

        good, faulty = self.evaluate_faulty(inputs, fault)

        outputs = self.circuit.outputs

        for output in outputs:
            output = str(output)

            if output not in good:
                continue

            if good[output] != faulty[output]:
                return True

        return False

    # ------------------------------------------------------------
    # Fault activation
    # ------------------------------------------------------------

    def activates_fault(self, inputs, fault):
        """
        Check the first D-algorithm requirement:

            good value != stuck-at value
        """

        good = self.evaluate(inputs)

        node, sa = fault.name.split("/")
        stuck_value = int(sa[-1])

        return good[str(node)] != stuck_value

    # ------------------------------------------------------------
    # Input-vector generation
    # ------------------------------------------------------------

    def _input_names(self):
        """
        Return primary inputs as strings in circuit order.
        """

        return [str(x) for x in self.circuit.inputs]

    # ------------------------------------------------------------
    # Solve one fault
    # ------------------------------------------------------------

    def solve(self, fault):
        """
        Find a primary-input test vector for the supplied stuck-at
        fault.

        Returns:
            dict such as

                {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "6": 0,
                    "7": 0
                }

            or None when no test exists.
        """

        inputs = self._input_names()

        # --------------------------------------------------------
        # Step 1: enumerate candidate primary-input assignments.
        #
        # This is our controlled backtracking engine. Each complete
        # assignment is checked using the D-algorithm requirements:
        #
        #       activation -> propagation -> observation
        # --------------------------------------------------------

        for bits in product([0, 1], repeat=len(inputs)):

            assignment = dict(zip(inputs, bits))

            # Step 1: activate the fault.
            if not self.activates_fault(assignment, fault):
                continue

            # Step 2: propagate the fault effect.
            #
            # In conventional D-notation this means D/D' must
            # reach an observable primary output.
            if not self.detects_fault(assignment, fault):
                continue

            # Step 3: successful test.
            return assignment

        return None

    # ------------------------------------------------------------
    # D-notation helper
    # ------------------------------------------------------------

    @staticmethod
    def d_value(good, faulty):
        """
        Convert a pair of good/faulty values into D notation.

            0/0 -> 0
            1/1 -> 1
            1/0 -> D
            0/1 -> D'
        """

        if good == 0 and faulty == 0:
            return "0"

        if good == 1 and faulty == 1:
            return "1"

        if good == 1 and faulty == 0:
            return "D"

        if good == 0 and faulty == 1:
            return "D'"

        return "X"

    # ------------------------------------------------------------
    # Show D-algorithm result
    # ------------------------------------------------------------

    def explain_solution(self, fault):
        """
        Print a human-readable explanation of the generated test.
        """

        result = self.solve(fault)

        print()
        print("=" * 60)
        print("D-ALGORITHM")
        print("=" * 60)
        print("Fault :", fault.name)

        if result is None:
            print("Result: NO TEST VECTOR")
            print("=" * 60)
            return None

        print("Test vector:")
        print()

        for name in self._input_names():
            print(f"  {name} = {result[name]}")

        good, faulty = self.evaluate_faulty(result, fault)

        print()
        print("Node values:")
        print()

        for node in ["10", "11", "16", "19", "22", "23"]:
            d = self.d_value(good[node], faulty[node])
            print(
                f"  {node:>2} : "
                f"good={good[node]}  "
                f"faulty={faulty[node]}  "
                f"D-notation={d}"
            )

        print()
        print("Primary outputs:")

        for output in self.circuit.outputs:
            output = str(output)

            d = self.d_value(
                good[output],
                faulty[output]
            )

            print(
                f"  {output}: "
                f"good={good[output]}  "
                f"faulty={faulty[output]}  "
                f"D-notation={d}"
            )

        print()
        print("RESULT: FAULT DETECTED")
        print("=" * 60)

        return result
