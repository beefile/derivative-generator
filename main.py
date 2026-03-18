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
    "sec": sp.sec,
    "exp": sp.exp,
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


def validate_input(expr: str) -> Tuple[bool, str, Optional[sp.Expr]]:
    expr = expr.strip()
    if not expr:
        return False, "Expression cannot be empty", None
# Validation check simplified; SymPy's parse_expr will handle syntax errors.
    normalized = normalize_input(expr)
    try:
        parsed = parse_expr(
            normalized,
            transformations=TRANSFORMATIONS,
            local_dict=LOCAL_DICT,
            evaluate=True,
        )
    except (SyntaxError, ValueError, TypeError):
        return False, "Unable to parse expression: invalid syntax", None
    except Exception:
        return False, "Unable to parse expression: invalid syntax", None

    return True, "Validation passed", parsed


# ---------------------- META SUMMARY ----------------------
def _set_meta(runtime_s=None, timestamp=None, iterations=None):
    rt = f"{runtime_s:.3f}s" if runtime_s is not None else "--"
    ts = timestamp if timestamp else "--"
    it = str(iterations) if iterations is not None else "--"

    trail_meta.configure(
        text=f"Runtime: {rt}   |   Timestamp: {ts}   |   Steps: {it}   |   Library: {LIBRARY_NAME}"
    )


