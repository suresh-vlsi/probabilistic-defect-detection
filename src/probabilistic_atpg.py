"""
probabilistic_atpg.py

Probabilistic ATPG utilities.

This module provides:

1. Fault -> test-vector representation
2. Test-vector -> fault mapping
3. Probabilistic test ranking
4. Greedy test-set compaction
5. Fault coverage calculation
6. Test-count reduction calculation

The implementation is intentionally independent of the simulator and
D-algorithm modules so that it can be tested independently.
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Sequence,
    Tuple,
)


# ============================================================
# TYPE DEFINITIONS
# ============================================================

TestVector = str
FaultName = str

FaultDictionary = Dict[FaultName, List[TestVector]]


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _is_test_vector(value: Any) -> bool:
    """
    Return True if value looks like a binary test vector.

    Examples
    --------
    "00000" -> True
    "10101" -> True
    10101   -> False
    """
    return isinstance(value, str) and all(
        bit in {"0", "1"} for bit in value
    )


def _normalize_tests(value: Any) -> List[TestVector]:
    """
    Convert a fault's test-vector representation into a list.

    Accepted forms:

        ["00000", "00001"]
        ("00000", "00001")
        {"00000", "00001"}
        "00000"

    Returns
    -------
    list[str]
    """
    if value is None:
        return []

    if _is_test_vector(value):
        return [value]

    if isinstance(value, (list, tuple, set, frozenset)):
        result = []

        for item in value:
            if isinstance(item, str):
                result.append(item)
            else:
                result.append(str(item))

        return result

    return [str(value)]


def _canonicalize_fault_tests(
    fault_tests: Mapping[Any, Any],
) -> FaultDictionary:
    """
    Convert a fault -> tests mapping into a canonical form.

    Canonical form:

        {
            "1/SA0": ["00000", "00001"],
            "1/SA1": ["00000", "00010"],
        }

    Test vectors are deduplicated and sorted.
    """

    if not isinstance(fault_tests, Mapping):
        raise TypeError(
            "fault_tests must be a mapping of fault -> test vectors"
        )

    normalized: FaultDictionary = {}

    for fault, tests in fault_tests.items():

        fault_name = str(fault)

        vector_list = _normalize_tests(tests)

        # Remove duplicates while preserving deterministic ordering.
        vector_list = sorted(set(vector_list))

        normalized[fault_name] = vector_list

    return normalized


def _entry_test(entry: Any) -> TestVector:
    """
    Extract a test vector from a ranked entry.

    Supported ranked-entry forms:

        "00001"

        ("00001", score)

        ("00001", score, faults)

        {
            "test": "00001",
            ...
        }

    """

    if isinstance(entry, str):
        return entry

    if isinstance(entry, Mapping):

        for key in ("test", "test_vector", "vector"):
            if key in entry:
                return str(entry[key])

    if isinstance(entry, (tuple, list)):

        if len(entry) >= 1:
            return str(entry[0])

    raise TypeError(
        f"Cannot extract test vector from ranked entry: {entry!r}"
    )


def _entry_faults(
    entry: Any,
    test_fault_map: Mapping[TestVector, Iterable[FaultName]],
) -> set[FaultName]:
    """
    Extract faults represented by a ranked entry.

    If the ranked entry does not explicitly contain fault information,
    use the test -> fault map.
    """

    test = _entry_test(entry)

    if isinstance(entry, Mapping):

        for key in ("faults", "detected_faults"):
            if key in entry:
                return set(str(x) for x in entry[key])

    if isinstance(entry, (tuple, list)) and len(entry) >= 3:

        possible_faults = entry[2]

        if isinstance(possible_faults, (list, tuple, set, frozenset)):
            return set(str(x) for x in possible_faults)

    return set(test_fault_map.get(test, []))


# ============================================================
# BUILD TEST -> FAULT MAP
# ============================================================

def build_test_fault_map(
    fault_dictionary: Mapping[Any, Any],
    *args: Any,
) -> Dict[TestVector, List[FaultName]]:
    """
    Build the reverse mapping:

        fault -> tests

    into:

        test -> faults

    Example
    -------

    Input:

        {
            "1/SA0": ["00000", "00001"],
            "1/SA1": ["00000", "00010"],
            "2/SA0": ["00000", "00011"],
        }

    Output:

        {
            "00000": ["1/SA0", "1/SA1", "2/SA0"],
            "00001": ["1/SA0"],
            "00010": ["1/SA1"],
            "00011": ["2/SA0"],
        }

    The optional *args parameter is retained for backward compatibility
    with older versions of this project.
    """

    canonical = _canonicalize_fault_tests(fault_dictionary)

    test_fault_map: Dict[TestVector, List[FaultName]] = {}

    for fault, tests in canonical.items():

        for test in tests:

            if test not in test_fault_map:
                test_fault_map[test] = []

            if fault not in test_fault_map[test]:
                test_fault_map[test].append(fault)

    # Make ordering deterministic.
    for test in test_fault_map:
        test_fault_map[test] = sorted(test_fault_map[test])

    return dict(sorted(test_fault_map.items()))


# ============================================================
# PROBABILISTIC TEST RANKING
# ============================================================

def rank_tests(
    test_vectors: Sequence[TestVector],
    fault_dictionary: Mapping[Any, Any],
) -> List[Dict[str, Any]]:
    """
    Rank candidate test vectors according to probabilistic fault
    detection importance.

    For each fault:

        contribution = 1 / number_of_tests_that_detect_the_fault

    A test receives the sum of the contributions of all faults it
    detects.

    Therefore a test that detects a rare/hard-to-detect fault receives
    a higher score.

    Returned entries have the form:

        {
            "test": "00000",
            "score": 2.5,
            "faults": ["1/SA0", "1/SA1"]
        }

    The list is sorted by:

        1. descending score
        2. descending number of detected faults
        3. ascending test-vector value
    """

    canonical = _canonicalize_fault_tests(fault_dictionary)

    test_fault_map = build_test_fault_map(canonical)

    # --------------------------------------------------------
    # Calculate probability weight for each fault.
    # --------------------------------------------------------

    fault_weight: Dict[FaultName, float] = {}

    for fault, tests in canonical.items():

        if len(tests) == 0:
            fault_weight[fault] = 0.0
        else:
            fault_weight[fault] = 1.0 / float(len(tests))

    # --------------------------------------------------------
    # Ensure every requested test vector is considered.
    # --------------------------------------------------------

    candidates = []

    seen = set()

    for vector in test_vectors:

        test = str(vector)

        if test in seen:
            continue

        seen.add(test)

        faults = set(test_fault_map.get(test, []))

        score = sum(
            fault_weight.get(fault, 0.0)
            for fault in faults
        )

        candidates.append(
            {
                "test": test,
                "score": score,
                "faults": sorted(faults),
            }
        )

    # --------------------------------------------------------
    # Deterministic ranking.
    # --------------------------------------------------------

    candidates.sort(
        key=lambda entry: (
            -float(entry["score"]),
            -len(entry["faults"]),
            entry["test"],
        )
    )

    # Add explicit rank.
    for index, entry in enumerate(candidates, start=1):
        entry["rank"] = index

    return candidates


# ============================================================
# GREEDY TEST-SET COMPACTION
# ============================================================

def compact_test_set(
    ranked_tests: Sequence[Any],
) -> List[Any]:
    """
    Compact a ranked test list using greedy set-cover selection.

    The highest-ranked test is selected first.

    Each subsequent test is selected only when it contributes at least
    one previously uncovered fault.

    The original ranked-entry format is preserved.

    Example
    -------

    ranked_tests = [
        {
            "test": "00000",
            "score": 2.0,
            "faults": ["1/SA0", "1/SA1"]
        },
        ...
    ]

    Returns
    -------

    A reduced list containing only the tests necessary to cover all
    faults represented in the ranked list.
    """

    if not ranked_tests:
        return []

    # --------------------------------------------------------
    # Build test -> faults from ranked entries.
    # --------------------------------------------------------

    test_fault_map: Dict[TestVector, set[FaultName]] = {}

    for entry in ranked_tests:

        test = _entry_test(entry)

        faults = set()

        if isinstance(entry, Mapping):

            if "faults" in entry:
                faults = set(str(x) for x in entry["faults"])

            elif "detected_faults" in entry:
                faults = set(
                    str(x)
                    for x in entry["detected_faults"]
                )

        elif isinstance(entry, (tuple, list)) and len(entry) >= 3:

            if isinstance(
                entry[2],
                (list, tuple, set, frozenset),
            ):
                faults = set(str(x) for x in entry[2])

        test_fault_map[test] = faults

    # --------------------------------------------------------
    # Collect all faults.
    # --------------------------------------------------------

    all_faults = set()

    for faults in test_fault_map.values():
        all_faults.update(faults)

    # --------------------------------------------------------
    # If ranked entries do not contain fault information,
    # preserve the ranked list instead of accidentally deleting
    # everything.
    # --------------------------------------------------------

    if not all_faults:
        return list(ranked_tests)

    # --------------------------------------------------------
    # Greedy set cover.
    # --------------------------------------------------------

    uncovered = set(all_faults)

    selected: List[Any] = []

    # The ranked list is already ordered by importance.
    remaining = list(ranked_tests)

    while uncovered and remaining:

        best_entry = None
        best_new_faults: set[FaultName] = set()

        best_index = -1

        for index, entry in enumerate(remaining):

            test = _entry_test(entry)

            faults = test_fault_map.get(test, set())

            new_faults = faults & uncovered

            if len(new_faults) > len(best_new_faults):

                best_entry = entry
                best_new_faults = new_faults
                best_index = index

        # No remaining test contributes anything.
        if best_entry is None or not best_new_faults:
            break

        selected.append(best_entry)

        uncovered -= best_new_faults

        remaining.pop(best_index)

    return selected


# ============================================================
# FAULT COVERAGE
# ============================================================

def calculate_fault_coverage(
    ranked_tests: Sequence[Any],
    fault_source: Any,
) -> Dict[str, Any]:
    """
    Calculate fault coverage.

    Parameters
    ----------
    ranked_tests:
        Ranked or compacted test entries.

    fault_source:
        Either:

        1. A fault dictionary:

           {
               "1/SA0": ["00000"],
               ...
           }

        OR

        2. An integer containing the total number of faults.

    Returns
    -------
    dict

    Example:

        {
            "covered_faults": 4,
            "total_faults": 4,
            "coverage": 100.0
        }

    Coverage is expressed as a percentage.
    """

    # --------------------------------------------------------
    # Case 1: complete fault dictionary supplied.
    # --------------------------------------------------------

    if isinstance(fault_source, Mapping):

        fault_dictionary = _canonicalize_fault_tests(
            fault_source
        )

        total_faults = len(fault_dictionary)

        test_fault_map = build_test_fault_map(
            fault_dictionary
        )

        covered_faults = set()

        for entry in ranked_tests:

            test = _entry_test(entry)

            faults = _entry_faults(
                entry,
                test_fault_map,
            )

            covered_faults.update(faults)

        # Never report faults that are not in the dictionary.
        covered_faults &= set(fault_dictionary.keys())

    # --------------------------------------------------------
    # Case 2: integer total-fault count supplied.
    #
    # This form is used by the existing test:
    #
    #     calculate_fault_coverage(ranked, len(fault_dictionary))
    #
    # Since no fault names are available, count distinct faults
    # represented by the ranked entries.
    # --------------------------------------------------------

    elif isinstance(fault_source, int):

        total_faults = int(fault_source)

        covered_faults = set()

        for entry in ranked_tests:

            if isinstance(entry, Mapping):

                if "faults" in entry:
                    covered_faults.update(
                        str(x)
                        for x in entry["faults"]
                    )

                elif "detected_faults" in entry:
                    covered_faults.update(
                        str(x)
                        for x in entry["detected_faults"]
                    )

            elif isinstance(entry, (tuple, list)):

                if len(entry) >= 3 and isinstance(
                    entry[2],
                    (list, tuple, set, frozenset),
                ):
                    covered_faults.update(
                        str(x)
                        for x in entry[2]
                    )

        # If the entries explicitly identify faults, use them.
        # Otherwise the integer form cannot determine coverage.
        if total_faults > 0:
            covered_count = min(
                len(covered_faults),
                total_faults,
            )
        else:
            covered_count = 0

        return {
            "covered_faults": covered_count,
            "total_faults": total_faults,
            "coverage": (
                100.0 * covered_count / total_faults
                if total_faults > 0
                else 0.0
            ),
        }

    else:

        raise TypeError(
            "fault_source must be either a fault dictionary "
            "or an integer total-fault count"
        )

    # --------------------------------------------------------
    # Calculate percentage.
    # --------------------------------------------------------

    covered_count = len(covered_faults)

    if total_faults > 0:
        coverage = (
            100.0 * covered_count / total_faults
        )
    else:
        coverage = 0.0

    return {
        "covered_faults": covered_count,
        "total_faults": total_faults,
        "coverage": coverage,
    }


# ============================================================
# TEST REDUCTION
# ============================================================

def calculate_test_reduction(
    original_test_count: int,
    reduced_test_count: int,
) -> float:
    """
    Calculate percentage reduction in test count.

    Formula:

        reduction =
            ((original - reduced) / original) * 100

    Example
    -------

        calculate_test_reduction(32, 8)

    gives:

        75.0
    """

    original = int(original_test_count)
    reduced = int(reduced_test_count)

    if original < 0:
        raise ValueError(
            "original_test_count cannot be negative"
        )

    if reduced < 0:
        raise ValueError(
            "reduced_test_count cannot be negative"
        )

    if reduced > original:
        raise ValueError(
            "reduced_test_count cannot exceed "
            "original_test_count"
        )

    if original == 0:
        return 0.0

    reduction = (
        (original - reduced)
        / original
        * 100.0
    )

    return reduction


# ============================================================
# OPTIONAL HIGH-LEVEL PIPELINE
# ============================================================

def probabilistic_atpg(
    test_vectors: Sequence[TestVector],
    fault_dictionary: Mapping[Any, Any],
) -> Dict[str, Any]:
    """
    Complete probabilistic ATPG post-processing pipeline.

    Steps:

        1. Build test -> fault map
        2. Rank tests probabilistically
        3. Compact the ranked test set
        4. Calculate fault coverage
        5. Calculate test reduction
    """

    canonical_faults = _canonicalize_fault_tests(
        fault_dictionary
    )

    test_fault_map = build_test_fault_map(
        canonical_faults
    )

    ranked_tests = rank_tests(
        test_vectors,
        canonical_faults,
    )

    compacted_tests = compact_test_set(
        ranked_tests
    )

    coverage = calculate_fault_coverage(
        compacted_tests,
        canonical_faults,
    )

    reduction = calculate_test_reduction(
        len(test_vectors),
        len(compacted_tests),
    )

    return {
        "test_fault_map": test_fault_map,
        "ranked_tests": ranked_tests,
        "compacted_tests": compacted_tests,
        "coverage": coverage,
        "test_reduction": reduction,
    }


# ============================================================
# BACKWARD-COMPATIBILITY ALIASES
# ============================================================

def reduce_test_set(
    ranked_tests: Sequence[Any],
) -> List[Any]:
    """
    Backward-compatible alias for compact_test_set().
    """

    return compact_test_set(ranked_tests)


# ============================================================
# MODULE SELF TEST
# ============================================================

if __name__ == "__main__":

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

    print("=" * 60)
    print("PROBABILISTIC ATPG SELF TEST")
    print("=" * 60)

    print("\nFault dictionary:")
    for fault, tests in fault_dictionary.items():
        print(f"  {fault}: {tests}")

    print("\nTest -> Fault map:")

    test_fault_map = build_test_fault_map(
        fault_dictionary
    )

    for test, faults in test_fault_map.items():
        print(f"  {test}: {faults}")

    print("\nRanked tests:")

    ranked = rank_tests(
        test_vectors,
        fault_dictionary,
    )

    for entry in ranked:
        print(
            f"  rank={entry['rank']:2d} "
            f"test={entry['test']} "
            f"score={entry['score']:.6f} "
            f"faults={entry['faults']}"
        )

    print("\nCompacted tests:")

    compacted = compact_test_set(ranked)

    for entry in compacted:
        print(
            f"  {entry['test']} "
            f"faults={entry['faults']}"
        )

    print("\nCoverage:")

    coverage = calculate_fault_coverage(
        compacted,
        fault_dictionary,
    )

    print(
        f"  Covered faults : "
        f"{coverage['covered_faults']}"
    )

    print(
        f"  Total faults   : "
        f"{coverage['total_faults']}"
    )

    print(
        f"  Coverage       : "
        f"{coverage['coverage']:.2f}%"
    )

    print("\nTest reduction:")

    reduction = calculate_test_reduction(
        len(test_vectors),
        len(compacted),
    )

    print(
        f"  Original tests : {len(test_vectors)}"
    )

    print(
        f"  Reduced tests  : {len(compacted)}"
    )

    print(
        f"  Reduction      : {reduction:.2f}%"
    )

    print("\n" + "=" * 60)
