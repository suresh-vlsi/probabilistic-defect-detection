from pathlib import Path

from src.parser import parse_bench
from src.simulator import simulate


BENCHMARK = (
    Path(__file__).parent.parent
    / "benchmarks"
    / "iscas85"
    / "c17.bench"
)


def vector_to_inputs(circuit, vector):

    return {
        node: int(bit)
        for node, bit in zip(
            circuit.inputs,
            vector
        )
    }


def test_c17_loads():

    circuit = parse_bench(BENCHMARK)

    assert len(circuit.inputs) == 5
    assert len(circuit.outputs) == 2
    assert len(circuit.gates) == 6


def test_c17_all_zero():

    circuit = parse_bench(BENCHMARK)

    inputs = vector_to_inputs(
        circuit,
        "00000"
    )

    outputs = simulate(
        circuit,
        inputs
    )

    assert outputs["22"] == 0
    assert outputs["23"] == 0


def test_c17_all_one():

    circuit = parse_bench(BENCHMARK)

    inputs = vector_to_inputs(
        circuit,
        "11111"
    )

    outputs = simulate(
        circuit,
        inputs
    )

    assert outputs["22"] == 1
    assert outputs["23"] == 0