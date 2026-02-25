import customtkinter as ctk
import time
from datetime import datetime

# color palette
BG = "#FBF6F2"
ACCENT = "#FFD4F8"
TEXT = "#0B1009"

TITLE = "SYMBOLIC: DERIVATIVE GENERATOR (BASIC RULES)"
PLACEHOLDER = "Enter a function, e.g., 2x^2 - 5x - 3"

BORDER_W = 2

# app
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Symbolic: Derivative Generator")
app.geometry("1000x680")
app.configure(fg_color=BG)

# font declarations (make sure poppins is installed)
font_title = ctk.CTkFont(family="Poppins", size=20, weight="bold")
font_label = ctk.CTkFont(family="Poppins", size=14, weight="bold")
font_body = ctk.CTkFont(family="Poppins", size=13)
font_btn = ctk.CTkFont(family="Poppins", size=13, weight="bold")
font_symbol = ctk.CTkFont(family="Poppins", size=12, weight="bold")
font_trail = ctk.CTkFont(family="Poppins", size=15)
font_output = ctk.CTkFont(family="Poppins", size=16, weight="bold")
font_meta = ctk.CTkFont(family="Poppins", size=12)  

# main container
root = ctk.CTkFrame(app, fg_color=BG)
root.pack(fill="both", expand=True, padx=30, pady=25)

# header
ctk.CTkLabel(root, text=TITLE, text_color=TEXT, font=font_title).pack(anchor="w")

# input placeholder & compute button row
input_row = ctk.CTkFrame(root, fg_color=BG)
input_row.pack(fill="x", pady=(20, 12))
input_row.grid_columnconfigure(0, weight=1)
input_row.grid_columnconfigure(1, weight=0)

ENTRY_HEIGHT = 46

entry_shell = ctk.CTkFrame(
    input_row,
    fg_color=BG,
    border_color=TEXT,
    border_width=BORDER_W,
    corner_radius=14
)
entry_shell.grid(row=0, column=0, sticky="ew", padx=(0, 12))
entry_shell.grid_columnconfigure(0, weight=1)

entry = ctk.CTkEntry(
    entry_shell,
    placeholder_text=PLACEHOLDER,
    height=ENTRY_HEIGHT,
    fg_color=BG,
    text_color=TEXT,
    border_width=0,
    font=font_body
)
entry.grid(row=0, column=0, sticky="ew", padx=(14, 6), pady=6)

def clear_input():
    entry.delete(0, "end")
    entry.focus_set()

clear_btn = ctk.CTkButton(
    entry_shell,
    text="✕",
    width=36,
    height=ENTRY_HEIGHT - 6,
    fg_color=BG,
    hover_color=BG,
    text_color=TEXT,
    border_width=0,
    font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
    command=clear_input
)
clear_btn.grid(row=0, column=1, padx=(0, 10))

# symbols
symbols_frame = ctk.CTkFrame(root, fg_color=BG)
symbols_frame.pack(fill="x", pady=(10, 20))

