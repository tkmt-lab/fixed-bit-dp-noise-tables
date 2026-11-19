# Certificate method

The nonnegative integer counts form x. The specification is converted to rational inequalities Ax≥b and the rational loss is scaled to an integer objective cᵀx. A nonnegative rational dual λ with Aᵀλ≤c yields the lower bound cᵀx≥bᵀλ; integrality allows the ceiling of the bound. An infeasible leaf has λ≥0, Aᵀλ≤0 and bᵀλ>0, a contradiction for x≥0.

A branch on integer xᵢ at integer t covers xᵢ≤t and xᵢ≥t+1. The checker rebuilds those constraints and checks every leaf. A verified feasible table and a tree whose feasible leaves meet its integer cost establish OPTIMAL. A tree of infeasible leaves establishes UNSAT. The package's independent checker separately reconstructs the rows from the specification. These are ordinary exact-rational checks, not a machine-checked formal proof of the implementations.
