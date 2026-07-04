from __future__ import annotations

import ast
import math
import operator

SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCS = {
    "sqrt": math.sqrt,
    "round": round,
    "abs": abs,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return SAFE_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return SAFE_OPS[op_type](_safe_eval(node.operand))

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCS:
            args = [_safe_eval(a) for a in node.args]
            return float(SAFE_FUNCS[node.func.id](*args))
        raise ValueError(f"Unsupported function: {ast.dump(node.func)}")

    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def safe_calculate(expression: str) -> str:
    """Safely evaluate a math expression using AST parsing. No eval()."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        if result == int(result):
            return f"{int(result):,}"
        return f"{result:,.4f}"
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError) as e:
        return f"Error: {e}"
