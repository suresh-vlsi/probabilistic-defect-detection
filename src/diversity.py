def hamming_distance(vector_a, vector_b):
    """
    Calculate Hamming distance between two
    binary test vectors.
    """

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same length."
        )

    return sum(
        bit_a != bit_b
        for bit_a, bit_b in zip(
            vector_a,
            vector_b
        )
    )


def average_hamming_distance(vectors):
    """
    Calculate the average pairwise Hamming distance
    among a collection of test vectors.
    """

    if len(vectors) < 2:
        return 0.0

    distances = []

    for i in range(len(vectors)):

        for j in range(i + 1, len(vectors)):

            distances.append(
                hamming_distance(
                    vectors[i],
                    vectors[j]
                )
            )

    return sum(distances) / len(distances)