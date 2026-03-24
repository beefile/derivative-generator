import customtkinter as ctk
from tkinter import font as tkfont

from trail_logger import clear_trail

# ---------------------- DESIGN SYSTEM ----------------------
PRIMARY = "#FFFFFF"
SECONDARY = "#000000"
ACCENT = "#d3191c"
ACCENT_HOVER = "#b22d32"
METHOD_ACTIVE = "#1F2933"
METHOD_ACTIVE_HOVER = "#111827"
METHOD_IDLE = "#E6EAEE"
METHOD_IDLE_HOVER = "#D7DEE5"

MUTED = "#444444"
SOFT_BG = "#F7F7F7"

RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 14

SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 14
SPACE_LG = 18
SPACE_XL = 24

TITLE = "SYMBOLIC: DERIVATIVE GENERATOR (BASIC RULES)"
PLACEHOLDER = "Enter a function, e.g., 2x^2 - 5x - 3"
DEFAULT_META = "Runtime: -- | Timestamp: -- | Iterations: -- | Library: SymPy"
METHOD_OPTIONS = ["Rule-Based", "Direct SymPy"]
DEFAULT_METHOD_LABEL = "Rule-Based"

# ---------------------- APP SETUP ----------------------
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title(TITLE)
app.geometry("1200x760")
app.minsize(860, 640)
app.configure(fg_color=PRIMARY)
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

# ---------------------- FONT RESOLUTION ----------------------
def pick_installed_font(*candidates: str, fallback: str = "Segoe UI") -> str:
    try:
        families = set(tkfont.families(app))
    except Exception:
        families = set()

    for name in candidates:
        if name and name in families:
            return name
    return fallback

HEADING_FAMILY = pick_installed_font("Segoe UI", "Inter", "Arial", fallback="Arial")
BODY_FAMILY = pick_installed_font("Courier New", "Courier", "Consolas", "Cascadia Mono", fallback="Segoe UI")

font_title = ctk.CTkFont(family=HEADING_FAMILY, size=28, weight="bold")
font_heading = ctk.CTkFont(family=HEADING_FAMILY, size=20, weight="bold")
font_body = ctk.CTkFont(family=BODY_FAMILY, size=15)
font_btn = ctk.CTkFont(family=BODY_FAMILY, size=15, weight="bold")
font_symbol = ctk.CTkFont(family=HEADING_FAMILY, size=13, weight="bold")
font_trail = ctk.CTkFont(family=BODY_FAMILY, size=16)
font_output = ctk.CTkFont(family=HEADING_FAMILY, size=14, weight="bold")
font_meta_label = ctk.CTkFont(family=BODY_FAMILY, size=13, weight="bold")
font_meta_value = ctk.CTkFont(family=HEADING_FAMILY, size=15, weight="bold")

# ---------------------- UI HELPERS ----------------------
def make_shadow_panel(parent):
    panel = ctk.CTkFrame(
        parent,
        fg_color=PRIMARY,
        corner_radius=RADIUS_LG,
        border_color=SECONDARY,
        border_width=2
    )
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(0, weight=1)
    return panel, panel

def make_section_header(parent, title: str, subtitle: str | None = None):
    wrap = ctk.CTkFrame(parent, fg_color=PRIMARY, corner_radius=0)
    wrap.grid_columnconfigure(1, weight=1)

    accent_bar = ctk.CTkFrame(
        wrap,
        fg_color=ACCENT,
        width=6,
        height=36,
        corner_radius=RADIUS_SM
    )
    accent_bar.grid(row=0, column=0, rowspan=2 if subtitle else 1, sticky="nsw", padx=(0, SPACE_SM))

    ctk.CTkLabel(
        wrap,
        text=title,
        font=font_heading,
        text_color=SECONDARY
    ).grid(row=0, column=1, sticky="w")

    if subtitle:
        ctk.CTkLabel(
            wrap,
            text=subtitle,
            font=font_body,
            text_color=MUTED
        ).grid(row=1, column=1, sticky="w", pady=(SPACE_XS, 0))

    return wrap

def make_stat_chip(parent, label: str, value: str):
    chip = ctk.CTkFrame(
        parent,
        fg_color=ACCENT_HOVER,
        corner_radius=RADIUS_MD,
        border_color=SECONDARY,
        border_width=1
    )
    chip.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        chip,
        text=label,
        font=font_meta_label,
        text_color=PRIMARY
    ).grid(row=0, column=0, sticky="w", padx=SPACE_MD, pady=(SPACE_SM, 0))

    value_label = ctk.CTkLabel(
        chip,
        text=value,
        font=font_meta_value,
        text_color=SECONDARY
    )
    value_label.grid(row=1, column=0, sticky="w", padx=SPACE_MD, pady=(0, SPACE_MD))

    return chip, value_label

