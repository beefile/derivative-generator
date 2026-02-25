import customtkinter as ctk

# ---------------------- COLOR & STYLES ----------------------
BG = "#FBF6F2"
ACCENT = "#FFD4F8"
TEXT = "#0B1009"

TITLE = "SYMBOLIC: DERIVATIVE GENERATOR (BASIC RULES)"
PLACEHOLDER = "Enter a function, e.g., 2x^2 - 5x - 3"
BORDER_W = 2
ENTRY_HEIGHT = 46

# ---------------------- APP SETUP ----------------------
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title(TITLE)
app.geometry("1000x680")
app.configure(fg_color=BG)

# ---------------------- FONTS ----------------------
font_title = ctk.CTkFont(family="Poppins", size=20, weight="bold")
font_label = ctk.CTkFont(family="Poppins", size=14, weight="bold")
font_body = ctk.CTkFont(family="Poppins", size=13)
font_btn = ctk.CTkFont(family="Poppins", size=13, weight="bold")
font_symbol = ctk.CTkFont(family="Poppins", size=12, weight="bold")
font_trail = ctk.CTkFont(family="Poppins", size=15)
font_output = ctk.CTkFont(family="Poppins", size=16, weight="bold")
font_meta = ctk.CTkFont(family="Poppins", size=12)  

# ---------------------- MAIN CONTAINER ----------------------
root = ctk.CTkFrame(app, fg_color=BG)
root.pack(fill="both", expand=True, padx=30, pady=25)

# ---------------------- HEADER ----------------------
ctk.CTkLabel(root, text=TITLE, text_color=TEXT, font=font_title).pack(anchor="w")



# ---------------------- INPUT ROW ----------------------
input_row = ctk.CTkFrame(root, fg_color=BG)
input_row.pack(fill="x", pady=(20, 12))
input_row.grid_columnconfigure(0, weight=1)
input_row.grid_columnconfigure(1, weight=0)

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

# ---------------------- SYMBOLS PANEL ----------------------
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

# ---------------------- SOLUTION TRAIL ----------------------
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

# ---------------------- SUMMARY METADATA ----------------------
trail_meta = ctk.CTkLabel(
    root,
    text="Runtime: —   |   Timestamp: —   |   Iterations: —   |   Library: N/A yet",
    text_color=TEXT,
    font=font_meta
)
trail_meta.pack(anchor="w", pady=(0, 16))

# ---------------------- OUTPUT PANEL ----------------------
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

# ---------------------- COMPUTE BUTTON (placeholder) ----------------------
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
    command=lambda: None  # no backend yet
)
compute_btn.grid(row=0, column=1)

