# Sources and credit

- P. Kairouz, K. Bonawitz, D. Ramage, “Discrete Distribution Estimation under Local Privacy,” ICML 2016, section 4.1: https://proceedings.mlr.press/v48/kairouz16.html . The standard k-ary randomized-response distribution is a baseline; the synthetic cyclic loss here is not the paper's estimation risk.
- HiGHS project and highspy: https://highs.dev/ . The generator uses the solver; the included certificate checks do not require it.
- Feras A. Saad, Cameron E. Freer, Martin C. Rinard and Vikash K. Mansinghka, [Optimal Approximate Sampling](https://github.com/probcomp/optimal-approximate-sampling/tree/3eb406282e42cd4321db3d808e4c07b53a26a80b), fixed version `3eb406282e42cd4321db3d808e4c07b53a26a80b`. This tool approximates distributions; it does not promise pure DP for arbitrary adjacent rows.
- Fabian Schmid, [lut_sampler](https://github.com/Fable95/lut_sampler/tree/6c8f5248424b01c8398739f3ddd992265c963630), fixed revision `6c8f5248424b01c8398739f3ddd992265c963630`. The tool provides approximate sampling; its distribution-approximation guarantee is distinct from the pure-DP inequalities checked here. See [VERIFICATION-RECORD.md](VERIFICATION-RECORD.md) for the build history.

External source code and papers are linked, not bundled. License and attribution in this package apply to project-owned material only.
