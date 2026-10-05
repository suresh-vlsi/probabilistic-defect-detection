from pathlib import Path

from src.parser import parse_bench
from src.faults import generate_stuck_at_faults
from src.d_algorithm import DAlgorithm
from src.fault_sim import detect_fault


BENCHMARK = (
    Path(__file__).parent.parent
    / "benchmarks"
    / "iscas85"
    / "c17.bench"
)


def test_d_algorithm_can_create_assignment():

    circuit = parse_bench(BENCHMARK)

    faults = generate_stuck_at_faults(
        circuit
    )

    solver = DAlgorithm(circuit)

    fault = next(
        f for f in faults
        if f.name == "10/SA0"
    )

    result = solver.solve(fault)

    assert result is not None

    assert set(result.keys()) == set(
        circuit.inputs
    )