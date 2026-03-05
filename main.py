from ui_design import app, entry, trail_box, trail_meta, final_value, compute_btn
from trail_logger import clear_trail, append_line, add_step, get_step_count

import time
from datetime import datetime

# ---------------------- VALIDATION RULES ----------------------
ALLOWED_CHARS = "0123456789x+-*/^() π√lnloge"

def validate_expression(expr: str) -> tuple[bool, str]:
    expr = expr.strip()

    if not expr:
        return False, "Expression cannot be empty"

    if any(c not in ALLOWED_CHARS for c in expr.replace(" ", "")):
        return False, "Invalid character detected"

    if expr.count("(") != expr.count(")"):
        return False, "Unmatched parentheses"

    unsupported = ["diff", "integral", "sum", "product"]
    if any(word in expr for word in unsupported):
        return False, "Unsupported keyword detected"

    return True, "Validation passed"

# ---------------------- META SUMMARY ----------------------
def _set_meta(runtime_s=None, timestamp=None, iterations=None):
    rt = f"{runtime_s:.3f}s" if runtime_s else "—"
    ts = timestamp if timestamp else "—"
    it = str(iterations) if iterations else "—"

    trail_meta.configure(
        text=f"Runtime: {rt}   |   Timestamp: {ts}   |   Iterations: {it}   |   Library: N/A yet"
    )

# ---------------------- COMPUTE BUTTON BACKEND ----------------------
def start_validation():

    compute_btn.configure(state="disabled")

    clear_trail(trail_box)

    final_value.configure(text="")
    _set_meta(None, None, None)

    user_expr = entry.get()

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()

    valid, msg = validate_expression(user_expr)

    if not valid:

        append_line(trail_box, f"[VALIDATION] FAIL: {msg}")

        final_value.configure(text="Error in input")

        _set_meta(time.time() - start_time, timestamp_str, 0)

    else:

        append_line(trail_box, "GIVEN")
        append_line(trail_box, f"f(x) = {user_expr}\n")

        append_line(trail_box, "METHOD")
        append_line(trail_box, "Basic differentiation rules\n")

        append_line(trail_box, "STEPS")

        add_step(trail_box, "Parse the input expression")
        add_step(trail_box, "Identify polynomial terms")
        add_step(trail_box, "Prepare rules for differentiation")

        append_line(trail_box, "\nFINAL ANSWER")

        final_value.configure(text="Derivative computation will appear here")

        append_line(trail_box, "\nVERIFICATION")
        append_line(trail_box, "Verification placeholder (Week 9 implementation)")

        append_line(trail_box, "\nSUMMARY")

        _set_meta(time.time() - start_time, timestamp_str, get_step_count())

    compute_btn.configure(state="normal")


# ---------------------- INVALID INPUT TESTS ----------------------
invalid_tests = [
    "",
    "2x^2 + $5x",
    "2x^2 + (3x",
]

for test in invalid_tests:
    valid, msg = validate_expression(test)
    print(f"Test Input: '{test}' -> Valid: {valid}, Message: {msg}")

# ---------------------- LINK BACKEND TO BUTTON ----------------------
compute_btn.configure(command=start_validation)

# ---------------------- RUN APP ----------------------
app.mainloop()