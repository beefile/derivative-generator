import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set, Tuple

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from trail_logger import clear_trail
from ui_design import app, compute_btn, entry, final_value, trail_box, trail_meta

# ---------------------- PARSER SETUP ----------------------
# Default symbol for constant-only expressions
default_var = sp.symbols("x")

TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)
LOCAL_DICT = {
    "x": default_var,
    "pi": sp.pi,
    "e": sp.E,
    "ln": sp.log,
    "log": sp.log,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "sqrt": sp.sqrt,
}
LIBRARY_NAME = "SymPy"


# ---------------------- DATA STRUCTURES ----------------------
@dataclass
class Step:
    text: str
    rule: str


# ---------------------- INPUT HANDLING ----------------------
def normalize_input(expr: str) -> str:
    replacements = {
        "^": "**",
        "×": "*",
        "·": "*",
        "÷": "/",
        "−": "-",
        "–": "-",
        "—": "-",
    }
    for old, new in replacements.items():
        expr = expr.replace(old, new)
    return expr.strip()


def validate_expression(expr: str) -> Tuple[bool, str, Optional[sp.Expr]]:
    expr = expr.strip()
    if not expr:
        return False, "Expression cannot be empty", None
    if expr.count("(") != expr.count(")"):
        return False, "Unmatched parentheses", None

    normalized = normalize_input(expr)
    try:
        parsed = parse_expr(
            normalized,
            transformations=TRANSFORMATIONS,
            local_dict=LOCAL_DICT,
            evaluate=True,
        )
    except Exception as exc:
        return False, f"Unable to parse expression: {exc}", None

    return True, "Validation passed", parsed


# ---------------------- META SUMMARY ----------------------
def _set_meta(runtime_s=None, timestamp=None, iterations=None):
    rt = f"{runtime_s:.3f}s" if runtime_s is not None else "--"
    ts = timestamp if timestamp else "--"
    it = str(iterations) if iterations is not None else "--"

    trail_meta.configure(
        text=f"Runtime: {rt}   |   Timestamp: {ts}   |   Iterations: {it}   |   Library: {LIBRARY_NAME}"
    )


# ---------------------- DIFFERENTIATION LOGIC ----------------------
def differentiate_with_steps(expr: sp.Expr, var: sp.Symbol) -> Tuple[sp.Expr, List[Step], Set[str]]:
    steps: List[Step] = []
    used_rules: Set[str] = set()

    def d(expr_inner: sp.Expr) -> str:
        return f"d/d{var}({sp.sstr(expr_inner)})"

    def record(text: str, rule: str):
        steps.append(Step(text=text, rule=rule))
        used_rules.add(rule)

    def recurse(node: sp.Expr) -> sp.Expr:
        # Constant Rule
        if node.is_Number:
            record(f"{d(node)} = 0", "Constant Rule")
            return sp.Integer(0)

        # Variable Rule
        if node == var:
            record(f"{d(node)} = 1", "Variable Rule")
            return sp.Integer(1)

        # Sum and Difference Rule
        if node.is_Add:
            pieces = [d(arg) for arg in node.args]
            record(f"{d(node)} = " + " + ".join(pieces), "Sum and Difference Rule")
            derivatives = [recurse(arg) for arg in node.args]
            combined = sp.Add(*derivatives)
            record(f"= {sp.sstr(combined)}", "Sum and Difference Rule")
            return combined

        # Constant Multiple Rule (coeff * f(x))
        coeff, factors = node.as_coeff_mul()
        inner = sp.Mul(*factors)
        if coeff != 1 and inner != 1:
            record(
                f"{d(node)} = {coeff} * {d(inner)}",
                "Constant Multiple Rule",
            )
            inner_deriv = recurse(inner)
            derivative = coeff * inner_deriv
            record(f"= {sp.sstr(derivative)}", "Constant Multiple Rule")
            return derivative

        # Quotient Rule
        num, den = node.as_numer_denom()
        if den != 1 and (num.has(var) or den.has(var)):
            record(
                f"{d(node)} -> Apply Quotient Rule",
                "Quotient Rule",
            )
            dnum = recurse(num)
            dden = recurse(den)
            derivative = (dnum * den - num * dden) / (den ** 2)
            rule_line = (
                f"= (({sp.sstr(dnum)})*({sp.sstr(den)}) - ({sp.sstr(num)})*({sp.sstr(dden)})) / ({sp.sstr(den)}**2)"
            )
            record(rule_line, "Quotient Rule")
            return derivative

        # Product Rule
        if node.is_Mul:
            factors = node.args
            if len(factors) >= 2:
                f = factors[0]
                g = sp.Mul(*factors[1:]) if len(factors) > 2 else factors[1]
                record(
                    f"{d(node)} -> Apply Product Rule with f={sp.sstr(f)}, g={sp.sstr(g)}",
                    "Product Rule",
                )
                df = recurse(f)
                dg = recurse(g)
                derivative = df * g + f * dg
                record(
                    f"= ({sp.sstr(df)})*({sp.sstr(g)}) + ({sp.sstr(f)})*({sp.sstr(dg)})",
                    "Product Rule",
                )
                return derivative

        # Power Rule (x^n)
        if node.is_Pow and node.base == var and node.exp.is_number:
            derivative = node.exp * var ** (node.exp - 1)
            record(
                f"{d(node)} = {sp.sstr(node.exp)}*{var}^{sp.sstr(node.exp - 1)}",
                "Power Rule",
            )
            return derivative

        # Chain Rule for (g(x))^n
        if node.is_Pow and node.exp.is_number and node.base.has(var):
            record(f"{d(node)} -> Apply Chain Rule", "Chain Rule")
            inner = node.base
            inner_deriv = recurse(inner)
            derivative = node.exp * inner ** (node.exp - 1) * inner_deriv
            record(
                f"= {sp.sstr(node.exp)}*({sp.sstr(inner)})^{sp.sstr(node.exp - 1)}*({sp.sstr(inner_deriv)})",
                "Chain Rule",
            )
            return derivative

        # Chain Rule for f(g(x))
        if node.is_Function:
            inner = node.args[0] if node.args else var
            record(f"{d(node)} -> Apply Chain Rule", "Chain Rule")
            inner_deriv = recurse(inner)
            outer_deriv = sp.diff(node, inner)
            derivative = outer_deriv * inner_deriv
            record(
                f"= ({sp.sstr(outer_deriv)})*({sp.sstr(inner_deriv)})",
                "Chain Rule",
            )
            return derivative

        # Fallback to SymPy diff
        derivative = sp.diff(node, var)
        record(f"{d(node)} = {sp.sstr(derivative)}", "SymPy diff")
        return derivative

    raw_derivative = recurse(expr)
    simplified = sp.simplify(raw_derivative)
    if not sp.simplify(raw_derivative - simplified) == 0:
        record(f"Simplify: {sp.sstr(simplified)}", "Simplify")

    return simplified, steps, used_rules


