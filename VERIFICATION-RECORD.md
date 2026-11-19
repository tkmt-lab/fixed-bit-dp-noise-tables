# Verification record

## Table and certificate checks — 2026-11-01 (JST)

An independent verification implementation checked integer tables, sampler mappings and losses: 286 table artifacts (including duplicate representations), 230 Python/C code artifacts and 1,084,384 mapping calls. It independently verified 37 integer optima via an exact rational reduced LP. Ten older Python samplers used input-dependent CDF loops; those artifacts were excluded from the one-lookup samplers in this package. These were separate-implementation checks within the laboratory, not external human peer review.

A second independent implementation reconstructed the constraint rows from the public specification and checked 56 OPTIMAL certificates and one UNSAT certificate, with 186 branches and 243 leaves, and rejected six corrupted certificates. It confirmed the k=5,b=11 correction from integer cost 16093 to 16092. The 56 consisted of 51 original benchmark optima, one improved benchmark optimum and four examples. Two other benchmark optima remained unresolved. The verification retained input hashes and detailed reports.

## Package snapshot and build checks — 2026-11-02

The snapshot included the independent certificate-checking implementation and a verification command for all 60 proof records, a forged UNSAT control and 108 historical Python/C mapping pairs. It also included separate checks for the improved and example samplers. The independently checked standard form used a separate implementation; the main generator and main checker shared their own model-construction function. The checks did not constitute human peer review or a formal verification of the Python checkers.

The historical solver labels in the sampler result files were conservatively changed to FEASIBLE; their original numerical labels were retained as historical metadata. Certified claims were based on the separate proof records, not on those labels.

In the build records fixed in this snapshot, Rust `lut_sampler` failed to build unchanged because two `maestro` revisions yielded incompatible types. A patched variant with matching revisions was stopped at an RSS safety threshold. Newly generated tables from that build were therefore not compared in this snapshot. Previously published tables studied separately were not outputs of that patched build. The source-reading and build records were retained; the public sources and fixed versions are listed in [SOURCES.md](SOURCES.md).

The portability correction was checked on macOS; only Linux flag selection was tested at that time. The snapshot recorded neither publication nor a DOI. Its scope excluded subsequent Rust comparisons.

## Linux replay and metadata — 2026-11-05

A verification run replayed this package natively on Debian Linux with clang 19.1.7: all 60 proof records, the forged UNSAT rejection, and 108 historical sampler pairs (1,079,232 mapping calls) passed. The counting example returned OPTIMAL with loss 7/12 and passed the normal and proof-only checks. The saved generation runs used NumPy 2.5.4 and highspy 1.15.1. This replay supplemented the macOS and Linux flag-selection checks recorded on 2026-11-02; it added neither a mathematical claim nor human peer review.

The run also identified missing release metadata, a missing changelog and the quick-start placement. The subsequent editorial correction supplied these for the distribution dated 2026-11-19 without changing mathematical statements, numeric data, certificates or solver/checker code. The package was assembled on 2026-11-05. That editorial work performed no public upload or DOI registration; the distribution date was metadata, not evidence of either operation.

## Documentation edits — 2026-11-06

The English and Japanese READMEs were arranged as title, release metadata and DOI status, result and purpose, then one runnable example. Scope statements were consolidated, Japanese acknowledgments made specific, and the author's research contact added. Author credits and the generated-file description were expanded; temporary-directory names and CLI diagnostics were made specific to the public tool. Mathematical statements, numeric data, certificates and solver/checker logic were preserved.

The final wording pass described the release history directly and consolidated dated build, verification and editorial history in this record. The independent checker's module description was changed to describe its input and function. PDFs and the file manifest were regenerated. These documentation edits performed no public upload or DOI registration.
