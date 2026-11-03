# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Bounded JSON property format for running user-defined Z3 checks."""

from __future__ import annotations

import math
import re
from typing import Any

from .checker import CheckResult, require_z3, z3

MAX_VARIABLES = 16
MAX_CONSTRAINTS = 32
MAX_EXPRESSION_NODES = 128
MAX_EXPRESSION_DEPTH = 16
MAX_SOLVER_TIMEOUT_MS = 2_000
_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")
_PROPERTY_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
_COMPARISONS = {"eq", "ne", "lt", "le", "gt", "ge"}


def _number(value: Any, label: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a JSON number")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or abs(value) > 1e100:
        raise ValueError(f"{label} must be finite")
    return value


def _touch(depth: int, counter: list[int]) -> None:
    counter[0] += 1
    if depth > MAX_EXPRESSION_DEPTH:
        raise ValueError(f"expression depth exceeds {MAX_EXPRESSION_DEPTH}")
    if counter[0] > MAX_EXPRESSION_NODES:
        raise ValueError(f"expression exceeds {MAX_EXPRESSION_NODES} nodes")


def _parse_term(node: Any, variables: dict[str, Any], depth: int, counter: list[int]):
    _touch(depth, counter)
    if not isinstance(node, dict):
        raise ValueError("arithmetic expressions must be JSON objects")
    if set(node) == {"var"}:
        name = node["var"]
        if not isinstance(name, str) or name not in variables:
            raise ValueError(f"unknown variable: {name}")
        return variables[name]
    if set(node) == {"const"}:
        value = _number(node["const"], "constant")
        return z3.RealVal(str(value))
    if len(node) != 1:
        raise ValueError("arithmetic expression must contain exactly one operator")
    operator, operands = next(iter(node.items()))
    if operator not in {"add", "sub", "mul"} or not isinstance(operands, list):
        raise ValueError(f"unsupported arithmetic expression: {operator}")
    min_operands = 2
    max_operands = 8
    if len(operands) < min_operands or len(operands) > max_operands:
        raise ValueError(f"{operator} requires 2..8 operands")
    parsed = [_parse_term(item, variables, depth + 1, counter) for item in operands]
    if operator == "add":
        return sum(parsed[1:], parsed[0])
    if operator == "mul":
        result = parsed[0]
        for value in parsed[1:]:
            result = result * value
        return result
    if len(parsed) != 2:
        raise ValueError("sub requires exactly 2 operands")
    return parsed[0] - parsed[1]


def _parse_constraint(node: Any, variables: dict[str, Any], depth: int, counter: list[int]):
    _touch(depth, counter)
    if not isinstance(node, dict) or not isinstance(node.get("op"), str):
        raise ValueError("constraints must be JSON objects with an op")
    operator = node["op"]
    if operator in _COMPARISONS:
        if set(node) != {"op", "left", "right"}:
            raise ValueError(f"{operator} requires left and right terms")
        left = _parse_term(node["left"], variables, depth + 1, counter)
        right = _parse_term(node["right"], variables, depth + 1, counter)
        return {
            "eq": left == right,
            "ne": left != right,
            "lt": left < right,
            "le": left <= right,
            "gt": left > right,
            "ge": left >= right,
        }[operator]
    if operator in {"and", "or"}:
        if set(node) != {"op", "args"} or not isinstance(node["args"], list):
            raise ValueError(f"{operator} requires an args list")
        args = node["args"]
        if not 2 <= len(args) <= 8:
            raise ValueError(f"{operator} requires 2..8 constraints")
        parsed = [
            _parse_constraint(item, variables, depth + 1, counter)
            for item in args
        ]
        return z3.And(*parsed) if operator == "and" else z3.Or(*parsed)
    if operator == "not":
        if set(node) != {"op", "arg"}:
            raise ValueError("not requires one arg")
        return z3.Not(_parse_constraint(node["arg"], variables, depth + 1, counter))
    raise ValueError(f"unsupported constraint operator: {operator}")


def run_declarative_property(spec: Any) -> CheckResult:
    """Run a bounded declarative property without evaluating user code."""
    if not isinstance(spec, dict):
        raise ValueError("property must be a JSON object")
    required = {"name", "description", "variables", "constraints", "expected"}
    if set(spec) != required:
        raise ValueError(f"property fields must be exactly: {', '.join(sorted(required))}")

    name = spec["name"]
    description = spec["description"]
    if not isinstance(name, str) or not _PROPERTY_NAME.fullmatch(name):
        raise ValueError("name must be 1..80 safe identifier characters")
    if not isinstance(description, str) or len(description) > 500:
        raise ValueError("description must be a string no longer than 500 characters")
    expected = spec["expected"]
    if not isinstance(expected, str) or expected not in {"sat", "unsat"}:
        raise ValueError("expected must be 'sat' or 'unsat'")

    raw_variables = spec["variables"]
    if not isinstance(raw_variables, dict) or not 1 <= len(raw_variables) <= MAX_VARIABLES:
        raise ValueError(f"variables must contain 1..{MAX_VARIABLES} bounded variables")
    constraints = spec["constraints"]
    if not isinstance(constraints, list) or not 1 <= len(constraints) <= MAX_CONSTRAINTS:
        raise ValueError(f"constraints must contain 1..{MAX_CONSTRAINTS} expressions")

    variable_specs = []
    for variable_name, definition in raw_variables.items():
        if not isinstance(variable_name, str) or not _IDENTIFIER.fullmatch(variable_name):
            raise ValueError(f"invalid variable name: {variable_name}")
        if not isinstance(definition, dict) or set(definition) != {"sort", "min", "max"}:
            raise ValueError(f"{variable_name} must define exactly sort, min, and max")
        sort = definition["sort"]
        if not isinstance(sort, str) or sort not in {"int", "real"}:
            raise ValueError(f"{variable_name}.sort must be 'int' or 'real'")
        minimum = _number(definition["min"], f"{variable_name}.min")
        maximum = _number(definition["max"], f"{variable_name}.max")
        if minimum > maximum:
            raise ValueError(f"{variable_name}.min must not exceed max")
        if sort == "int":
            if type(minimum) is not int or type(maximum) is not int:
                raise ValueError(f"{variable_name} integer bounds must be integers")
        variable_specs.append((variable_name, sort, minimum, maximum))

    require_z3()
    solver = z3.Solver()
    solver.set(timeout=MAX_SOLVER_TIMEOUT_MS)
    variables: dict[str, Any] = {}
    for variable_name, sort, minimum, maximum in variable_specs:
        variable = z3.Int(variable_name) if sort == "int" else z3.Real(variable_name)
        variables[variable_name] = variable
        solver.add(variable >= minimum, variable <= maximum)
    counter = [0]
    for constraint in constraints:
        solver.add(_parse_constraint(constraint, variables, 0, counter))

    result = solver.check()
    expected_result = z3.sat if expected == "sat" else z3.unsat
    model: dict[str, str] = {}
    if result == z3.sat:
        z3_model = solver.model()
        model = {decl.name(): str(z3_model[decl]) for decl in z3_model.decls()}
    return CheckResult(
        name=name,
        status="PASS" if result == expected_result else "FAIL",
        z3_result=str(result),
        model=model,
        description=description,
    )
