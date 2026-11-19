"""JSON -> integer DP table, Python/C code and exact verification."""
import argparse
import json
import math
import resource
import sys
from fractions import Fraction as F
from pathlib import Path

import highspy
import numpy as np
import checker
import prover


def rational(value):
    if type(value) is int or isinstance(value, str):
        return F(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        if type(value["numerator"]) is int and type(value["denominator"]) is int:
            return F(value["numerator"], value["denominator"])
    raise ValueError("use an integer, fraction string, or numerator/denominator object")


def validate(spec):
    allowed = {"D", "Y", "edges", "r", "b", "loss", "output_constraints"}
    if set(spec)-allowed or allowed-{"output_constraints"}-set(spec):
        raise ValueError("missing or unknown specification fields")
    for key in ("D", "Y"):
        if not isinstance(spec[key], list) or not 1 <= len(spec[key]) <= 32:
            raise ValueError("D and Y must each contain 1..32 labels")
        if any(type(v) not in (int, str) for v in spec[key]) or len(set(spec[key])) != len(spec[key]):
            raise ValueError("labels must be unique integers or strings")
    nd, ny = len(spec["D"]), len(spec["Y"])
    if type(spec["b"]) is not int or not 0 <= spec["b"] <= 12:
        raise ValueError("supported b values are integers in [0,12]")
    r = rational(spec["r"])
    if r < 1 or max(r.numerator, r.denominator) > 10**6:
        raise ValueError("r >= 1, numerator and denominator <= 1000000")
    if not isinstance(spec["edges"], list):
        raise ValueError("edges must be a list")
    for edge in spec["edges"]:
        if not isinstance(edge, list) or len(edge) != 2 or any(type(x) is not int or not 0 <= x < nd for x in edge):
            raise ValueError("edge endpoints must be D indices")
    if len(spec["loss"]) != nd or any(len(row) != ny for row in spec["loss"]):
        raise ValueError("loss shape mismatch")
    for row in spec["loss"]:
        for value in row:
            q = rational(value)
            if not 0 <= q <= 10**6 or q.denominator > 10**6:
                raise ValueError("loss outside supported range")
    c = spec.get("output_constraints", {})
    if not isinstance(c, dict) or set(c)-{"forbidden", "min_counts", "max_counts"}:
        raise ValueError("unknown output constraint")
    for pair in c.get("forbidden", []):
        if len(pair) != 2 or type(pair[0]) is not int or type(pair[1]) is not int or not (0 <= pair[0] < nd and 0 <= pair[1] < ny):
            raise ValueError("forbidden pair must be D,Y indices")
    for key in ("min_counts", "max_counts"):
        if key in c:
            if len(c[key]) != nd or any(len(row) != ny for row in c[key]):
                raise ValueError("bound shape mismatch")
            if any(type(v) is not int or not 0 <= v <= 2**spec["b"] for row in c[key] for v in row):
                raise ValueError("count bound outside [0,2^b]")
    return spec


def model(spec, continuous=False, rounded=None, distance=None, budget=5):
    validate(spec)
    nd, ny, s = len(spec["D"]), len(spec["Y"]), 2**spec["b"]
    cells = nd*ny
    scale = 1 if continuous else s
    h = highspy.Highs()
    for key, value in {"threads": 1, "parallel": "off", "random_seed": 0,
                       "output_flag": False, "time_limit": min(120, budget),
                       "mip_rel_gap": 0.0, "mip_abs_gap": 0.0}.items():
        if h.setOptionValue(key, value) != highspy.HighsStatus.kOk:
            raise RuntimeError(f"solver option rejected: {key}")
    constraints = spec.get("output_constraints", {})
    forbidden = set(map(tuple, constraints.get("forbidden", [])))
    for i in range(cells+(cells if rounded is not None else 0)):
        lo, hi = 0, highspy.kHighsInf
        if i < cells:
            d, y = divmod(i, ny)
            if "min_counts" in constraints:
                lo = constraints["min_counts"][d][y]*scale/s
            if "max_counts" in constraints:
                hi = constraints["max_counts"][d][y]*scale/s
            if (d, y) in forbidden:
                hi = 0
            cost = float(rational(spec["loss"][d][y]))
        else:
            cost = 0
        h.addVar(lo, hi)
        if not continuous:
            h.changeColIntegrality(i, highspy.HighsVarType.kInteger)
        h.changeColCost(i, int(i >= cells) if rounded is not None and distance is None else cost)

    def row(terms, lower, upper):
        indices, values = zip(*terms)
        h.addRow(lower, upper, len(indices), np.array(indices, dtype=np.int32), np.array(values, dtype=float))

    for d in range(nd):
        row([(d*ny+y, 1) for y in range(ny)], scale, scale)
    r = rational(spec["r"])
    for d, e in spec["edges"]:
        if d == e:
            continue
        for left, right in ((d, e), (e, d)):
            for y in range(ny):
                row([(left*ny+y, r.denominator), (right*ny+y, -r.numerator)], -highspy.kHighsInf, 0)
    if rounded is not None:
        for i, v in enumerate(sum(rounded, [])):
            row([(i, 1), (cells+i, -1)], -highspy.kHighsInf, v)
            row([(i, -1), (cells+i, -1)], -highspy.kHighsInf, -v)
        if distance is not None:
            row([(cells+i, 1) for i in range(cells)], distance, distance)
    return h


def solve(spec, budget=5, rounded=None, distance=None, start=None):
    validate(spec)
    result = {"spec": spec, "status": "UNKNOWN", "table": None, "samplers": None}
    result["optimization_scope"] = ("original_spec_loss" if rounded is None else
                                    "minimum_l1_projection" if distance is None else "loss_with_fixed_l1")
    if rounded is not None:
        result.update(repair_reference=rounded, fixed_l1_distance=distance)
    if budget <= 0:
        result["reason"] = "zero budget; solver not run"
        return result
    c = spec.get("output_constraints", {})
    nd, ny, s = len(spec["D"]), len(spec["Y"]), 2**spec["b"]
    forbidden = set(map(tuple, c.get("forbidden", [])))
    for d in range(nd):
        lower = c.get("min_counts", [[0]*ny for _ in range(nd)])[d]
        upper = [0 if (d, y) in forbidden else c.get("max_counts", [[s]*ny for _ in range(nd)])[d][y] for y in range(ny)]
        if any(a > b for a, b in zip(lower, upper)) or sum(lower) > s or sum(upper) < s:
            result.update(status="UNSAT", reason="exact contradiction in local output bounds")
            return result
    h = model(spec, rounded=rounded, distance=distance, budget=budget)
    if start is not None and not checker.table_errors(spec, start):
        values = sum(start, [])
        if rounded is not None:
            values += [abs(a-b) for a, b in zip(values, sum(rounded, []))]
        if distance is None or sum(values[nd*ny:]) == distance:
            h.setSolution(len(values), np.arange(len(values), dtype=np.int32), np.array(values, dtype=float))
    h.run()
    status = h.modelStatusToString(h.getModelStatus())
    info, sol = h.getInfo(), h.getSolution()
    result.update(solver_status=status, seconds=h.getRunTime(), nodes=info.mip_node_count,
                  solver_objective=info.objective_function_value if math.isfinite(info.objective_function_value) else None,
                  solver_lower_bound=info.mip_dual_bound if math.isfinite(info.mip_dual_bound) else None)
    if h.getModelStatus() == highspy.HighsModelStatus.kInfeasible:
        result["status"] = "UNSAT"
        return result
    if not sol.value_valid:
        return result
    nd, ny = len(spec["D"]), len(spec["Y"])
    floats = sol.col_value[:nd*ny]
    values = [round(x) for x in floats]
    table = [values[d*ny:(d+1)*ny] for d in range(nd)]
    if any(abs(x-y) > 1e-5 for x, y in zip(floats, values)) or checker.table_errors(spec, table):
        result["reason"] = "incumbent failed exact checking"
        return result
    result.update(status="FEASIBLE",  # Numerical solver status is not an independently checked integer certificate.
                  table=table, loss=str(checker.loss(spec, table)))
    if rounded is not None:
        result["l1_distance"] = sum(abs(a-b) for a, b in zip(values, sum(rounded, [])))
    return result


def lp(spec):
    h = model(spec, continuous=True)
    h.run()
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        raise RuntimeError("LP not optimal")
    ny = len(spec["Y"])
    values = [F(v).limit_denominator(10**6) for v in h.getSolution().col_value]
    table = [values[d*ny:(d+1)*ny] for d in range(len(spec["D"]))]
    if checker.table_errors(spec, table, total=1, integer=False):
        raise RuntimeError("LP rational reconstruction invalid")
    return table


def round_lp(table, bits):
    rounded = []
    for row in table:
        scaled = [p*2**bits for p in row]
        vals = [p.numerator//p.denominator for p in scaled]
        order = sorted(range(len(row)), key=lambda y: (-(scaled[y]-vals[y]), y))
        for y in order[:2**bits-sum(vals)]:
            vals[y] += 1
        rounded.append(vals)
    return rounded


def emit(result, directory):
    if result["status"] in ("FEASIBLE", "OPTIMAL", "UNSAT"):
        certificate, stats = prover.produce(result["spec"], result["table"])
        if certificate is None and stats.get("better_candidate") is not None:
            result["previous_loss"] = result.get("loss")
            result["table"] = stats["better_candidate"]
            assert not checker.table_errors(result["spec"], result["table"])
            result["loss"] = str(checker.loss(result["spec"], result["table"]))
            certificate, stats = prover.produce(result["spec"], result["table"])
        result["certificate"] = certificate
        result["proof_stats"] = stats
        result["status"] = ("OPTIMAL" if result["table"] is not None else "UNSAT") if certificate else ("FEASIBLE" if result["table"] is not None else "UNKNOWN")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if result["table"] is not None:
        mapping = [[y for y, n in enumerate(row) for _ in range(n)] for row in result["table"]]
        bits = result["spec"]["b"]
        (directory/"sampler.py").write_text('"""Generated mapping; caller supplies valid input index and uniform b-bit word."""\n'
            + f'BITS = {bits}\nMAP = {mapping!r}\n\ndef sample_from_bits(d, word):\n    return MAP[d][word]\n')
        rows = ["{"+",".join(map(str, row))+"}" for row in mapping]
        (directory/"sampler.c").write_text('/* Generated. Valid d index and uniform b-bit word are caller preconditions.\n'
            ' * One address-dependent load; no constant-time guarantee. No RNG inside. */\n#include <stdint.h>\n'
            + f'static const uint16_t MAP[{len(mapping)}][{2**bits}] = {{\n'+",\n".join(rows)+'\n};\n'
            + 'uint16_t sample_from_bits(uint32_t d, uint32_t word) {\n    return MAP[d][word];\n}\n')
        result["samplers"] = {"python": "sampler.py", "c": "sampler.c", "bits": bits,
                              "input_contract": "valid D index and uniform word in [0,2^b)",
                              "constant_time_claim": False}
    path = directory/"result.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    result["verification"] = checker.verify(path)
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--time-limit", type=float, default=5)
    a = p.parse_args()
    try:
        spec = validate(json.loads(a.spec.read_text()))
        if not math.isfinite(a.time_limit) or a.time_limit < 0:
            raise ValueError("invalid time limit")
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        p.error(str(exc))
    resource.setrlimit(resource.RLIMIT_CPU, (7200, 7200))
    result = solve(spec, a.time_limit)
    emit(result, a.out)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
