from src.diversity import (
    hamming_distance,
    average_hamming_distance,
)


def test_hamming_distance():

    assert hamming_distance(
        "00000",
        "11111"
    ) == 5

    assert hamming_distance(
        "10101",
        "10101"
    ) == 0


def test_average_hamming_distance():

    vectors = [
        "000",
        "001",
        "111",
    ]

    result = average_hamming_distance(
        vectors
    )

    assert result == 2.0