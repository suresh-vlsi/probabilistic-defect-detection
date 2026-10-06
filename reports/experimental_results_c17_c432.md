# Probabilistic Defect Detection --- Experimental Results

## C17 and C432 ISCAS85 Benchmark Evaluation

**Project:** Probabilistic Defect Detection / Probabilistic ATPG\
**Experiment Phase:** Phase 2 --- Experimental Evaluation\
**Benchmarks:** ISCAS85 C17 and C432\
**Fault Model:** Single Stuck-at Fault (SA0 / SA1)\
**Evaluation Date:** 2026-10-06

------------------------------------------------------------------------

## 1. Executive Summary

This report documents the experimental evaluation of the probabilistic
test-generation flow on two ISCAS85 combinational benchmark circuits:
**C17** and **C432**.

The implemented flow combines:

1.  ISCAS85 benchmark parsing
2.  Bounded/random test-vector generation
3.  Single stuck-at fault generation
4.  Fault-dictionary construction through fault simulation
5.  Exhaustive ATPG baseline generation
6.  Test-to-fault mapping
7.  Probabilistic test ranking
8.  Greedy test-set compaction
9.  Final coverage evaluation
10. Test-set reduction analysis

The results demonstrate that probabilistic ranking followed by greedy
compaction can reduce the number of applied test vectors substantially
while preserving very high fault coverage.

### Key results

  -----------------------------------------------------------------------------
  Benchmark   Total Faults      Initial    Compacted         Final         Test
                                  Tests        Tests      Coverage    Reduction
  ----------- ------------ ------------ ------------ ------------- ------------
  **C17**               22           32            4   **100.00%**   **87.50%**

  **C432**             392         1000           19    **99.23%**   **98.10%**
  -----------------------------------------------------------------------------

The C17 benchmark achieves complete fault coverage with only four tests.
For the larger C432 benchmark, only 19 tests are retained from the
original 1000-vector sampled set, corresponding to a **98.10%
reduction** while maintaining **99.23% fault coverage**.

------------------------------------------------------------------------

## 2. Experimental Objective

The objective of this experiment is to evaluate whether a probabilistic
ranking strategy can identify a small, high-value subset of test vectors
from a larger candidate pool.

The central hypothesis is:

> Test vectors that detect a large and diverse set of faults should
> receive higher priority and can be selected preferentially during
> test-set compaction.

The experiment therefore compares the original candidate test set
against the compacted test set using fault coverage and test-count
reduction as the primary metrics.

------------------------------------------------------------------------

## 3. Experimental Flow

The implemented pipeline is:

``` text
             ISCAS85 Benchmark
                     |
                     v
              Parse Circuit
                     |
                     v
       Generate Candidate Test Vectors
                     |
                     v
        Generate Stuck-at Faults
                     |
                     v
          Fault-Dictionary Build
                     |
                     v
         Exhaustive ATPG Baseline
                     |
                     v
           Test-to-Fault Mapping
                     |
                     v
        Probabilistic Test Ranking
                     |
                     v
        Greedy Test-Set Compaction
                     |
                     v
          Compacted Test Coverage
                     |
                     v
            Reduction Analysis
                     |
                     v
              JSON Results
```

------------------------------------------------------------------------

## 4. Metrics

### 4.1 Fault Coverage

Fault coverage is calculated as:

\[ `\text{Fault Coverage}`{=tex} =
`\frac{\text{Number of Detected Faults}}`{=tex}
{`\text{Total Number of Faults}`{=tex}} `\times 100`{=tex} \]

### 4.2 Test-Set Reduction

Test-set reduction is calculated as:

\[ `\text{Reduction}`{=tex} = `\left`{=tex}( 1 -
`\frac{\text{Compacted Test Count}}`{=tex}
{`\text{Original Test Count}`{=tex}} `\right`{=tex}) `\times 100`{=tex}
\]

A higher reduction is desirable provided that fault coverage remains
sufficiently high.

------------------------------------------------------------------------

# 5. C17 Experimental Results

## 5.1 Circuit Characteristics

The C17 benchmark is a small ISCAS85 combinational circuit with:

-   **5 primary inputs**
-   **2 primary outputs**
-   **22 single stuck-at faults**

The experiment evaluated all:

\[ 2\^5 = 32 \]

possible input vectors.

------------------------------------------------------------------------

## 5.2 Probabilistic Ranking

The candidate vectors were ranked according to their estimated
fault-detection value.

The highest-ranked vectors were selected as candidates for greedy
compaction.

Representative high-ranked tests included:

``` text
01001
10111
11110
10111
11000
00111
01110
01111
00011
```

The ranking stage identified vectors capable of detecting large portions
of the fault set.

------------------------------------------------------------------------

## 5.3 Greedy Test-Set Compaction

  Metric                          Result
  ------------------------ -------------
  Original test vectors               32
  Compacted test vectors           **4**
  Compaction time             0.000241 s
  Total faults                        22
  Covered faults                  **22**
  Final coverage             **100.00%**
  Test reduction              **87.50%**
  Undetected faults                **0**

