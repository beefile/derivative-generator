import os
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass, field
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
from ui_design import (
    app,
    compute_btn,
    entry,
    export_btn,
    final_value,
    method_var,
    trail_box,
    trail_meta,
)

# ---------------------- PARSER SETUP ----------------------
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

METHOD_LABELS = {
    "rule_based": "Rule-Based",
    "direct_sympy": "Direct SymPy",
}
METHOD_KEYS_BY_LABEL = {label: key for key, label in METHOD_LABELS.items()}
DEFAULT_METHOD_KEY = "rule_based"

last_result: Optional["DerivativeResult"] = None

# ---------------------- EXPORT FUNCTIONALITY ----------------------
def export_report():
    if not last_result or not last_result.success:
        messagebox.showinfo("Export", "No successful computation to export.")
        return
    
    content = []
    content.append("=" * 60)
    content.append("SYMBOLIC DERIVATIVE REPORT")
    content.append("=" * 60)
    content.append(f"Timestamp: {last_result.timestamp}")
    content.append(f"Method: {last_result.method_label}")
    content.append(f"Runtime: {last_result.runtime_s:.3f}s")
    content.append("=" * 60)
    content.append("")
    
    content.extend(last_result.lines)
    
    content.append("")
    content.append("=" * 60)
    content.append("End of Report")
    content.append("=" * 60)
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Export Solution Trail"
    )
    
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))
            messagebox.showinfo("Export Successful", f"Report successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to write file:\n{e}")

NUMERIC_SAMPLE_POINTS = (-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0)
NUMERIC_SAMPLE_LIMIT = 3
NUMERIC_BACKCHECK_STEP = 1e-5
NUMERIC_BACKCHECK_TOLERANCE = 1e-4


# ---------------------- DATA STRUCTURES ----------------------
@dataclass
class Step:
    text: str
    rule: str


@dataclass
class VerificationSample:
    x_value: float
    computed_value: float
    finite_difference_value: float
    residual: float
    tolerance: float
    passed: bool


@dataclass
class VerificationResult:
    reference_derivative: Optional[sp.Expr] = None
    difference_expr: Optional[sp.Expr] = None
    symbolic_passed: bool = False
    numeric_samples: List[VerificationSample] = field(default_factory=list)
    numeric_check_ran: bool = False
    numeric_passed: bool = False
    overall_passed: bool = False
    status_text: str = "NOT RUN"


@dataclass
class DerivativeResult:
    success: bool
    message: str
    method_key: str
    method_label: str
    runtime_s: float
    timestamp: str
    iterations: int
    lines: List[str] = field(default_factory=list)
    final_answer_text: str = ""
    derivative: Optional[sp.Expr] = None
    parsed_expr: Optional[sp.Expr] = None
    variable: Optional[sp.Symbol] = None
    is_constant: bool = False
    rules_used: Set[str] = field(default_factory=set)
    verification: VerificationResult = field(default_factory=VerificationResult)


# ---------------------- INPUT HANDLING ----------------------
def format_expression(expr_obj: sp.Expr) -> str:
    text = sp.sstr(expr_obj)
    text = text.replace("**", "^")
    return re.sub(r"\^1(\b)", r"\1", text)


def normalize_input(expr: str) -> str:
    replacements = {
        "^": "**",
        "Ãƒâ€”": "*",
        "Ã‚Â·": "*",
        "ÃƒÂ·": "/",
        "Ã¢Ë†â€™": "-",
        "Ã¢â‚¬â€œ": "-",
        "Ã¢â‚¬â€": "-",
    }
    for old, new in replacements.items():
        expr = expr.replace(old, new)
    return expr.strip()


def validate_input(expr: str) -> Tuple[bool, str, Optional[sp.Expr]]:
    expr = expr.strip()
    if not expr:
        return False, "Expression cannot be empty", None

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

    invalid_symbols = sorted(
        symbol.name for symbol in parsed.free_symbols if not re.fullmatch(r"[A-Za-z]+", symbol.name)
    )
    if invalid_symbols:
        return False, "Only letter-based variables are allowed (example: x)", None

    return True, "Validation passed", parsed