symbols = [
    ("x", "x"), ("+", "+"), ("−", "-"), ("×", "*"), ("÷", "/"),
    ("^", "^"), ("(", "("), (")", ")"),
    ("π", "pi"), ("√", "sqrt("), ("ln", "ln("), ("log", "log("),
    ("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("e", "e")
]

for i in range(len(symbols)):
    symbols_frame.grid_columnconfigure(i, weight=1)

def insert_symbol(val: str):
    entry.insert("end", val)
    entry.focus_set()

for i, (lbl, val) in enumerate(symbols):
    btn = ctk.CTkButton(
        symbols_frame,
        text=lbl,
        height=42,
        corner_radius=10,
        fg_color=BG,
        hover_color=BG,
        text_color=TEXT,
        border_color=ACCENT,
        border_width=2,
        font=font_symbol,
        command=lambda v=val: insert_symbol(v)
    )
    btn.grid(row=0, column=i, sticky="ew", padx=4)

# solution trail panel
ctk.CTkLabel(root, text="Solution Trail", text_color=TEXT, font=font_label).pack(anchor="w")

trail_panel = ctk.CTkFrame(
    root,
    fg_color=BG,
    border_color=TEXT,
    border_width=BORDER_W,
    corner_radius=16,
    height=220
)
trail_panel.pack(fill="x", pady=(6, 6))
trail_panel.pack_propagate(False)

trail_box = ctk.CTkTextbox(
    trail_panel,
    fg_color=BG,
    text_color=TEXT,
    border_width=0,
    font=font_trail
)
trail_box.pack(fill="both", expand=True, padx=14, pady=14)
trail_box.configure(state="disabled")

# summary
trail_meta = ctk.CTkLabel(
    root,
    text="Runtime: —   |   Timestamp: —   |   Iterations: —   |   Library: N/A yet",
    text_color=TEXT,
    font=font_meta
)
trail_meta.pack(anchor="w", pady=(0, 16))

# output panel
ctk.CTkLabel(root, text="Final Answer", text_color=TEXT, font=font_label).pack(anchor="w")

answer_panel = ctk.CTkFrame(
    root,
    fg_color=BG,
    border_color=TEXT,
    border_width=BORDER_W,
    corner_radius=16,
    height=90
)
answer_panel.pack(fill="x", pady=(6, 0))
answer_panel.pack_propagate(False)

final_value = ctk.CTkLabel(
    answer_panel,
    text="",
    text_color=TEXT,
    font=font_output
)
final_value.pack(anchor="w", padx=14, pady=18)

# hardcoded sample computation for documentation purposes only
def build_sample_steps(user_expr: str) -> list[str]:
    expr_display = user_expr.strip() if user_expr.strip() else "2x^2 − 5x − 3"

    return [
        "GIVEN:\n"
        f"Problem: Differentiate {expr_display}\n"
        "Inputs: variable = x\n\n",

        "METHOD:\n"
        "Basic differentiation rules (Sum Rule + Power Rule + Constant Rule)\n"
        "Parameters: N/A\n\n",

        "STEPS:\n"
        "1) Apply the sum rule (differentiate term-by-term):\n"
        "   d/dx(2x^2) + d/dx(−5x) + d/dx(−3)\n\n",

        "2) Apply power rule to 2x^2:\n"
        "   d/dx(2x^2) = 2 · d/dx(x^2)\n"
        "   d/dx(x^2) = 2x\n"
        "   ⇒ d/dx(2x^2) = 4x\n\n",

        "3) Differentiate −5x and −3:\n"
        "   d/dx(−5x) = −5 · d/dx(x) = −5 · 1 = −5\n"
        "   d/dx(−3) = 0\n\n",

        "4) Combine results:\n"
        "   4x − 5\n\n",

        "FINAL ANSWER:\n"
        "   4x − 5\n\n",

        "VERIFICATION:\n"
        "Substitution check (term-by-term):\n"
        "   d/dx(2x^2) = 4x ✓\n"
        "   d/dx(−5x) = −5 ✓\n"
        "   d/dx(−3) = 0 ✓\n\n",
    ]

_stream_job_id = None
_stream_start_time = None

def _clear_trail():
    trail_box.configure(state="normal")
    trail_box.delete("1.0", "end")
    trail_box.configure(state="disabled")

def _append_trail(chunk: str):
    trail_box.configure(state="normal")
    trail_box.insert("end", chunk)
    trail_box.see("end")
    trail_box.configure(state="disabled")

def _set_meta(runtime_s: float | None, timestamp: str | None, iterations: int | None):
    rt = f"{runtime_s:.3f}s" if runtime_s is not None else "—"
    ts = timestamp if timestamp is not None else "—"
    it = str(iterations) if iterations is not None else "—"
    trail_meta.configure(
        text=f"Runtime: {rt}   |   Timestamp: {ts}   |   Iterations: {it}   |   Library: N/A yet"
    )

def start_step_stream():
    global _stream_job_id, _stream_start_time

    compute_btn.configure(state="disabled")

    _clear_trail()
    final_value.configure(text="")
    _set_meta(None, None, None)

    user_expr = entry.get().strip()
    steps = build_sample_steps(user_expr)

    _stream_start_time = time.time()
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    delay_ms = 520  # speed per chunk

    def run_next(i: int):
        global _stream_job_id

        if i >= len(steps):
            final_value.configure(text="4x − 5")

            runtime = time.time() - _stream_start_time
            iterations = len(steps) 
            _set_meta(runtime, timestamp_str, iterations)

            compute_btn.configure(state="normal")
            _stream_job_id = None
            return

        _append_trail(steps[i])
        _stream_job_id = app.after(delay_ms, lambda: run_next(i + 1))

    run_next(0)

# compute button for sample streaming
compute_btn = ctk.CTkButton(
    input_row,
    text="Compute",
    width=170,
    height=ENTRY_HEIGHT,
    corner_radius=14,
    fg_color=ACCENT,
    hover_color=ACCENT,
    text_color=TEXT,
    font=font_btn,
    command=start_step_stream
)
compute_btn.grid(row=0, column=1)

app.mainloop()