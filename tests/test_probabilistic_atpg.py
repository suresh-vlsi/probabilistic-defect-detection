from src.probabilistic_atpg import (
    build_test_fault_map,
    rank_tests,
    compact_test_set,
    calculate_fault_coverage,
    calculate_test_reduction,
)


def test_build_test_fault_map():

    fault_dictionary = {
        "1/SA0": ["00000", "00001"],
        "1/SA1": ["00000", "00010"],
        "2/SA0": ["00000", "00011"],
        "3/SA0": ["00001", "00010"],
    }

    test_map = build_test_fault_map(
        fault_dictionary
    )

    assert "00000" in test_map

    assert "1/SA0" in test_map["00000"]

    assert "1/SA1" in test_map["00000"]


def test_probabilistic_ranking():

    test_vectors = [
        "00000",
        "00001",
        "00010",
        "00011",
    ]

    fault_dictionary = {

        "1/SA0": [
            "00000",
            "00001",
        ],

        "1/SA1": [
            "00000",
            "00010",
        ],

        "2/SA0": [
            "00000",
            "00011",
        ],

        "3/SA0": [
            "00001",
            "00010",
        ],
    }

    ranked = rank_tests(
        test_vectors,
        fault_dictionary
    )

    assert len(ranked) > 0

    compacted = compact_test_set(
        ranked
    )

    assert len(compacted) > 0

    coverage = calculate_fault_coverage(
        ranked,
        len(fault_dictionary)
    )

    assert coverage["coverage"] == 100.0


def test_test_reduction():

    reduction = calculate_test_reduction(
        32,
        8
    )

    assert reduction == 75.0