Thus:

\[ 32 `\rightarrow 4`{=tex} \]

test vectors are sufficient to maintain complete coverage.

------------------------------------------------------------------------

## 5.4 C17 Result

The C17 experiment is particularly strong because the compaction stage
achieves:

> **100% stuck-at fault coverage with an 87.50% reduction in test
> vectors.**

This provides a useful sanity-check case for the probabilistic ranking
and compaction implementation.

------------------------------------------------------------------------

# 6. C432 Experimental Results

## 6.1 Circuit Characteristics

The C432 benchmark is substantially larger than C17.

The parsed circuit contains:

  Property                     Value
  ------------------------ ---------
  Primary inputs                  36
  Primary outputs                  7
  Circuit nodes                  196
  Gates                          160
  Single stuck-at faults     **392**

The full input space contains:

\[ 2\^{36} \]

possible input vectors, which is too large for direct exhaustive vector
enumeration in this experiment.

Therefore, a bounded random candidate pool of **1000 test vectors** was
generated.

------------------------------------------------------------------------

## 6.2 Candidate Test Generation

  Metric                          Value
  ------------------------- -----------
  Primary inputs                     36
  Exhaustive vector space     (2\^{36})
  Sampled test vectors         **1000**

The 1000 vectors form the candidate population for probabilistic ranking
and compaction.

------------------------------------------------------------------------

## 6.3 Fault-Dictionary Construction

The fault dictionary was constructed by simulating the candidate vectors
against the complete set of 392 single stuck-at faults.

  Metric                                Result
  ------------------------------ -------------
  Total faults                             392
  Detected faults                      **389**
  Undetected faults                      **3**
  Fault coverage                    **99.23%**
  Dictionary construction time     35.111978 s

The three faults that remained undetected by the candidate population
were:

``` text
259/SA1
347/SA1
379/SA1
```

Therefore, the 1000-vector candidate population itself establishes a
coverage ceiling of:

\[ `\frac{389}{392}`{=tex}`\times100`{=tex} = 99.23% \]

for this experiment.

------------------------------------------------------------------------

## 6.4 Exhaustive ATPG Baseline

The implementation also generated an ATPG baseline.

  Metric                    Result
  ------------------- ------------
  Faults                       392
  Tests generated              389
  ATPG success rate     **99.23%**
  ATPG runtime          1.492599 s

The baseline confirms that the three remaining faults were not covered
by the sampled candidate population.

------------------------------------------------------------------------

## 6.5 Probabilistic Test Ranking

All 1000 candidate tests were ranked.

  Metric               Result
  -------------- ------------
  Ranked tests           1000
  Ranking time     0.069026 s

The ranking stage prioritizes tests with high estimated fault-detection
value.

The highest-ranked candidate in the recorded experiment detected
approximately 107 faults, while other top-ranked candidates detected
roughly 102--110 faults depending on the vector and scoring
contribution.

------------------------------------------------------------------------

## 6.6 Greedy Test-Set Compaction

The greedy compaction algorithm reduced:

\[ 1000 `\rightarrow 19`{=tex} \]

test vectors.

  Metric                  Result
  ----------------- ------------
  Original tests            1000
  Compacted tests         **19**
  Compaction time     0.055622 s
  Test reduction      **98.10%**

The reduction is:

\[ `\left`{=tex}( 1-`\frac{19}{1000}`{=tex}
`\right`{=tex})`\times100`{=tex} = 98.10% \]

------------------------------------------------------------------------

## 6.7 Compacted Coverage

The 19-vector compacted set detects the same 389 faults available to the
original candidate population.

  Metric                    Result
  ------------------- ------------
  Covered faults           **389**
  Total faults                 392
  Final coverage        **99.23%**
  Undetected faults          **3**

Therefore, the compaction process does **not sacrifice any coverage
relative to the original candidate population**.

This is an important result:

> The probabilistic compaction reduces the candidate test set by 98.10%
> while preserving the full 99.23% coverage achievable by the sampled
> candidate pool.

------------------------------------------------------------------------

# 7. C17 vs C432 Comparison

  Metric                        C17         C432
  ------------------- ------------- ------------
  Primary inputs                  5           36
  Primary outputs                 2            7
  Circuit nodes                 ---          196
  Gates                         ---          160
  Total faults                   22          392
  Candidate tests                32         1000
  Covered faults                 22          389
  Initial coverage          100.00%       99.23%
  Compacted tests             **4**       **19**
  Final coverage        **100.00%**   **99.23%**
  Test reduction         **87.50%**   **98.10%**
  Undetected faults               0            3

### Main observation

The larger C432 benchmark exhibits an even greater test-count reduction:

\[ 98.10% \> 87.50% \]

while maintaining the complete coverage obtainable from its sampled
candidate pool.

------------------------------------------------------------------------

# 8. Runtime Comparison