# ---------------------- BACKEND-EXPECTED HELPERS ----------------------
def insert_symbol(val: str):
    entry.insert("end", val)
    entry.focus_set()

def clear_input():
    entry.delete(0, "end")
    clear_trail(trail_box)
    final_value.configure(text="Derivative computation will appear here")
    trail_meta.configure(text=DEFAULT_META)
    set_method(DEFAULT_METHOD_LABEL)
    entry.focus_set()

def apply_meta_to_chips(text: str):
    parts = [p.strip() for p in text.split("|")]
    data = {}

    def _clean(value: str) -> str:
        return (value or "--").replace("â€”", "—").strip()

    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            data[key.strip().lower()] = value.strip()

    runtime_val.configure(text=_clean(data.get("runtime", "--")))
    timestamp_val.configure(text=_clean(data.get("timestamp", "--")))
    iterations_val.configure(text=_clean(data.get("iterations", "--")))
    library_val.configure(text=_clean(data.get("library", "SymPy")))

# ---------------------- ROOT ----------------------
root = ctk.CTkFrame(app, fg_color="#F0F0F0")
root.grid(row=0, column=0, sticky="nsew")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

# ---------------------- HEADER ----------------------
header = ctk.CTkFrame(
    root,
    fg_color=SECONDARY,
    corner_radius=0,
    border_width=0,
    height=110
)
header.grid(row=0, column=0, sticky="ew")
header.grid_columnconfigure(0, weight=1)
header.grid_rowconfigure(0, weight=1)
# Removed grid_propagate(False) or fixed height for flexibility

header_inner = ctk.CTkFrame(header, fg_color=SECONDARY, corner_radius=0)
header_inner.grid(row=0, column=0, sticky="nsew", padx=SPACE_XL)

header_inner.grid_columnconfigure(0, weight=1)
header_inner.grid_columnconfigure(1, weight=0)
header_inner.grid_columnconfigure(2, weight=1)
header_inner.grid_rowconfigure(0, weight=1)

title_frame = ctk.CTkFrame(header_inner, fg_color=SECONDARY, corner_radius=0)
title_frame.grid(row=0, column=1)

ctk.CTkLabel(
    title_frame,
    text="∫",
    font=ctk.CTkFont(family=HEADING_FAMILY, size=36, weight="bold"),
    text_color=ACCENT
).grid(row=0, column=0, padx=(0, SPACE_MD))

ctk.CTkLabel(
    title_frame,
    text=TITLE,
    font=font_title,
    text_color=PRIMARY
).grid(row=0, column=1)

# ---------------------- MAIN BODY ----------------------
body = ctk.CTkFrame(root, fg_color="#F0F0F0")
body.grid(row=1, column=0, sticky="nsew", padx=SPACE_XL, pady=SPACE_LG)
body.grid_rowconfigure(0, weight=1)
body.grid_columnconfigure(0, weight=3)
body.grid_columnconfigure(1, weight=4)
# Prevent internal content from pushing columns left/right
# body.grid_propagate(False) - Removed for responsiveness

left_col = ctk.CTkFrame(body, fg_color="#F0F0F0")
right_col = ctk.CTkFrame(body, fg_color="#F0F0F0")

# Lock horizontal sizes
# left_col.grid_propagate(False)
# right_col.grid_propagate(False) - Removed for responsiveness

left_col.grid(row=0, column=0, sticky="nsew", padx=(0, SPACE_MD))
right_col.grid(row=0, column=1, sticky="nsew", padx=(SPACE_MD, 0))

left_col.grid_columnconfigure(0, weight=1)
left_col.grid_rowconfigure(0, weight=0, minsize=200) # Input
left_col.grid_rowconfigure(1, weight=1, minsize=300) # Symbols
left_col.grid_rowconfigure(2, weight=0, minsize=80)  # Answer

right_col.grid_columnconfigure(0, weight=1)
right_col.grid_rowconfigure(0, weight=1)

# ---------------------- INPUT PANEL ----------------------
input_outer, input_panel = make_shadow_panel(left_col)
input_outer.grid(row=0, column=0, sticky="nsew", pady=(0, SPACE_MD))
# Prevent internal content from resizing the panel during computation
# input_outer.grid_propagate(False) - Removed for true responsiveness
input_panel.grid_columnconfigure(0, weight=1)
input_panel.grid_rowconfigure(0, weight=0)  # Header: Fixed
input_panel.grid_rowconfigure(1, weight=1)  # Input Box: Flexible
input_panel.grid_rowconfigure(2, weight=0)  # Method: Fixed
input_panel.grid_rowconfigure(3, weight=0)  # Buttons: Fixed

