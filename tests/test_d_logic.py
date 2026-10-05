from src.d_logic import (
    decode,
    encode,
    nand,
    and_gate,
    or_gate,
)


def test_encoding():

    assert decode("0") == (0, 0)
    assert decode("1") == (1, 1)
    assert decode("D") == (1, 0)
    assert decode("D'") == (0, 1)


def test_nand_activation():

    assert nand(["0", "X"]) == "1"
    assert nand(["1", "1"]) == "0"


def test_d_propagation_through_nand():

    # NAND(D, 1) = D'
    assert nand(["D", "1"]) == "D'"

    # NAND(D', 1) = D
    assert nand(["D'", "1"]) == "D"


def test_and_gate():

    assert and_gate(["D", "1"]) == "D"
    assert and_gate(["D'", "1"]) == "D'"


def test_or_gate():

    assert or_gate(["D", "0"]) == "D"
    assert or_gate(["D'", "0"]) == "D'"