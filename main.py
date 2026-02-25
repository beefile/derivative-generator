import customtkinter as ctk

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
app.title("Symbolic Derivative Generator")
app.geometry("1000x650")
app.configure(fg_color=BG)

# font declarations
font_title = ctk.CTkFont(family="Poppins", size=20, weight="bold")
font_label = ctk.CTkFont(family="Poppins", size=14, weight="bold")
font_body = ctk.CTkFont(family="Poppins", size=13)
font_btn = ctk.CTkFont(family="Poppins", size=13, weight="bold")
font_symbol = ctk.CTkFont(family="Poppins", size=12, weight="bold")
font_trail = ctk.CTkFont(family="Poppins", size=15)
font_output = ctk.CTkFont(family="Poppins", size=16, weight="bold")

# main container
root = ctk.CTkFrame(app, fg_color=BG)
root.pack(fill="both", expand=True, padx=30, pady=25)

# header
ctk.CTkLabel(root, text=TITLE, text_color=TEXT, font=font_title).pack(anchor="w")

# input placeholder and button
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

# solution trail placeholder
ctk.CTkLabel(root, text="Solution Trail", text_color=TEXT, font=font_label).pack(anchor="w")

trail_panel = ctk.CTkFrame(
    root,
    fg_color=BG,
    border_color=TEXT,
    border_width=BORDER_W,
    corner_radius=16,
    height=210
)
trail_panel.pack(fill="x", pady=(6, 18))
trail_panel.pack_propagate(False)

trail_box = ctk.CTkTextbox(
    trail_panel,
    fg_color=BG,
    text_color=TEXT,
    border_width=0,
    font=font_trail
)
trail_box.pack(fill="both", expand=True, padx=14, pady=14)
trail_box.configure(state="disabled")  # start empty + locked

# output placeholder
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

# hardcode sample computation for documentation purposes only
SAMPLE_TRAIL = (
    "Let's find the derivative step-by-step.\n"
    "d/dx ( 2x^2 − 5x − 3 )\n\n"
    "Use the power rule.\n"
    "d/dx ( 2x^2 ) + d/dx ( −5x ) + d/dx ( −3 )\n"
    "= 2 * d/dx(x^2) + (−5) * d/dx(x) + 0\n"
    "= 2 * (2x) + (−5) * (1) + 0\n"
    "= 4x − 5\n"
)

def show_sample_computation():
    trail_box.configure(state="normal")
    trail_box.delete("1.0", "end")
    trail_box.insert("end", SAMPLE_TRAIL)
    trail_box.configure(state="disabled")

    final_value.configure(text="4x − 5")

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
    command=show_sample_computation
)
compute_btn.grid(row=0, column=1)

app.mainloop()