input_header = make_section_header(input_panel, "Input Function")
input_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_LG, SPACE_SM))

entry_shell = ctk.CTkFrame(
    input_panel,
    fg_color=SOFT_BG,
    corner_radius=RADIUS_MD,
    border_color=SECONDARY,
    border_width=2,
    height=90
)
entry_shell.grid(row=1, column=0, sticky="nsew", padx=SPACE_LG, pady=(0, SPACE_MD))
entry_shell.grid_columnconfigure(0, weight=1)
entry_shell.grid_rowconfigure(0, weight=1)
# Remove propagation lock from internal shell to prevent clipping
# entry_shell.grid_propagate(False)

entry = ctk.CTkEntry(
    entry_shell,
    placeholder_text=PLACEHOLDER,
    height=60,
    fg_color=SOFT_BG,
    text_color=SECONDARY,
    placeholder_text_color=MUTED,
    border_width=0,
    font=ctk.CTkFont(family=BODY_FAMILY, size=14),
)
entry.grid(row=0, column=0, sticky="ew", padx=(SPACE_SM, SPACE_SM), pady=SPACE_SM)

clear_btn = ctk.CTkButton(
    entry_shell,
    text="✕",
    width=44,
    height=42,
    fg_color=SOFT_BG,
    hover_color=SOFT_BG,
    text_color=SECONDARY,
    border_width=0,
    corner_radius=RADIUS_MD,
    font=font_btn,
    command=clear_input,
)
clear_btn.grid(row=0, column=1, padx=(0, SPACE_MD), pady=SPACE_SM)

def _highlight_entry(_event=None, focus=False):
    entry_shell.configure(border_color=ACCENT if focus else SECONDARY)

entry.bind("<FocusIn>", lambda e: _highlight_entry(focus=True))
entry.bind("<FocusOut>", lambda e: _highlight_entry(focus=False))

method_frame = ctk.CTkFrame(input_panel, fg_color=PRIMARY)
method_frame.grid(row=2, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_MD))
method_frame.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(
    method_frame,
    text="Method Selection",
    font=font_body,
    text_color=SECONDARY,
).grid(row=0, column=0, sticky="w", pady=(0, SPACE_XS))

method_var = ctk.StringVar(value=DEFAULT_METHOD_LABEL)
method_button_row = ctk.CTkFrame(method_frame, fg_color="transparent")
method_button_row.grid(row=1, column=0, sticky="ew")
method_button_row.grid_columnconfigure(0, weight=1)
method_button_row.grid_columnconfigure(1, weight=1)

method_buttons = {}

def set_method(method_label: str):
    method_var.set(method_label)
    for label, button in method_buttons.items():
        is_selected = label == method_label
        button.configure(
            fg_color=METHOD_ACTIVE if is_selected else METHOD_IDLE,
            hover_color=METHOD_ACTIVE_HOVER if is_selected else METHOD_IDLE_HOVER,
            text_color=PRIMARY if is_selected else SECONDARY,
            border_color=METHOD_ACTIVE if is_selected else METHOD_IDLE,
        )

for index, option in enumerate(METHOD_OPTIONS):
    button = ctk.CTkButton(
        method_button_row,
        text=option,
        height=42,
        corner_radius=RADIUS_MD,
        fg_color=METHOD_IDLE,
        hover_color=METHOD_IDLE_HOVER,
        text_color=SECONDARY,
        border_color=METHOD_IDLE,
        border_width=2,
        font=ctk.CTkFont(family=BODY_FAMILY, size=14, weight="bold"),
        command=lambda value=option: set_method(value),
    )
    button.grid(row=0, column=index, sticky="ew", padx=(0, SPACE_SM) if index == 0 else (SPACE_SM, 0))
    method_buttons[option] = button

set_method(DEFAULT_METHOD_LABEL)

button_row = ctk.CTkFrame(input_panel, fg_color=PRIMARY)
# Added top padding (SPACE_MD) to separate from the input box
button_row.grid(row=3, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_LG))
button_row.grid_columnconfigure(0, weight=1)
button_row.grid_columnconfigure(1, weight=0)

compute_btn = ctk.CTkButton(
    button_row,
    text="Compute",
    height=46,
    corner_radius=RADIUS_MD,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color=PRIMARY,
    font=font_btn,
    command=lambda: None,
)
compute_btn.grid(row=0, column=0, sticky="ew", padx=(0, SPACE_SM))

