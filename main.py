from pathlib import Path

from src.parser import parse_bench
from src.simulator import simulate
from src.faults import generate_stuck_at_faults
from src.fault_sim import find_detecting_tests
from src.atpg import (
    generate_all_input_vectors,
    generate_tests_for_all_faults,
)
from src.d_algorithm import DAlgorithm

from src.probabilistic_atpg import (
    build_test_fault_map,
    rank_tests,
    compact_test_set,
    calculate_fault_coverage,
    calculate_test_reduction,
    print_ranking,
)

def main():

    # =========================================================
    # LOAD BENCHMARK
    # =========================================================

    benchmark = (
        Path(__file__).parent
        / "benchmarks"
        / "iscas85"
        / "c17.bench"
    )

    print("\n==============================================")
    print(" PROBABILISTIC DEFECT DETECTION")
    print(" STEP 2: EXHAUSTIVE SSA FAULT SIMULATION")
    print("==============================================\n")

    print(f"Benchmark: {benchmark}\n")

    circuit = parse_bench(benchmark)

    circuit.summary()

    # =========================================================
    # GENERATE ALL INPUT VECTORS
    # =========================================================

    test_vectors = generate_all_input_vectors(
        circuit
    )

    print(
        f"Number of primary inputs : "
        f"{len(circuit.inputs)}"
    )

    print(
        f"Number of possible tests : "
        f"{len(test_vectors)}"
    )

    print()

    # =========================================================
    # GENERATE SSA FAULTS
    # =========================================================

    faults = generate_stuck_at_faults(
        circuit
    )

    print(
        f"Number of circuit nodes : "
        f"{len(circuit.nodes)}"
    )

    print(
        f"Number of SSA faults : "
        f"{len(faults)}"
    )

    print()

    # =========================================================
    # FAULT DICTIONARY
    # =========================================================

    fault_dictionary = {}

    print("==============================================")
    print("FAULT DICTIONARY")
    print("==============================================")

    for fault in faults:

        detecting_tests = find_detecting_tests(
            circuit,
            test_vectors,
            fault
        )

        fault_dictionary[fault.name] = (
            detecting_tests
        )

        print(
            f"{fault.name:8s} : "
            f"{len(detecting_tests):2d} detecting tests"
        )

    # =========================================================
    # COVERAGE
    # =========================================================

    detected_faults = [
        fault
        for fault in faults
        if len(
            fault_dictionary[fault.name]
        ) > 0
    ]

    undetected_faults = [
        fault
        for fault in faults
        if len(
            fault_dictionary[fault.name]
        ) == 0
    ]

    total_faults = len(faults)

    detected_count = len(
        detected_faults
    )

    coverage = (
        detected_count
        / total_faults
        * 100
    )

    print("\n==============================================")
    print("SSA FAULT COVERAGE")
    print("==============================================")

    print(
        f"Total faults      : {total_faults}"
    )

    print(
        f"Detected faults   : {detected_count}"
    )

    print(
        f"Undetected faults : "
        f"{len(undetected_faults)}"
    )

    print(
        f"Fault coverage    : "
        f"{coverage:.2f}%"
    )

    # =========================================================
    # UNDETECTED FAULTS
    # =========================================================

    if undetected_faults:

        print("\nUndetected faults:")

        for fault in undetected_faults:
            print(
                f"  {fault.name}"
            )

    else:

        print(
            "\nAll SSA faults are detected."
        )
    
    # =========================================================
    # ATPG BASELINE
    # =========================================================

    print("\n==============================================")
    print("EXHAUSTIVE ATPG BASELINE")
    print("==============================================")

    atpg_tests = generate_tests_for_all_faults(
        circuit,
        faults,
        test_vectors
    )
    
    # ============================================================
    # STEP 4: PROBABILISTIC TEST PRIORITIZATION
    # ============================================================

    print("\n" + "=" * 60)
    print("STEP 4: PROBABILISTIC TEST PRIORITIZATION")
    print("=" * 60)

    # ------------------------------------------------------------
    # BUILD TEST -> FAULT MAP
    # ------------------------------------------------------------

    test_fault_map = build_test_fault_map(
        fault_dictionary
    )

    print("\nTEST -> FAULT MAP")
    print("-" * 60)

    for test, detected_faults in sorted(test_fault_map.items()):
        print(
            f"{test} -> "
            f"{len(detected_faults):2d} faults"
        )

    # ------------------------------------------------------------
    # RANK TEST VECTORS
    # ------------------------------------------------------------

    ranked_tests = rank_tests(
        test_vectors,
        fault_dictionary
    )

    print("\nPROBABILISTIC TEST RANKING")
    print("-" * 60)

    print_ranking(ranked_tests)

    # ------------------------------------------------------------
    # COMPACT TEST SET
    # ------------------------------------------------------------

    compacted_tests = compact_test_set(
        ranked_tests
    )

    print("\nCOMPACTED TEST SET")
    print("-" * 60)

    for i, test in enumerate(compacted_tests, 1):
        print(
            f"{i:3d}. {test}"
        )

    # ------------------------------------------------------------
    # TEST-SET REDUCTION
    # ------------------------------------------------------------

    reduction = calculate_test_reduction(
        test_vectors,
        compacted_tests
    )

    print("\nTEST-SET COMPACTION")
    print("-" * 60)

    print(
        f"Original test vectors : {len(test_vectors)}"
    )

    print(
        f"Compacted test vectors: {len(compacted_tests)}"
    )

    print(
        f"Test reduction        : {reduction:.2f}%"
    )

    # ------------------------------------------------------------
    # COMPACTED TEST COVERAGE
    # ------------------------------------------------------------

    compacted_coverage = calculate_fault_coverage(
        compacted_tests,
        fault_dictionary
    )

    print("\nCOMPACTED TEST COVERAGE")
    print("-" * 60)

    print(
        f"Fault coverage        : "
        f"{compacted_coverage:.2f}%"
    )

    print("\n" + "=" * 60)
    print("STEP 4 COMPLETE")
    print("=" * 60)

    atpg_success = 0

    for fault in faults:

        test = atpg_tests[fault.name]

        if test is not None:
            atpg_success += 1

        print(
            f"{fault.name:8s} -> "
            f"{test}"
        )

    print("\nATPG RESULTS")
    print("----------------------------------------------")

    print(
        f"Faults              : {len(faults)}"
    )

    print(
        f"Tests generated     : {atpg_success}"
    )

    print(
        f"ATPG success rate   : "
        f"{atpg_success / len(faults) * 100:.2f}%"
    )
    
    # ============================================================
    # STEP 3: D-ALGORITHM ATPG
    # ============================================================

    print("\n" + "=" * 60)
    print("STEP 3: D-ALGORITHM ATPG")
    print("=" * 60)

    solver = DAlgorithm(circuit)

    d_tests = {}
    d_detected = 0

    for fault in faults:
      result = solver.solve(fault)

      if result is not None:
        d_tests[fault.name] = result
        d_detected += 1

    print(f"\nTotal faults        : {len(faults)}")
    print(f"Test vectors found  : {d_detected}")
    print(
    f"D-Algorithm success : "
    f"{100.0 * d_detected / len(faults):.2f}%"
    )

    print("\nGenerated D-Algorithm tests:")

    for fault_name, test in d_tests.items():
      print(f"  {fault_name:10s} -> {test}")


    # =========================================================
    # EXAMPLE FAULT
    # =========================================================

    example_fault = "10/SA0"

    print("\n==============================================")
    print(
        f"EXAMPLE: {example_fault}"
    )
    print("==============================================")

    for vector in fault_dictionary[
        example_fault
    ]:

        print(
            f"  {vector}"
        )

    print("\n==============================================")
    print("STEP 2 COMPLETE")
    print("==============================================\n")


if __name__ == "__main__":
    main()