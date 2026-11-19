"""Stdlib checker, independent of solver and compiler; standalone entry point."""
import argparse
import ctypes
import importlib.util
import json
import re
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path


def shared_library_settings():
    if sys.platform == 'darwin':
        return '.dylib', ['-dynamiclib']
    if sys.platform.startswith('linux'):
        return '.so', ['-shared', '-fPIC']
    raise RuntimeError('C sampler checks support macOS and Linux')


def ratio(value):
    if isinstance(value, dict):
        assert set(value) == {"numerator", "denominator"}
        assert type(value["numerator"]) is int and type(value["denominator"]) is int
        return Q(value["numerator"], value["denominator"])
    assert type(value) is int or isinstance(value, str)
    return Q(value)


def table_errors(spec, table, total=None, integer=True):
    nd, ny = len(spec["D"]), len(spec["Y"])
    assert 1 <= nd <= 32 and 1 <= ny <= 32
    assert type(spec["b"]) is int and 0 <= spec["b"] <= 12
    assert len(spec["loss"]) == nd and all(len(row) == ny for row in spec["loss"])
    assert all(ratio(v) >= 0 for row in spec["loss"] for v in row)
    s = 2**spec["b"] if total is None else total
    if len(table) != nd or any(len(row) != ny for row in table):
        return ["shape"]
    errors = []
    for d in range(nd):
        if sum(table[d]) != s:
            errors.append(f"row_sum:{d}")
        for y, n in enumerate(table[d]):
            if n < 0 or (integer and type(n) is not int):
                errors.append(f"count:{d},{y}")
    r = ratio(spec["r"])
    assert r >= 1
    for d, e in spec["edges"]:
        assert type(d) is int and type(e) is int and 0 <= d < nd and 0 <= e < nd
        for left, right in ((d, e), (e, d)):
            for y in range(ny):
                if r.denominator*table[left][y] > r.numerator*table[right][y]:
                    errors.append(f"DP:{left},{right},{y}")
    constraints = spec.get("output_constraints", {})
    for d, y in constraints.get("forbidden", []):
        if table[d][y] != 0:
            errors.append(f"forbidden:{d},{y}")
    for key, sign in (("min_counts", 1), ("max_counts", -1)):
        for d, row in enumerate(constraints.get(key, [])):
            for y, v in enumerate(row):
                if sign*(table[d][y]-Q(v*s, 2**spec["b"])) < 0:
                    errors.append(f"{key}:{d},{y}")
    return errors


def loss(spec, table, total=None):
    s = 2**spec["b"] if total is None else total
    return sum(Q(v)*ratio(spec["loss"][d][y]) for d, row in enumerate(table) for y, v in enumerate(row))/(len(table)*s)


def verify(result_path, compile_c=True):
    result_path = Path(result_path)
    result = json.loads(result_path.read_text())
    assert result["status"] in ("OPTIMAL", "FEASIBLE", "UNSAT", "UNKNOWN")
    if result["status"] not in ("OPTIMAL", "FEASIBLE"):
        assert result["table"] is None and result.get("samplers") is None
        return {"status_protocol": "PASS", "status": result["status"], "words": 0}
    spec, table = result["spec"], result["table"]
    errors = table_errors(spec, table)
    assert not errors, errors
    assert str(loss(spec, table)) == result["loss"]
    if result.get("fixed_l1_distance") is not None:
        distance = sum(abs(a-b) for a, b in zip(sum(table, []), sum(result["repair_reference"], [])))
        assert distance == result["fixed_l1_distance"] == result["l1_distance"]
    module_path = result_path.parent/result["samplers"]["python"]
    module_spec = importlib.util.spec_from_file_location("generated_sampler", module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    functions = {"python": module.sample_from_bits}
    if compile_c:
        c_path = result_path.parent/result["samplers"]["c"]
        body = re.search(r"uint16_t sample_from_bits\([^)]*\)\s*\{([^}]+)\}", c_path.read_text()).group(1)
        assert body.strip() == "return MAP[d][word];", "unexpected C control flow"
        assert result["samplers"]["bits"] == spec["b"]
        suffix, shared_flags = shared_library_settings()
        library_path = c_path.with_suffix(suffix)
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", *shared_flags,
                        str(c_path), "-o", str(library_path)], check=True, capture_output=True, timeout=30)
        lib = ctypes.CDLL(str(library_path.resolve()))
        lib.sample_from_bits.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        lib.sample_from_bits.restype = ctypes.c_uint16
        functions["c"] = lib.sample_from_bits
    total_words = 0
    for name, sample in functions.items():
        for d in range(len(table)):
            hist = [0]*len(spec["Y"])
            for word in range(2**spec["b"]):
                y = sample(d, word)
                assert 0 <= y < len(hist)
                hist[y] += 1
            assert hist == table[d], (name, d)
            total_words += 2**spec["b"]
    return {"status": "PASS", "integer_dp": "PASS", "output_constraints": "PASS",
            "mapping_languages": list(functions), "words": total_words,
            "c_source_single_lookup": bool(compile_c),
            "c_compiler": "clang -std=c11 -O2" if compile_c else None}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("result", type=Path)
    p.add_argument("--python-only", action="store_true")
    a = p.parse_args()
    print(json.dumps(verify(a.result, not a.python_only), indent=2))
