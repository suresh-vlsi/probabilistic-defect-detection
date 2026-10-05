from pathlib import Path

from src.parser import parse_bench
from src.atpg import (
    generate_all_input_vectors,
    generate_test_for_fault,
)
from src.faults import generate_stuck_at_faults
from src.fault_sim import detect_fault


BENCHMARK = (
    Path(__file__).parent.parent
    / "benchmarks"
    / "iscas85"
    / "c17.bench"
)


def test_atpg_finds_test_for_every_fault():

    circuit = parse_bench(BENCHMARK)

    test_vectors = generate_all_input_vectors(
        circuit
    )

    faults = generate_stuck_at_faults(
        circuit
    )

    for fault in faults:

        vector, input_values = (
            generate_test_for_fault(
                circuit,
                fault,
                test_vectors
            )
        )

        assert vector is not None

        assert input_values is not None

        assert detect_fault(
            circuit,
            input_values,
            fault
        )