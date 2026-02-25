from ui_design import app, entry, trail_box, trail_meta, final_value, compute_btn
import time
from datetime import datetime

# ---------------------- VALIDATION RULES ----------------------
ALLOWED_CHARS = "0123456789x+-*/^() π√lnloge"

def validate_expression(expr: str) -> tuple[bool, str]:
    expr = expr.strip()

    # 1. Required field
    if not expr:
        return False, "Expression cannot be empty"

    # 2. Allowed characters
    if any(c not in ALLOWED_CHARS for c in expr.replace(" ", "")):
        return False, "Invalid character detected"

    # 3. Parentheses match
    if expr.count("(") != expr.count(")"):
        return False, "Unmatched parentheses"

    # 4. Optional unsupported keywords
    unsupported = ["diff", "integral", "sum", "product"]
    if any(word in expr for word in unsupported):
        return False, f"Unsupported keyword detected"

    return True, "Validation passed"

# ---------------------- TRAIL LOGGING ----------------------
def _clear_trail():
    trail_box.configure(state="normal")
    trail_box.delete("1.0", "end")
    trail_box.configure(state="disabled")

def _append_trail(msg: str):
    trail_box.configure(state="normal")
    trail_box.insert("end", msg + "\n")
    trail_box.see("end")
    trail_box.configure(state="disabled")

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
    _clear_trail()
    final_value.configure(text="")
    _set_meta(None, None, None)

    user_expr = entry.get()
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()

    valid, msg = validate_expression(user_expr)
    if not valid:
        _append_trail(f"[VALIDATION] FAIL: {msg}")
        final_value.configure(text="Error in input")
        _set_meta(time.time() - start_time, timestamp_str, 0)
    else:
        _append_trail("[VALIDATION] PASS")
        _append_trail(f"Expression accepted: {user_expr}")
        # Placeholder for derivative computation
        final_value.configure(text="Ready to compute derivative")
        _set_meta(time.time() - start_time, timestamp_str, 1)

    compute_btn.configure(state="normal")

# ---------------------- INVALID INPUT TESTS ----------------------
invalid_tests = [
    "",             # empty input
    "2x^2 + $5x",   # invalid character $
    "2x^2 + (3x",   # unmatched parentheses
]

for test in invalid_tests:
    valid, msg = validate_expression(test)
    print(f"Test Input: '{test}' -> Valid: {valid}, Message: {msg}")

# ---------------------- LINK BACKEND TO BUTTON ----------------------
compute_btn.configure(command=start_validation)

# ---------------------- RUN APP ----------------------
app.mainloop()