reset_btn = ctk.CTkButton(
    button_row,
    text="Reset",
    width=110,
    height=46,
    corner_radius=RADIUS_MD,
    fg_color=PRIMARY,
    hover_color=SOFT_BG,
    border_color=SECONDARY,
    border_width=2,
    text_color=SECONDARY,
    font=font_btn,
    command=clear_input,
)
reset_btn.grid(row=0, column=1, sticky="e")

symbols_outer, symbols_panel = make_shadow_panel(left_col)
symbols_outer.grid(row=1, column=0, sticky="nsew", pady=(0, SPACE_MD))
# Prevent internal content from resizing the panel
# symbols_outer.grid_propagate(False) - Removed for true responsiveness
symbols_panel.grid_columnconfigure(0, weight=1)
symbols_panel.grid_rowconfigure(0, weight=0)
symbols_panel.grid_rowconfigure(1, weight=1)

symbols_header = make_section_header(symbols_panel, "Symbols", "Tap to insert into input")
symbols_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_LG, SPACE_SM))

symbols_body = ctk.CTkFrame(symbols_panel, fg_color=PRIMARY)
symbols_body.grid(row=1, column=0, sticky="nsew", padx=SPACE_LG, pady=(0, 16))

symbols = [
    ("x", "x"), ("+", "+"), ("−", "-"), ("×", "*"),
    ("÷", "/"), ("^", "^"), ("(", "("), (")", ")"),
    ("π", "pi"), ("√", "sqrt("), ("ln", "ln("), ("log", "log("),
    ("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("e", "e"),
]

max_cols = 4
for idx in range(max_cols):
    symbols_body.grid_columnconfigure(idx, weight=1)
for idx in range(4): # 4 rows
    symbols_body.grid_rowconfigure(idx, weight=1, uniform="sym")

for i, (lbl, val) in enumerate(symbols):
    r = i // max_cols
    c = i % max_cols
    btn = ctk.CTkButton(
        symbols_body,
        text=lbl,
        width=50,
        height=50,
        corner_radius=RADIUS_MD,
        fg_color=PRIMARY,
        hover_color=ACCENT,
        text_color=SECONDARY,
        border_color=SECONDARY,
        border_width=2,
        font=font_symbol,
        command=lambda v=val: insert_symbol(v),
    )
    btn.grid(row=r, column=c, sticky="ew", padx=SPACE_XS, pady=SPACE_XS)

answer_outer, answer_panel = make_shadow_panel(left_col)
answer_outer.grid(row=2, column=0, sticky="nsew")
# Prevent internal content from resizing the panel
# answer_outer.grid_propagate(False) - Removed for true responsiveness

answer_panel.grid_columnconfigure(0, weight=1)
answer_panel.grid_rowconfigure(0, weight=0)
answer_panel.grid_rowconfigure(1, weight=1)

answer_header = make_section_header(answer_panel, "Final Answer")
answer_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_MD, SPACE_XS))

answer_body = ctk.CTkFrame(answer_panel, fg_color=PRIMARY, corner_radius=0)
answer_body.grid(row=1, column=0, sticky="nsew", padx=SPACE_LG, pady=(0, SPACE_MD))
answer_body.grid_columnconfigure(0, weight=1)
answer_body.grid_rowconfigure(0, weight=1)

final_value = ctk.CTkLabel(
    answer_body,
    text="Derivative computation will appear here",
    text_color=SECONDARY,
    font=font_output,
    anchor="center",
    justify="center",
    wraplength=380
)
final_value.grid(row=0, column=0, sticky="nsew")

# ---------------------- SOLUTION TRAIL PANEL ----------------------
trail_outer, trail_panel = make_shadow_panel(right_col)
trail_outer.grid(row=0, column=0, sticky="nsew")
trail_panel.grid_columnconfigure(0, weight=1)
trail_panel.grid_rowconfigure(0, weight=0)
trail_panel.grid_rowconfigure(1, weight=1)
trail_panel.grid_rowconfigure(2, weight=0)

trail_header = make_section_header(trail_panel, "Solution Trail", "Scrollable derivation log")
trail_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_LG, SPACE_SM))

trail_body = ctk.CTkFrame(
    trail_panel,
    fg_color=SOFT_BG,
    corner_radius=RADIUS_MD,
    border_color=SECONDARY,
    border_width=1
)
trail_body.grid(row=1, column=0, sticky="nsew", padx=SPACE_LG, pady=(0, SPACE_MD))
trail_body.grid_columnconfigure(0, weight=1)
trail_body.grid_rowconfigure(0, weight=1)