The recorded total experiment runtimes were approximately:

  Benchmark       Total Runtime
  ----------- -----------------
  C17            **0.015884 s**
  C432          **39.181001 s**

The dominant cost for C432 is fault-dictionary construction and fault
simulation.

For C432:

``` text
Fault dictionary construction : 35.111978 s
Probabilistic ranking         : 0.069026 s
Greedy compaction             : 0.055622 s
```

This indicates that the computational bottleneck is currently **fault
simulation / dictionary construction**, rather than the probabilistic
ranking or compaction algorithm.

------------------------------------------------------------------------

# 9. Interpretation

The experimental results support the usefulness of probabilistic test
ranking as a test-set reduction mechanism.

### C17

C17 provides a complete-coverage validation case:

-   32 possible tests
-   22 faults
-   4 selected tests
-   100% coverage
-   87.50% test reduction

### C432

C432 demonstrates scalability to a substantially larger combinational
benchmark:

-   1000 sampled candidate tests
-   392 faults
-   19 selected tests
-   99.23% coverage
-   98.10% test reduction

The three uncovered faults are:

``` text
259/SA1
347/SA1
379/SA1
```

These should be treated as a **candidate-generation limitation**, not as
faults lost by the compaction algorithm, because they were already
absent from the original 1000-vector candidate coverage.

------------------------------------------------------------------------

# 10. Important Experimental Distinction

The C432 result should be interpreted carefully.

The experiment does **not** claim:

> "19 tests provide 99.23% coverage when the entire (2\^{36}) input
> space is considered."

Instead, the demonstrated claim is:

> "19 tests preserve the 99.23% fault coverage obtained by the
> 1000-vector candidate population."

This distinction is important for rigorous research reporting.

The next stage of the project should therefore investigate improved
candidate generation and deterministic ATPG so that the probabilistic
method can be evaluated against a stronger fault-coverage baseline.

------------------------------------------------------------------------

# 11. Current Limitations

### 11.1 Bounded Candidate Generation

C432 uses 1000 sampled vectors rather than exhaustive enumeration
because:

\[ 2\^{36} \]

is prohibitively large for direct enumeration.

### 11.2 Three Undetected Faults

The candidate population does not detect:

``` text
259/SA1
347/SA1
379/SA1
```

Additional ATPG-directed vectors should be generated for these faults.

### 11.3 Fault Simulation Runtime

The C432 experiment spends most of its runtime in fault-dictionary
construction.

Future optimization opportunities include:

-   parallel fault simulation
-   bit-parallel simulation
-   fault dropping
-   fault equivalence collapsing
-   dominance-based fault reduction
-   incremental simulation
-   compact fault signatures

------------------------------------------------------------------------

# 12. Next Research Step

The natural next phase is to combine deterministic ATPG with
probabilistic ranking.

A proposed architecture is:

``` text
                Candidate Generation
                       |
          +------------+------------+
          |                         |
          v                         v
   Random / Probabilistic      ATPG-Directed
       Test Vectors              Vectors
          |                         |
          +------------+------------+
                       |
                       v
              Fault Detection Map
                       |
                       v
             Probabilistic Ranking
                       |
                       v
              Greedy Compaction
                       |
                       v
             Coverage Verification
```

For the three C432 undetected faults, the next experiment should
specifically generate detecting vectors using ATPG and inject them into
the candidate population.

This will allow a stronger comparison between:

1.  Random test generation
2.  Exhaustive/deterministic ATPG
3.  Probabilistic ATPG
4.  Probabilistic ranking + greedy compaction
5.  Hybrid ATPG + probabilistic compaction

------------------------------------------------------------------------

# 13. Reproducibility

The experiments were executed using the project's experiment runner:

``` bash
python experiments/run_experiment.py --benchmark c17.bench
```

and:

``` bash
python experiments/run_experiment.py --benchmark c432.bench
```

Results are stored as JSON files under:

``` text
experiments/results/
├── c17_result.json
└── c432_result.json
```

The corresponding ISCAS85 benchmark files are:

``` text
benchmarks/iscas85/
├── c17.bench
└── c432.bench
```

------------------------------------------------------------------------

# 14. Conclusion

The current experimental evaluation demonstrates that the probabilistic
defect-detection pipeline can achieve substantial test-set compression
while retaining high fault coverage.

The strongest current results are:

-   **C17:** 4 tests, 100% coverage, 87.50% reduction
-   **C432:** 19 tests, 99.23% coverage, 98.10% reduction

The C432 experiment is particularly significant because the system
reduces 1000 candidate vectors to only 19 while preserving all 389
faults detectable by the candidate population.

The next research milestone is to close the remaining three C432
coverage gaps using deterministic ATPG and evaluate whether a hybrid
deterministic-probabilistic approach can achieve **100% fault coverage
with a similarly compact test set**.

------------------------------------------------------------------------

## Experiment Status

**Phase 2 --- Experimental Evaluation: COMPLETE for C17 and C432**

**Next phase:** Hybrid ATPG + Probabilistic Test Ranking + Coverage
Optimization
