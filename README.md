# Fixed-bit differential privacy tables and samplers

**v1.0.0 · Release date: 2026-11-19 · DOI: unassigned** · [Repository](https://github.com/tkmt-lab/fixed-bit-dp-noise-tables) · [日本語](README.ja.md)

Generate finite integer probability tables and samplers using up to 12 fair random bits.
Researchers and engineers can check pure differential privacy on specified adjacency edges and replay exact optimality or infeasibility certificates.

## Try one example

In this package root, use Python 3.11+, NumPy, highspy and clang (macOS/Linux):

```sh
python3 -B cli.py examples/counting.json --out ../dp-output
python3 -B checker.py ../dp-output/result.json
python3 -B checker.py ../dp-output/result.json --proof-only
```

Expected: `OPTIMAL`, `loss: "7/12"`; checks report `PASS`.

Output in `../dp-output/`: `result.json`, `sampler.py`, `sampler.c`, and a shared library for the C sampler checks (`sampler.so` on Linux or `sampler.dylib` on macOS).

## Model, inputs and outputs

For each input state, the table contains nonnegative integer counts summing to 2^b. Given a rational privacy multiplier r, the checker verifies both directions of each specified adjacency edge using integer inequalities. Optional forbidden cells and lower or upper counts are supported. Loss is a nonnegative rational matrix; the generator minimizes expected loss under a uniform input distribution. The fixed benchmark uses complete adjacency, r=2, k=3..8 and b=4..12 with a synthetic cyclic asymmetric loss.

A JSON specification contains `D`, `Y`, `edges`, `r`, `b`, `loss`, and optionally `output_constraints`; see [examples/](examples/). Labels identify inputs and outputs; edge and sampler arguments are array indices. The generator writes `result.json` and, when a table exists, Python and C samplers. Status is `OPTIMAL` or `UNSAT` only when its exact certificate is checked; otherwise a verified table is `FEASIBLE`, and an unresolved search without one is `UNKNOWN`. Invalid specifications produce an error.

Generation with `cli.py` requires Python 3.11+, NumPy, the HiGHS Python binding `highspy`, and the `clang` C compiler. Install these dependencies separately under their own licenses.

## Check the saved results

The `verify.py` entry point needs only Python's standard library and `clang`. In the package root on macOS or Linux:

```sh
python3 -B verify.py
```

Expected: `status: "PASS"`, 60 proof records (56 OPTIMAL, 3 FEASIBLE, 1 UNSAT), and 108 historical Python/C sampler pairs covering 1,079,232 mapping calls. It checks certificates with both the package checker and a separately implemented specification-to-constraints checker, rejects a forged UNSAT certificate, and enumerates every random word. It also checks the improved and example samplers separately. Temporary build files go to a temporary directory.

C sampler checks use `-dynamiclib` and `.dylib` on macOS, or `-shared -fPIC` and `.so` on Linux, retaining `-Werror`. Keep Python assertions enabled when running the checks.

## Saved results

Of the 54 historical direct tables, 51 have independently checked optimality certificates. The old feasible k=5,b=11 table has integer cost 16093; the included corrected table has cost 16092 and an optimality certificate. Counting the improved table, 52 benchmark conditions have certified optima. The old k=7,b=5 and k=7,b=9 tables are feasible with optimality unresolved. Four further example optima and one UNSAT example have checked certificates. The 108 historical sampler records are labelled FEASIBLE; old numerical solver statuses are retained as historical fields.

The proof uses rational dual bounds and complete integer branch trees. The main generator and its checker share a standard-form construction; the separately implemented checker reconstructs it from the specification. See [PROOF.md](PROOF.md) for the method and [claims.json](claims.json) for the claims and their evidence.

## Scope

The guarantees concern the supplied finite specifications and certificates. They do not establish a new general theorem or general novelty, and the synthetic benchmark does not model every privacy application. Verification uses separate implementations within the laboratory and ordinary Python exact-rational checks, not human peer review or a formal proof of the checkers. Historical numerical solver labels are not certificates.

The caller must supply a valid input index and a uniform independent b-bit word. The C and Python samplers each use one lookup for valid arguments; the accessed address depends on the input. Constant time, side-channel resistance, a secure random source, cryptographic security and device performance are not established. Assess the mathematical model and implementation for each intended deployment.

This distribution does not include a comparison of newly generated Rust `lut_sampler` tables or claim a flaw in approximate-sampling tools. Replay environments, results and the build history are in [VERIFICATION-RECORD.md](VERIFICATION-RECORD.md). C sampler checks support macOS and Linux; other operating systems are outside the supported scope. Acknowledgments credit the work used and do not imply endorsement.

## AI use and responsibility

OpenAI Codex agents surveyed the literature, implemented the table generator and samplers, ran the benchmark calculations and drafted documentation.
The specified Codex models included `gpt-6.1-sol`, `gpt-6.1-terra` and `gpt-6-astra`. The records do not identify the exact version for every run.
Other Codex agents wrote separate implementations to compare sampler outputs with the tables and to reconstruct the constraints and check the rational certificates.
These were computational checks by AI agents. They did not involve human peer review.

Anthropic Claude Opus 5.5 helped document a Linux test that exposed a macOS-only compiler flag.
Google Gemini drafted a note explaining how distribution approximation differs from pure differential privacy. The note came from a Gemini 4 environment and does not record the exact model version.
The author, Tatsuhiko Takimoto, takes responsibility for the code, data and claims in this package.

## Acknowledgments and contact

Peter Kairouz, Keith Bonawitz and Daniel Ramage's work on discrete distribution estimation under local privacy supplies the standard k-ary randomized-response baseline. We thank them, the HiGHS developers for the optimization software, Feras A. Saad, Cameron E. Freer, Martin C. Rinard and Vikash K. Mansinghka for their public distribution-approximation implementation, Optimal Approximate Sampling, and Fabian Schmid for `lut_sampler` and its published approximation tables. See [SOURCES.md](SOURCES.md) for the references.

Author: Tatsuhiko Takimoto. Research contact: [research@tatsuhikotakimoto.com](mailto:research@tatsuhikotakimoto.com).

Project-owned code is Apache-2.0 and original data and documentation are CC-BY-4.0; see [LICENSE](LICENSE). Third-party software and papers are available from their respective sources under their own licenses.

## Release history and document copies

[CHANGELOG.md](CHANGELOG.md) records the release history.

[PACKAGE.pdf](PACKAGE.pdf) contains this README, the certificate method, verification record, sources and changelog. [README.ja.pdf](README.ja.pdf) is the Japanese README. `MANIFEST.sha256` covers every package file except itself, including these PDFs. To rebuild them, install Pandoc, XeLaTeX with xeCJK, DejaVu and Noto CJK fonts, then run `python3 -B build_docs.py`. Follow the manifest regeneration command in [build_docs.py](build_docs.py) and run `python3 -B verify.py` again. These additional tools are used only for building the PDFs.