trail_box = ctk.CTkTextbox(
    trail_body,
    fg_color=SOFT_BG,
    text_color=SECONDARY,
    border_width=0,
    font=font_trail,
)
trail_box.grid(row=0, column=0, sticky="nsew", padx=SPACE_MD, pady=SPACE_MD)
trail_box.configure(state="disabled")

meta_strip = ctk.CTkFrame(trail_panel, fg_color=PRIMARY)
meta_strip.grid(row=2, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_LG))
# meta_strip.configure(height=100) - Removed fixed height to prevent clipping

for col in range(4):
    meta_strip.grid_columnconfigure(col, weight=1)

runtime_chip, runtime_val = make_stat_chip(meta_strip, "Runtime", "--")
timestamp_chip, timestamp_val = make_stat_chip(meta_strip, "Timestamp", "--")
iterations_chip, iterations_val = make_stat_chip(meta_strip, "Iterations", "--")
library_chip, library_val = make_stat_chip(meta_strip, "Library", "SymPy")

runtime_chip.grid(row=0, column=0, sticky="ew", padx=(0, SPACE_SM))
timestamp_chip.grid(row=0, column=1, sticky="ew", padx=SPACE_SM)
iterations_chip.grid(row=0, column=2, sticky="ew", padx=SPACE_SM)
library_chip.grid(row=0, column=3, sticky="ew", padx=(SPACE_SM, 0))

trail_meta = ctk.CTkLabel(meta_strip, text=DEFAULT_META, font=font_meta_label, text_color=MUTED)
trail_meta.grid_forget()

_original_meta_configure = trail_meta.configure

def _meta_configure(*args, **kwargs):
    result = _original_meta_configure(*args, **kwargs)
    apply_meta_to_chips(trail_meta.cget("text"))
    return result

trail_meta.configure = _meta_configure  # type: ignore
apply_meta_to_chips(DEFAULT_META)

# ---------------------- RESPONSIVE LAYOUT ----------------------
layout_state = {"mode": None}

def apply_layout(mode: str):
    layout_state["mode"] = mode

    left_col.grid_forget()
    right_col.grid_forget()

    if mode == "wide":
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=6)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=0)

        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, SPACE_MD))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(SPACE_MD, 0))
    else:
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        left_col.grid(row=0, column=0, sticky="nsew", pady=(0, SPACE_MD))
        right_col.grid(row=1, column=0, sticky="nsew")

def maintain_answer_wrap(_event=None):
    try:
        width = max(answer_body.winfo_width() - 20, 220)
        final_value.configure(wraplength=width)
    except Exception:
        pass

def on_resize(event=None):
    # CRITICAL: Only trigger when the main window itself is resized
    if event and event.widget != app:
        return

    width = app.winfo_width()
    height = app.winfo_height()
    target = "narrow" if width < 940 else "wide"
    if layout_state["mode"] != target:
        apply_layout(target)
    
    # More aggressive dynamic font scaling
    scale = min(1.0, max(0.6, (height - 100) / 800))
    font_title.configure(size=int(28 * scale))
    font_heading.configure(size=int(21 * scale))
    font_body.configure(size=int(16 * scale))
    font_btn.configure(size=int(16 * scale))
    font_symbol.configure(size=int(15 * scale))
    font_output.configure(size=int(14 * scale))
    font_trail.configure(size=int(17 * scale))
    font_meta_label.configure(size=int(14 * scale))
    font_meta_value.configure(size=int(16 * scale))

    # Dynamic heights and widths to maintain absolute stability
    body_w = width - (SPACE_XL * 2)
    body_h = height - 110 - (SPACE_LG * 2) # 110 is header height
    body.configure(width=body_w, height=body_h)

    if target == "wide":
        w_left = int(body_w * 0.45)
        w_right = body_w - w_left - SPACE_MD
        left_col.configure(width=w_left, height=body_h)
        right_col.configure(width=w_right, height=body_h)
    else:
        left_col.configure(width=body_w, height=int(body_h * 0.5))
        right_col.configure(width=body_w, height=int(body_h * 0.5))

    # Removed manual height configurations for panels
    # Let the grid weights handle growth and content handle min size
    
    # Ensure containers don't shrink/grow when content changes if needed
    # (Leaving grid_propagate(True) by default for responsiveness)
    
    # Dynamic wraplength based on actual panel width
    try:
        new_wrap = int(w_left - 60) if target == "wide" else int(body_w - 60)
        final_value.configure(wraplength=max(200, new_wrap))
    except Exception:
        pass
    
    maintain_answer_wrap()

app.bind("<Configure>", on_resize)
apply_layout("wide")

# ---------------------- INITIAL STATE ----------------------
entry.focus_set()
maintain_answer_wrap()	
