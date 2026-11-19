# Changelog

## 1.0.0 — 2026-11-19

- Initial distribution of the finite-bit table generator, exact-rational certificate checks, separate specification-to-constraints checker, and Python/C samplers for up to 12 fair bits.
- Include 54 historical benchmark conditions: 52 have certified optima when the corrected table is counted. The k=7,b=5 and k=7,b=9 optima remain unresolved; their saved tables are feasible.
- Preserve the correction for k=5,b=11: the old feasible table costs 16093; the certified improved table costs 16092. The old table and historical numerical solver labels remain in the data. Four further example optima and one certified infeasible example are included.
- Include checks for 60 proof records and 108 historical Python/C pairs covering 1,079,232 mapping calls.
- Support C sampler checks with `-dynamiclib` / `.dylib` on macOS and `-shared -fPIC` / `.so` on Linux, retaining `-Werror`.
- Include release metadata, English/Japanese quick starts, and PDF document copies. Code is Apache-2.0; original documentation and data are CC-BY-4.0.

Verification environments, build results and dated editorial changes are recorded in [VERIFICATION-RECORD.md](VERIFICATION-RECORD.md). The guarantee scope is described in the README.