# ---------------------- META SUMMARY ----------------------
def _set_meta(runtime_s=None, timestamp=None, iterations=None):
    runtime_text = f"{runtime_s:.3f}s" if runtime_s is not None else "--"
    timestamp_text = timestamp if timestamp else "--"
    iterations_text = str(iterations) if iterations is not None else "--"

    trail_meta.configure(
        text=f"Runtime: {runtime_text} | Timestamp: {timestamp_text} | Iterations: {iterations_text} | Library: {LIBRARY_NAME}"
    )


# ---------------------- DIFFERENTIATION LOGIC ----------------------
def differentiate_with_steps(expr: sp.Expr, var: sp.Symbol) -> Tuple[sp.Expr, List[Step], Set[str]]:
    steps: List[Step] = []
    used_rules: Set[str] = set()

    def d(expr_inner: sp.Expr) -> str:
        return f"d/d{var}({format_expression(expr_inner)})"

    def record(text: str, rule: str):
        steps.append(Step(text=text.replace("**", "^"), rule=rule))
        used_rules.add(rule)

    def recurse(node: sp.Expr) -> sp.Expr:
        if node.is_number:
            record(f"{d(node)} = 0 (Derivative of a constant is always 0)", "Constant Rule")
            return sp.Integer(0)

        if node == var:
            record(f"{d(node)} = 1", "Variable Rule")
            return sp.Integer(1)

        if node.is_Add:
            ordered_args = node.as_ordered_terms()
            pieces = [d(arg) for arg in ordered_args]
            record(f"{d(node)} = " + " + ".join(pieces), "Sum and Difference Rule")
            derivatives = [recurse(arg) for arg in ordered_args]
            combined = sp.Add(*derivatives)
            record(f"= {format_expression(combined)}", "Sum and Difference Rule")
            return combined

        coeff, factors = node.as_coeff_mul()
        inner = sp.Mul(*factors)
        if coeff != 1 and inner.has(var):
            record(
                f"{d(node)} = {format_expression(coeff)} * {d(inner)}",
                "Constant Multiple Rule",
            )
            inner_deriv = recurse(inner)
            derivative = coeff * inner_deriv
            record(f"= {format_expression(derivative)}", "Constant Multiple Rule")
            return derivative

        num, den = node.as_numer_denom()
        if den != 1 and (num.has(var) or den.has(var)):
            record(f"{d(node)} -> Apply Quotient Rule", "Quotient Rule")
            dnum = recurse(num)
            dden = recurse(den)
            derivative = (dnum * den - num * dden) / (den**2)
            record(
                f"= (({format_expression(dnum)})*({format_expression(den)}) - ({format_expression(num)})*({format_expression(dden)})) / ({format_expression(den)}^2)",
                "Quotient Rule",
            )
            return derivative

        if node.is_Mul:
            factors = list(node.args)
            if len(factors) >= 2:
                record(f"{d(node)} -> Apply Generalized Product Rule", "Product Rule")
                derivatives_cache = [recurse(factor) for factor in factors]

                terms = []
                derivative = sp.Integer(0)
                for index in range(len(factors)):
                    df = derivatives_cache[index]
                    others = factors[:index] + factors[index + 1 :]
                    parts = [format_expression(df)] + [format_expression(item) for item in others]
                    terms.append("(" + ")*(".join(parts) + ")")
                    derivative += df * sp.Mul(*others)

                record("= " + " + ".join(terms), "Product Rule")
                return derivative

        if isinstance(node, sp.Pow) and node.exp == sp.Rational(1, 2):
            record(f"{d(node)} -> Apply Square Root Rule", "Square Root Rule")
            inner = node.base
            inner_deriv = recurse(inner)
            derivative = inner_deriv / (2 * sp.sqrt(inner))
            record(
                f"= ({format_expression(inner_deriv)}) / (2 * sqrt({format_expression(inner)}))",
                "Square Root Rule",
            )
            return derivative

        if node.is_Pow and node.base == var and node.exp.is_number:
            derivative = node.exp * var ** (node.exp - 1)
            exp_minus_1 = node.exp - 1
            exp_str = f"^{format_expression(exp_minus_1)}" if exp_minus_1 != 1 else ""
            record(f"{d(node)} = {format_expression(node.exp)}*{var}{exp_str}", "Power Rule")
            return derivative

        if (
            node.is_Pow
            and (node.base.has(var) or node.exp.has(var))
            and not (node.base == var and node.exp.is_number)
            and not (node.base == sp.E)
        ):
            record(f"{d(node)} -> Apply General Power Rule (assuming base > 0)", "General Power Rule")
            base = node.base
            exponent = node.exp
            dbase = recurse(base)
            dexponent = recurse(exponent)
            derivative = node * (dexponent * sp.log(base) + exponent * dbase / base)
            record(
                f"= {format_expression(node)} * ({format_expression(dexponent)}*ln({format_expression(base)}) + ({format_expression(exponent)}*{format_expression(dbase)})/{format_expression(base)})",
                "General Power Rule",
            )
            return derivative

        if node.is_Pow and node.exp.is_number and node.base.has(var):
            record(f"{d(node)} -> Apply Chain Rule", "Chain Rule")
            inner = node.base
            inner_deriv = recurse(inner)
            derivative = node.exp * inner ** (node.exp - 1) * inner_deriv
            record(
                f"= {format_expression(node.exp)}*({format_expression(inner)})^{format_expression(node.exp - 1)}*({format_expression(inner_deriv)})",
                "Chain Rule",
            )
            return derivative

        if isinstance(node, sp.sin):
            record(f"{d(node)} -> Apply Sine Rule", "Sine Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = sp.cos(inner) * inner_deriv
            record(f"= cos({format_expression(inner)}) * ({format_expression(inner_deriv)})", "Sine Rule")
            return derivative

        if isinstance(node, sp.cos):
            record(f"{d(node)} -> Apply Cosine Rule", "Cosine Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = -sp.sin(inner) * inner_deriv
            record(f"= -sin({format_expression(inner)}) * ({format_expression(inner_deriv)})", "Cosine Rule")
            return derivative

        if isinstance(node, sp.tan):
            record(f"{d(node)} -> Apply Tangent Rule", "Tangent Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = sp.sec(inner) ** 2 * inner_deriv
            record(f"= sec({format_expression(inner)})^2 * ({format_expression(inner_deriv)})", "Tangent Rule")
            return derivative

        if isinstance(node, sp.exp) or (node.is_Pow and node.base == sp.E):
            record(f"{d(node)} -> Apply Exponential Rule", "Exponential Rule")
            inner = node.args[0] if isinstance(node, sp.exp) else node.exp
            inner_deriv = recurse(inner)
            derivative = node * inner_deriv
            record(f"= {format_expression(node)} * ({format_expression(inner_deriv)})", "Exponential Rule")
            return derivative

        if isinstance(node, sp.log):
            record(f"{d(node)} -> Apply Logarithm Rule", "Logarithm Rule")
            inner = node.args[0]
            inner_deriv = recurse(inner)
            derivative = inner_deriv / inner
            record(
                f"= ({format_expression(inner_deriv)}) / ({format_expression(inner)})",
                "Logarithm Rule",
            )
            return derivative

        derivative = sp.diff(node, var)
        record(f"{d(node)} = {format_expression(derivative)}", "Advanced Rule (SymPy Fallback)")
        return derivative

    raw_derivative = recurse(expr)
    simplified = sp.simplify(raw_derivative)
    if sp.simplify(raw_derivative - simplified) != 0:
        record(f"Simplify: {format_expression(simplified)}", "Simplify")

    return simplified, steps, used_rules


def differentiate_direct_sympy(expr: sp.Expr, var: sp.Symbol) -> Tuple[sp.Expr, List[Step], Set[str]]:
    derivative = sp.simplify(sp.diff(expr, var))
    steps = [
        Step("Use SymPy's direct differentiator on the parsed expression", "Direct SymPy"),
        Step(f"d/d{var}({format_expression(expr)}) = {format_expression(derivative)}", "Direct SymPy"),
    ]
    return derivative, steps, {"Direct SymPy"}


# ---------------------- VERIFICATION ----------------------
def _safe_real_eval(expr: sp.Expr, var: sp.Symbol, value: float) -> Optional[float]:
    try:
        evaluated = sp.N(expr.subs(var, value), 16)
    except Exception:
        return None

    if getattr(evaluated, "has", lambda *_: False)(sp.zoo, sp.oo, -sp.oo, sp.nan):
        return None

    try:
        real_part, imag_part = evaluated.as_real_imag()
        real_float = float(real_part)
        imag_float = float(imag_part)
    except (TypeError, ValueError):
        return None

    if not (real_float == real_float and imag_float == imag_float):
        return None

    if abs(imag_float) > 1e-8:
        return None

    if abs(real_float) == float("inf"):
        return None

    return real_float


def build_verification_report(
    parsed_expr: sp.Expr,
    derivative: sp.Expr,
    var: sp.Symbol,
) -> VerificationResult:
    reference_derivative = sp.simplify(sp.diff(parsed_expr, var))
    difference_expr = sp.simplify(derivative - reference_derivative)
    symbolic_passed = difference_expr == 0

    numeric_samples: List[VerificationSample] = []

    for x_value in NUMERIC_SAMPLE_POINTS:
        computed_value = _safe_real_eval(derivative, var, x_value)
        f_plus = _safe_real_eval(parsed_expr, var, x_value + NUMERIC_BACKCHECK_STEP)
        f_minus = _safe_real_eval(parsed_expr, var, x_value - NUMERIC_BACKCHECK_STEP)

        if computed_value is None or f_plus is None or f_minus is None:
            continue

        finite_difference_value = (f_plus - f_minus) / (2 * NUMERIC_BACKCHECK_STEP)
        residual = abs(computed_value - finite_difference_value)
        tolerance = max(
            NUMERIC_BACKCHECK_TOLERANCE,
            NUMERIC_BACKCHECK_TOLERANCE * max(abs(computed_value), abs(finite_difference_value), 1.0),
        )
        numeric_samples.append(
            VerificationSample(
                x_value=x_value,
                computed_value=computed_value,
                finite_difference_value=finite_difference_value,
                residual=residual,
                tolerance=tolerance,
                passed=residual <= tolerance,
            )
        )

        if len(numeric_samples) >= NUMERIC_SAMPLE_LIMIT:
            break

    numeric_check_ran = bool(numeric_samples)
    numeric_passed = numeric_check_ran and all(sample.passed for sample in numeric_samples)
    overall_passed = symbolic_passed and (numeric_passed if numeric_check_ran else True)

    if overall_passed:
        status_text = "PASSED"
    elif symbolic_passed and not numeric_check_ran:
        status_text = "PASSED (symbolic only)"
    else:
        status_text = "FAILED"

    return VerificationResult(
        reference_derivative=reference_derivative,
        difference_expr=difference_expr,
        symbolic_passed=symbolic_passed,
        numeric_samples=numeric_samples,
        numeric_check_ran=numeric_check_ran,
        numeric_passed=numeric_passed,
        overall_passed=overall_passed,
        status_text=status_text,
    )


def _build_success_lines(
    user_expr: str,
    parsed_expr: sp.Expr,
    var: sp.Symbol,
    derivative: sp.Expr,
    steps: List[Step],
    rules_used: Set[str],
    method_label: str,
    is_constant: bool,
    runtime_s: float,
    timestamp_str: str,
    verification: VerificationResult,
) -> Tuple[List[str], int]:
    var_str = str(var)

    lines: List[str] = []
    lines.append("GIVEN:")
    if is_constant:
        lines.append(f"f({var_str}) = {user_expr} (constant function)")
    else:
        lines.append(f"f({var_str}) = {user_expr}")
    lines.append("")
    lines.append("METHOD:")
    lines.append(method_label)
    lines.append("")
    lines.append("STEPS:")
    lines.append(f"1. Apply derivative operator: d/d{var_str}({format_expression(parsed_expr)})")
    for idx, step in enumerate(steps, start=2):
        lines.append(f"{idx}. {step.text} [{step.rule}]")
    lines.append("")
    lines.append("FINAL ANSWER:")
    lines.append(f"f'({var_str}) = {format_expression(derivative)}")
    lines.append("")
    lines.append("COMPLETION:")
    if is_constant:
        lines.append("Stopped early: derivative of a constant is 0")
    else:
        lines.append(f"Process completed using the {method_label} method")
    lines.append("")
    lines.append("VERIFICATION:")
    lines.append(
        f"1. SymPy reference derivative: d/d{var_str}({format_expression(parsed_expr)}) = {format_expression(verification.reference_derivative)}"
    )
    lines.append(
        f"2. Symbolic difference: ({format_expression(derivative)}) - ({format_expression(verification.reference_derivative)}) = {format_expression(verification.difference_expr)}"
    )
    lines.append(f"3. Symbolic equivalence check: {'PASSED' if verification.symbolic_passed else 'FAILED'}")
    lines.append("4. Numeric back-check (central difference):")
    if verification.numeric_samples:
        for sample in verification.numeric_samples:
            lines.append(
                "   "
                + f"x = {sample.x_value:.4f} | computed = {sample.computed_value:.6f} | approx = {sample.finite_difference_value:.6f} | residual = {sample.residual:.2e} | {'PASSED' if sample.passed else 'FAILED'}"
            )
        lines.append(f"   Numeric back-check summary: {'PASSED' if verification.numeric_passed else 'FAILED'}")
    else:
        lines.append("   Numeric back-check skipped: no safe real sample points were found.")
    lines.append(f"5. Overall verification: {verification.status_text}")
    lines.append("")
    lines.append("SUMMARY:")
    lines.append(f"Method used: {method_label}")
    if rules_used:
        lines.append("Rules used: " + ", ".join(sorted(rules_used)))
    lines.append(f"Verification: {verification.status_text}")
    iterations = len(steps) + 1
    lines.append(f"Runtime: {runtime_s:.3f}s")
    lines.append(f"Timestamp: {timestamp_str}")
    lines.append(f"Iterations: {iterations}")
    lines.append(f"Library: {LIBRARY_NAME}")

    return lines, iterations


def _build_error_result(
    message: str,
    method_key: str,
    runtime_s: float,
    timestamp_str: str,
) -> DerivativeResult:
    method_label = METHOD_LABELS[method_key]
    return DerivativeResult(
        success=False,
        message=message,
        method_key=method_key,
        method_label=method_label,
        runtime_s=runtime_s,
        timestamp=timestamp_str,
        iterations=0,
        lines=[
            "METHOD:",
            method_label,
            "",
            "COMPLETION:",
            f"Stopped: {message}",
            "",
            "VERIFICATION:",
            "Not executed because derivative computation did not complete.",
            "Overall verification: NOT AVAILABLE",
        ],
        final_answer_text="Error in input",
        verification=VerificationResult(status_text="NOT AVAILABLE"),
    )


def compute_derivative_report(
    user_expr: str,
    method_key: str = DEFAULT_METHOD_KEY,
    now: Optional[datetime] = None,
) -> DerivativeResult:
    method_key = method_key if method_key in METHOD_LABELS else DEFAULT_METHOD_KEY
    timestamp_dt = now or datetime.now()
    timestamp_str = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()

    success, message, parsed_expr = validate_input(user_expr)
    if not success:
        return _build_error_result(message, method_key, time.time() - start_time, timestamp_str)

    free_symbols = parsed_expr.free_symbols
    if len(free_symbols) > 1:
        return _build_error_result(
            "Expression must contain only one variable",
            method_key,
            time.time() - start_time,
            timestamp_str,
        )

    if len(free_symbols) == 0:
        var = sp.Symbol("x")
        is_constant = True
    else:
        var = sorted(list(free_symbols), key=lambda symbol: symbol.name)[0]
        is_constant = False

    if method_key == "direct_sympy":
        derivative, steps, rules_used = differentiate_direct_sympy(parsed_expr, var)
    else:
        derivative, steps, rules_used = differentiate_with_steps(parsed_expr, var)

    verification = build_verification_report(parsed_expr, derivative, var)
    runtime_s = time.time() - start_time
    method_label = METHOD_LABELS[method_key]
    lines, iterations = _build_success_lines(
        user_expr=user_expr,
        parsed_expr=parsed_expr,
        var=var,
        derivative=derivative,
        steps=steps,
        rules_used=rules_used,
        method_label=method_label,
        is_constant=is_constant,
        runtime_s=runtime_s,
        timestamp_str=timestamp_str,
        verification=verification,
    )

    return DerivativeResult(
        success=True,
        message="Derivative computed successfully",
        method_key=method_key,
        method_label=method_label,
        runtime_s=runtime_s,
        timestamp=timestamp_str,
        iterations=iterations,
        lines=lines,
        final_answer_text=f"f'({var}) = {format_expression(derivative)}",
        derivative=derivative,
        parsed_expr=parsed_expr,
        variable=var,
        is_constant=is_constant,
        rules_used=rules_used,
        verification=verification,
    )


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

    def insert_line(index: int):
        if index >= len(lines):
            textbox.configure(state="disabled")
            if on_complete:
                on_complete()
            return

        textbox.configure(state="normal")
        if index in bold_indices:
            textbox.insert("end", lines[index] + "\n", ("bold",))
        else:
            textbox.insert("end", lines[index] + "\n")
        textbox.see("end")
        textbox.configure(state="disabled")
        textbox.after(delay, lambda: insert_line(index + 1))

    insert_line(0)


# ---------------------- COMPUTE BUTTON BACKEND ----------------------
def start_validation():
    global last_result
    compute_btn.configure(state="disabled")
    export_btn.configure(state="disabled")
    clear_trail(trail_box)
    final_value.configure(text="Computing...")
    _set_meta(None, None, None)

    method_label = method_var.get()
    method_key = METHOD_KEYS_BY_LABEL.get(method_label, DEFAULT_METHOD_KEY)
    result = compute_derivative_report(entry.get(), method_key)
    
    last_result = result

    if not result.success:
        trail_box.configure(state="normal")
        trail_box.insert("end", "\n".join(result.lines) + "\n")
        trail_box.configure(state="disabled")
        final_value.configure(text=result.final_answer_text)
        _set_meta(result.runtime_s, result.timestamp, result.iterations)
        compute_btn.configure(state="normal")
        return

    final_line_index = result.lines.index(result.final_answer_text)

    trail_box.configure(state="normal")
    trail_box.insert("end", f"Computing derivative with {result.method_label}...\n\n")
    trail_box.configure(state="disabled")

    def finalize():
        final_value.configure(text=result.final_answer_text)
        _set_meta(result.runtime_s, result.timestamp, result.iterations)
        compute_btn.configure(state="normal")
        export_btn.configure(state="normal")

    trail_box.after(
        700,
        lambda: type_trail_lines(
            trail_box,
            result.lines,
            delay=400,
            start_fresh=False,
            on_complete=finalize,
            bold_indices={final_line_index},
        ),
    )


# ---------------------- LINK BACKEND TO BUTTON ----------------------
compute_btn.configure(command=start_validation)
export_btn.configure(command=export_report)


# ---------------------- RUN APP ----------------------
if __name__ == "__main__":
    app.mainloop()