# ---------------------- TYPING EFFECT ----------------------
def type_trail_lines(
    textbox,
    lines: List[str],
    delay: int = 400,
    start_fresh: bool = False,
    on_complete=None,
    bold_indices: Optional[Set[int]] = None,
):
    bold_indices = bold_indices or set()
    try:
        textbox.tag_configure("bold", font=(None, 16, "bold"))
    except Exception:
        pass

    if start_fresh:
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.configure(state="disabled")

    def insert_line(i: int):
        if i >= len(lines):
            textbox.configure(state="disabled")
            if on_complete:
                on_complete()
            return
        textbox.configure(state="normal")
        if i in bold_indices:
            textbox.insert("end", lines[i] + "\n", ("bold",))
        else:
            textbox.insert("end", lines[i] + "\n")
        textbox.see("end")
        textbox.configure(state="disabled")
        textbox.after(delay, lambda: insert_line(i + 1))

    insert_line(0)


# ---------------------- COMPUTE BUTTON BACKEND ----------------------
def start_validation():
    compute_btn.configure(state="disabled")
    clear_trail(trail_box)

    final_value.configure(text="Computing...")
    _set_meta(None, None, None)

    user_expr = entry.get()

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()

    valid, msg, parsed_expr = validate_expression(user_expr)

    if not valid:
        trail_box.configure(state="normal")
        trail_box.insert("end", f"[VALIDATION] FAIL: {msg}\n")
        trail_box.configure(state="disabled")
        final_value.configure(text="Error in input")
        _set_meta(time.time() - start_time, timestamp_str, 0)
        compute_btn.configure(state="normal")
        return

    # Detect variable
    free_syms = sorted(list(parsed_expr.free_symbols), key=lambda s: s.name)
    if len(free_syms) == 0:
        var = default_var
    elif len(free_syms) == 1:
        var = free_syms[0]
    else:
        trail_box.configure(state="normal")
        trail_box.insert("end", "Error: Expression must contain only one variable.\n")
        trail_box.configure(state="disabled")
        final_value.configure(text="Error in input")
        _set_meta(time.time() - start_time, timestamp_str, 0)
        compute_btn.configure(state="normal")
        return

    derivative, steps, rules_used = differentiate_with_steps(parsed_expr, var)
    runtime_val = time.time() - start_time

    # Build lines for animated typing
    lines: List[str] = []
    lines.append("GIVEN:")
    lines.append(f"f({var}) = {user_expr}")
    lines.append("")
    lines.append("STEPS:")
    lines.append(f"1. Apply derivative operator: d/d{var}({sp.sstr(parsed_expr)})")
    for idx, step in enumerate(steps, start=2):
        lines.append(f"{idx}. {step.text} [{step.rule}]")
    lines.append("")
    lines.append("FINAL ANSWER:")
    lines.append(f"f'({var}) = {sp.sstr(derivative)}")
    lines.append("")
    lines.append("SUMMARY:")
    if rules_used:
        lines.append("Rules used: " + ", ".join(sorted(rules_used)))

    iterations_val = len(steps) + 1  # include the initial derivative operator line
    lines.append(f"Runtime: {runtime_val:.3f}s")
    lines.append(f"Timestamp: {timestamp_str}")
    lines.append(f"Iterations: {iterations_val}")
    lines.append(f"Library: {LIBRARY_NAME}")

    final_line_index = lines.index(f"f'({var}) = {sp.sstr(derivative)}")

    # Show initial computing message then animate lines
    trail_box.configure(state="normal")
    trail_box.insert("end", "Computing derivative...\n\n")
    trail_box.configure(state="disabled")

    final_answer_text = f"f'({var}) = {sp.sstr(derivative)}"

    def finalize():
        final_value.configure(text=final_answer_text)
        _set_meta(runtime_val, timestamp_str, iterations_val)
        compute_btn.configure(state="normal")

    trail_box.after(
        700,
        lambda: type_trail_lines(
            trail_box,
            lines,
            delay=400,
            start_fresh=False,
            on_complete=finalize,
            bold_indices={final_line_index},
        ),
    )


# ---------------------- LINK BACKEND TO BUTTON ----------------------
compute_btn.configure(command=start_validation)

# ---------------------- RUN APP ----------------------
app.mainloop()