# ---------------------- DIFFERENTIATION LOGIC ----------------------
def differentiate_with_steps(expr: sp.Expr, var: sp.Symbol) -> Tuple[sp.Expr, List[Step], Set[str]]:
    steps: List[Step] = []
    used_rules: Set[str] = set()

    def format_output(expr_obj) -> str:
        s = sp.sstr(expr_obj)
        s = s.replace("**", "^")
        # Simplify x^1 to x
        import re
        s = re.sub(r"\^1(\b)", r"\1", s)
        return s

    def d(expr_inner: sp.Expr) -> str:
        return f"d/d{var}({format_output(expr_inner)})"

    def record(text: str, rule: str):
        # Format any expressions in the text
        # This is a bit tricky, but we can target common patterns
        text = text.replace("**", "^")
        import re
        text = re.sub(r"\^1(\b)", r"\1", text)
        steps.append(Step(text=text, rule=rule))
        used_rules.add(rule)

    def recurse(node: sp.Expr) -> sp.Expr:
        # Constant Rule
        if node.is_number:
            record(f"{d(node)} = 0 (Derivative of a constant is always 0)", "Constant Rule")
            return sp.Integer(0)

        # Variable Rule
        if node == var:
            record(f"{d(node)} = 1", "Variable Rule")
            return sp.Integer(1)

        # Sum and Difference Rule
        if node.is_Add:
            ordered_args = node.as_ordered_terms()
            pieces = [d(arg) for arg in ordered_args]
            record(f"{d(node)} = " + " + ".join(pieces), "Sum and Difference Rule")
            derivatives = [recurse(arg) for arg in ordered_args]
            combined = sp.Add(*derivatives)
            record(f"= {format_output(combined)}", "Sum and Difference Rule")
            return combined

        # Constant Multiple Rule (coeff * f(x))
        coeff, factors = node.as_coeff_mul()
        inner = sp.Mul(*factors)
        if coeff != 1 and inner.has(var):
            record(
                f"{d(node)} = {format_output(coeff)} * {d(inner)}",
                "Constant Multiple Rule",
            )
            inner_deriv = recurse(inner)
            derivative = coeff * inner_deriv
            record(f"= {format_output(derivative)}", "Constant Multiple Rule")
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
                f"= (({format_output(dnum)})*({format_output(den)}) - ({format_output(num)})*({format_output(dden)})) / ({format_output(den)}^2)"
            )
            record(rule_line, "Quotient Rule")
            return derivative

        # Generalized Product Rule
        if node.is_Mul:
            factors = list(node.args)
            if len(factors) >= 2:
                record(
                    f"{d(node)} -> Apply Generalized Product Rule",
                    "Product Rule",
                )
                
                # Cache derivatives to avoid redundant recurse calls/steps
                derivatives_cache = [recurse(f) for f in factors]
                
                terms = []
                for i in range(len(factors)):
                    df = derivatives_cache[i]
                    others = factors[:i] + factors[i+1:]
                    term = [format_output(df)] + [format_output(o) for o in others]
                    terms.append("(" + ")*(".join(term) + ")")
                
                rule_line = "= " + " + ".join(terms)
                record(rule_line, "Product Rule")
                
                # Compute derivative symbolically using cached values
                derivative = 0
                for i in range(len(factors)):
                    df = derivatives_cache[i]
                    others = factors[:i] + factors[i+1:]
                    term_expr = df * sp.Mul(*others)
                    derivative += term_expr
                return derivative

        # Square Root Rule
        if isinstance(node, sp.Pow) and node.exp == sp.Rational(1, 2):
            record(f"{d(node)} -> Apply Square Root Rule", "Square Root Rule")
            inner = node.base
            inner_deriv = recurse(inner)
            derivative = inner_deriv / (2 * sp.sqrt(inner))
            record(
                f"= ({format_output(inner_deriv)}) / (2 * sqrt({format_output(inner)}))",
                "Square Root Rule",
            )
            return derivative

        # Power Rule (x^n)
        if node.is_Pow and node.base == var and node.exp.is_number:
            derivative = node.exp * var ** (node.exp - 1)
            exp_minus_1 = node.exp - 1
            exp_str = f"^{format_output(exp_minus_1)}" if exp_minus_1 != 1 else ""
            record(
                f"{d(node)} = {format_output(node.exp)}*{var}{exp_str}",
                "Power Rule",
            )
            return derivative

        # General Power Rule (a^b) - includes x^x, a^x, etc.
        if node.is_Pow and (node.base.has(var) or node.exp.has(var)) and not (node.base == var and node.exp.is_number) and not (node.base == sp.E):
            record(f"{d(node)} -> Apply General Power Rule (assuming base > 0)", "General Power Rule")
            a = node.base
            b = node.exp
            da = recurse(a)
            db = recurse(b)
            # (a^b)' = a^b * (b' ln a + b a'/a)
            derivative = node * (db * sp.log(a) + b * da / a)
            record(
                f"= {format_output(node)} * ({format_output(db)}*ln({format_output(a)}) + ({format_output(b)}*{format_output(da)})/{format_output(a)})",
                "General Power Rule",
            )
            return derivative

        # Chain Rule for (g(x))^n
        if node.is_Pow and node.exp.is_number and node.base.has(var):
            record(f"{d(node)} -> Apply Chain Rule", "Chain Rule")
            inner = node.base
            inner_deriv = recurse(inner)
            derivative = node.exp * inner ** (node.exp - 1) * inner_deriv
            record(
                f"= {format_output(node.exp)}*({format_output(inner)})^{format_output(node.exp - 1)}*({format_output(inner_deriv)})",
                "Chain Rule",
            )
            return derivative

        # Trig: Sine Rule
        if isinstance(node, sp.sin):
            record(f"{d(node)} -> Apply Sine Rule", "Sine Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = sp.cos(inner) * inner_deriv
            record(f"= cos({format_output(inner)}) * ({format_output(inner_deriv)})", "Sine Rule")
            return derivative

        # Trig: Cosine Rule
        if isinstance(node, sp.cos):
            record(f"{d(node)} -> Apply Cosine Rule", "Cosine Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = -sp.sin(inner) * inner_deriv
            record(f"= -sin({format_output(inner)}) * ({format_output(inner_deriv)})", "Cosine Rule")
            return derivative

        # Trig: Tangent Rule
        if isinstance(node, sp.tan):
            record(f"{d(node)} -> Apply Tangent Rule", "Tangent Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = sp.sec(inner)**2 * inner_deriv
            record(f"= sec({format_output(inner)})^2 * ({format_output(inner_deriv)})", "Tangent Rule")
            return derivative

        # Exponential Rule
        if isinstance(node, sp.exp) or (node.is_Pow and node.base == sp.E):
            record(f"{d(node)} -> Apply Exponential Rule", "Exponential Rule")
            inner = node.args[0] if isinstance(node, sp.exp) else node.exp
            inner_deriv = recurse(inner)
            derivative = node * inner_deriv
            record(f"= {format_output(node)} * ({format_output(inner_deriv)})", "Exponential Rule")
            return derivative

        # Logarithm Rule
        if isinstance(node, sp.log):
            record(f"{d(node)} -> Apply Logarithm Rule", "Logarithm Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = inner_deriv / inner
            record(
                f"= ({format_output(inner_deriv)}) / ({format_output(inner)})",
                "Logarithm Rule",
            )
            return derivative

        # Fallback to SymPy diff
        derivative = sp.diff(node, var)
        record(f"{d(node)} = {format_output(derivative)}", "Advanced Rule (SymPy Fallback)")
        return derivative

    raw_derivative = recurse(expr)
    simplified = sp.simplify(raw_derivative)
    if not sp.simplify(raw_derivative - simplified) == 0:
        record(f"Simplify: {format_output(simplified)}", "Simplify")

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
    start_time = time.time()
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def format_final(expr_obj) -> str:
        s = sp.sstr(expr_obj)
        s = s.replace("**", "^")
        import re
        s = re.sub(r"\^1(\b)", r"\1", s)
        return s

    success, message, parsed_expr = validate_input(user_expr)
    if not success:
        trail_box.configure(state="normal")
        trail_box.insert("end", f"COMPLETION:\nStopped: {message}\n")
        trail_box.configure(state="disabled")
        final_value.configure(text="Error in input")
        _set_meta(time.time() - start_time, timestamp_str, 0)
        compute_btn.configure(state="normal")
        return

    # Detect variable
    free_syms = parsed_expr.free_symbols
    if len(free_syms) == 0:
        var = sp.Symbol("x")  # Symbol for constant functions
        is_constant = True
    else:
        # Sort to ensure consistency
        var = sorted(list(free_syms), key=lambda s: s.name)[0]
        is_constant = False

    if len(free_syms) > 1:
        trail_box.configure(state="normal")
        trail_box.insert("end", "COMPLETION:\nStopped: Expression must contain only one variable\n")
        trail_box.configure(state="disabled")
        final_value.configure(text="Error in input")
        _set_meta(time.time() - start_time, timestamp_str, 0)
        compute_btn.configure(state="normal")
        return

    derivative, steps, rules_used = differentiate_with_steps(parsed_expr, var)
    runtime_val = time.time() - start_time
    var_str = str(var)

    # Build lines for animated typing
    lines: List[str] = []
    lines.append("GIVEN:")
    if is_constant:
        lines.append(f"f({var_str}) = {user_expr} (constant function)")
    else:
        lines.append(f"f({var_str}) = {user_expr}")
    lines.append("")
    lines.append("STEPS:")
    lines.append(f"1. Apply derivative operator: d/d{var_str}({format_final(parsed_expr)})")
    for idx, step in enumerate(steps, start=2):
        lines.append(f"{idx}. {step.text} [{step.rule}]")
    lines.append("")
    lines.append("FINAL ANSWER:")

    lines.append(f"f'({var_str}) = {format_final(derivative)}")
    lines.append("")
    
    lines.append("COMPLETION:")

    if is_constant:
        lines.append("Stopped early: derivative of a constant is 0")
    else:
        lines.append("Process completed: derivative fully computed using differentiation rules")

    lines.append("")
    
    lines.append("VERIFICATION:")
    # Compute derivative using SymPy directly
    sympy_derivative = sp.diff(parsed_expr, var)

    # Compute difference symbolically
    difference_expr = sp.simplify(derivative - sympy_derivative)
    
    # Append safe strings for GUI
    lines.append(f"1. SymPy derivative: d/d{var_str}({format_final(parsed_expr)}) = {format_final(sympy_derivative)}")
    lines.append(f"2. Difference: ({format_final(derivative)}) - ({format_final(sympy_derivative)}) = {format_final(difference_expr)}")

    # Symbolic verification result
    if difference_expr == 0:
        lines.append("True")
    else:
        lines.append("False")
    lines.append("")  

    lines.append("SUMMARY:")
    if rules_used:
        lines.append("Rules used: " + ", ".join(sorted(rules_used)))

    iterations_val = len(steps) + 1  # include the initial derivative operator line
    lines.append(f"Runtime: {runtime_val:.3f}s")
    lines.append(f"Timestamp: {timestamp_str}")
    lines.append(f"Steps: {iterations_val}")
    lines.append(f"Library: {LIBRARY_NAME}")

    final_line_index = lines.index(f"f'({var_str}) = {format_final(derivative)}")

    # Show initial computing message then animate lines
    trail_box.configure(state="normal")
    trail_box.insert("end", "Computing derivative...\n\n")
    trail_box.configure(state="disabled")

    final_answer_text = f"f'({var_str}) = {format_final(derivative)}"

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
