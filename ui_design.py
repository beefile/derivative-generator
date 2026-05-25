import customtkinter as ctk
from tkinter import font as tkfont

from trail_logger import clear_trail
from about_popup import show_about_popup

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

SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 22

TITLE = "SYMBOLIC: DERIVATIVE GENERATOR (BASIC RULES)"
PLACEHOLDER = "Enter a function, e.g., 2x^2 - 5x - 3"
DEFAULT_META = "Runtime: -- | Timestamp: -- | Iterations: -- | Library: SymPy"
DEFAULT_STATUS = ""
METHOD_OPTIONS = ["Rule-Based", "Direct SymPy"]
DEFAULT_METHOD_LABEL = "Rule-Based"

# ---------------------- APP SETUP ----------------------
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title(TITLE)
app.geometry("1200x760")
app.minsize(760, 520)
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

font_title      = ctk.CTkFont(family=HEADING_FAMILY, size=28, weight="bold")
font_heading    = ctk.CTkFont(family=HEADING_FAMILY, size=20, weight="bold")
font_body       = ctk.CTkFont(family=BODY_FAMILY,    size=15)
font_btn        = ctk.CTkFont(family=BODY_FAMILY,    size=15, weight="bold")
font_symbol     = ctk.CTkFont(family=HEADING_FAMILY, size=13, weight="bold")
font_trail      = ctk.CTkFont(family=BODY_FAMILY,    size=16)
font_output     = ctk.CTkFont(family=HEADING_FAMILY, size=26, weight="bold")
font_meta_label = ctk.CTkFont(family=BODY_FAMILY,    size=13, weight="bold")
font_meta_value = ctk.CTkFont(family=HEADING_FAMILY, size=15, weight="bold")
font_label      = ctk.CTkFont(family=HEADING_FAMILY, size=13)

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
        width=5,
        height=32,
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
            font=ctk.CTkFont(family=BODY_FAMILY, size=14),
            text_color=MUTED
        ).grid(row=1, column=1, sticky="w", pady=(2, 0))

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
    ).grid(row=0, column=0, sticky="w", padx=SPACE_MD, pady=(SPACE_SM, 2))

    value_label = ctk.CTkLabel(
        chip,
        text=value,
        font=font_meta_value,
        text_color=PRIMARY
    )
    value_label.grid(row=1, column=0, sticky="w", padx=SPACE_MD, pady=(0, SPACE_SM))

    return chip, value_label

# ---------------------- BACKEND-EXPECTED HELPERS ----------------------
def insert_symbol(val: str):
    entry.insert("end", val)
    entry.focus_set()

def clear_input():
    entry.delete(0, "end")
    clear_trail(trail_box)
    final_value.configure(text="Derivative computation will appear here")
    set_status_message(DEFAULT_STATUS, MUTED)
    trail_meta.configure(text=DEFAULT_META)
    set_method(DEFAULT_METHOD_LABEL)
    entry.focus_set()
    try:
        export_btn.configure(state="disabled")
    except NameError:
        pass

def apply_meta_to_chips(text: str):
    parts = [p.strip() for p in text.split("|")]
    data = {}

    def _clean(value: str) -> str:
        return (value or "--").strip()

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
root.grid_rowconfigure(0, weight=0)  # header: fixed
root.grid_rowconfigure(1, weight=1)  # scroll area: fills rest

# ---------------------- HEADER ----------------------
header = ctk.CTkFrame(
    root,
    fg_color=SECONDARY,
    corner_radius=0,
    border_width=0,
    height=70
)
header.grid(row=0, column=0, sticky="ew")
header.grid_columnconfigure(0, weight=1)
header.grid_rowconfigure(0, weight=1)
header.grid_propagate(False)  # FIXED: header never resizes

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

info_btn = ctk.CTkButton(
    header_inner,
    text="𝒾",
    width=36,
    height=36,
    corner_radius=18,
    fg_color="transparent",
    hover_color=METHOD_IDLE_HOVER,
    text_color=PRIMARY,
    border_width=2,
    border_color=PRIMARY,
    font=ctk.CTkFont(family=HEADING_FAMILY, size=18, weight="bold", slant="italic"),
    command=lambda: show_about_popup(app, font_title=font_heading, font_body=font_body, heading_family=HEADING_FAMILY)
)
info_btn.grid(row=0, column=2, sticky="e", padx=(0, 10))

# ---------------------- MAIN BODY ----------------------
body_scroll = ctk.CTkScrollableFrame(
    root,
    fg_color="#F0F0F0",
    corner_radius=0,
)
body_scroll.grid(row=1, column=0, sticky="nsew")
body_scroll.grid_columnconfigure(0, weight=1)
body_scroll.grid_rowconfigure(0, weight=0)

body = ctk.CTkFrame(body_scroll, fg_color="#F0F0F0")
body.grid(row=0, column=0, sticky="nsew", padx=SPACE_XL, pady=SPACE_LG)
body.grid_rowconfigure(0, weight=0)
body.grid_rowconfigure(1, weight=0)
body.grid_columnconfigure(0, weight=5)
body.grid_columnconfigure(1, weight=6)

left_col = ctk.CTkFrame(body, fg_color="#F0F0F0")
right_col = ctk.CTkFrame(body, fg_color="#F0F0F0")

left_col.grid(row=0, column=0, sticky="nsew", padx=(0, SPACE_MD))
right_col.grid(row=0, column=1, sticky="nsew", padx=(SPACE_MD, 0))

left_col.grid_columnconfigure(0, weight=1)
# Row weights: Input needs the most space (buttons+entry+methods), Symbols medium, Answer compact
left_col.grid_rowconfigure(0, weight=6, minsize=350)   # Input panel  — tall enough for all controls
left_col.grid_rowconfigure(1, weight=5, minsize=370)   # Symbols panel
left_col.grid_rowconfigure(2, weight=1, minsize=60)    # Answer panel — compact

right_col.grid_columnconfigure(0, weight=1)
right_col.grid_rowconfigure(0, weight=1)

# Let the scroll container measure the full content height naturally.
left_col.grid_propagate(True)
right_col.grid_propagate(True)

# ---------------------- INPUT PANEL ----------------------
input_outer, input_panel = make_shadow_panel(left_col)
input_outer.grid(row=0, column=0, sticky="nsew", pady=(0, SPACE_MD))

input_panel.grid_columnconfigure(0, weight=1)
input_panel.grid_rowconfigure(0, weight=0)  # Header
input_panel.grid_rowconfigure(1, weight=0)  # Entry shell
input_panel.grid_rowconfigure(2, weight=0)  # [unused]
input_panel.grid_rowconfigure(3, weight=0)  # Method label
input_panel.grid_rowconfigure(4, weight=0)  # Method buttons
input_panel.grid_rowconfigure(5, weight=0)  # Action buttons
input_panel.grid_rowconfigure(6, weight=1)  # Spacer so buttons stay top

input_header = make_section_header(input_panel, "Input Function")
input_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_LG, SPACE_SM))

entry_shell = ctk.CTkFrame(
    input_panel,
    fg_color=SOFT_BG,
    corner_radius=RADIUS_MD,
    border_color=SECONDARY,
    border_width=2,
    height=54
)
entry_shell.grid(row=1, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_MD))
entry_shell.grid_columnconfigure(0, weight=1)
entry_shell.grid_rowconfigure(0, weight=1)
entry_shell.grid_propagate(False)  # FIXED: entry shell never grows

entry = ctk.CTkEntry(
    entry_shell,
    placeholder_text=PLACEHOLDER,
    height=44,
    fg_color=SOFT_BG,
    text_color=SECONDARY,
    placeholder_text_color=MUTED,
    border_width=0,
    font=ctk.CTkFont(family=BODY_FAMILY, size=14),
)
entry.grid(row=0, column=0, sticky="ew", padx=(SPACE_MD, SPACE_XS), pady=SPACE_XS)

clear_btn = ctk.CTkButton(
    entry_shell,
    text="✕",
    width=36,
    height=36,
    fg_color=SOFT_BG,
    hover_color=METHOD_IDLE,
    text_color=MUTED,
    border_width=0,
    corner_radius=RADIUS_SM,
    font=font_btn,
    command=clear_input,
)
clear_btn.grid(row=0, column=1, padx=(0, SPACE_SM), pady=SPACE_XS)

def _highlight_entry(_event=None, focus=False):
    entry_shell.configure(border_color=ACCENT if focus else SECONDARY)

entry.bind("<FocusIn>",  lambda e: _highlight_entry(focus=True))
entry.bind("<FocusOut>", lambda e: _highlight_entry(focus=False))

ctk.CTkLabel(
    input_panel,
    text="Method Selection",
    font=ctk.CTkFont(family=BODY_FAMILY, size=14),
    text_color=MUTED,
    anchor="w",
).grid(row=3, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_XS))

method_frame = ctk.CTkFrame(input_panel, fg_color=PRIMARY)
method_frame.grid(row=4, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_MD))
method_frame.grid_columnconfigure(0, weight=1)

method_var = ctk.StringVar(value=DEFAULT_METHOD_LABEL)
method_button_row = ctk.CTkFrame(method_frame, fg_color="transparent")
method_button_row.grid(row=0, column=0, sticky="ew")
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
        height=40,
        corner_radius=RADIUS_MD,
        fg_color=METHOD_IDLE,
        hover_color=METHOD_IDLE_HOVER,
        text_color=SECONDARY,
        border_color=METHOD_IDLE,
        border_width=2,
        font=ctk.CTkFont(family=BODY_FAMILY, size=14, weight="bold"),
        command=lambda value=option: set_method(value),
    )
    button.grid(
        row=0, column=index, sticky="ew",
        padx=(0, SPACE_XS) if index == 0 else (SPACE_XS, 0)
    )
    method_buttons[option] = button

set_method(DEFAULT_METHOD_LABEL)

button_row = ctk.CTkFrame(input_panel, fg_color=PRIMARY)
button_row.grid(row=5, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_LG))
button_row.grid_columnconfigure(0, weight=1)
button_row.grid_columnconfigure(1, weight=0)

compute_btn = ctk.CTkButton(
    button_row,
    text="Compute",
    height=44,
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
    height=44,
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

# ---------------------- SYMBOLS PANEL ----------------------
symbols_outer, symbols_panel = make_shadow_panel(left_col)
symbols_outer.grid(row=1, column=0, sticky="nsew", pady=(0, SPACE_MD))

symbols_panel.grid_columnconfigure(0, weight=1)
symbols_panel.grid_rowconfigure(0, weight=0)
symbols_panel.grid_rowconfigure(1, weight=1)

symbols_header = make_section_header(symbols_panel, "Symbols", "Tap to insert into input")
symbols_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_LG, SPACE_SM))

symbols_body = ctk.CTkFrame(symbols_panel, fg_color=PRIMARY)
symbols_body.grid(row=1, column=0, sticky="nsew", padx=SPACE_LG, pady=(0, SPACE_LG))

symbols = [
    ("x",   "x"),    ("+",    "+"),   ("−",    "-"),   ("×",   "*"),
    ("÷",   "/"),    ("^",    "^"),   ("(",    "("),   (")",   ")"),
    ("π",   "pi"),   ("√",    "sqrt("),("ln", "ln("), ("log", "log("),
    ("sin", "sin("), ("cos",  "cos("), ("tan", "tan("),("e",   "e"),
]

max_cols = 4
for idx in range(max_cols):
    symbols_body.grid_columnconfigure(idx, weight=1)
for idx in range(4):
    symbols_body.grid_rowconfigure(idx, weight=1, uniform="sym")

for i, (lbl, val) in enumerate(symbols):
    r = i // max_cols
    c = i % max_cols
    btn = ctk.CTkButton(
        symbols_body,
        text=lbl,
        width=50,
        height=46,
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

# ---------------------- ANSWER PANEL ----------------------
answer_outer, answer_panel = make_shadow_panel(left_col)
answer_outer.grid(row=2, column=0, sticky="nsew")

answer_panel.grid_columnconfigure(0, weight=1)
answer_panel.grid_rowconfigure(0, weight=0)   # Header
answer_panel.grid_rowconfigure(1, weight=0)   # Status (hidden by default)
answer_panel.grid_rowconfigure(2, weight=1)   # Final value (fills remaining)

answer_header = make_section_header(answer_panel, "Final Answer")
answer_header.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_MD, SPACE_XS))

status_message = ctk.CTkLabel(
    answer_panel,
    text=DEFAULT_STATUS,
    text_color=MUTED,
    font=font_body,
    anchor="w",
    justify="left",
    wraplength=380,
)
# Start hidden; show only when there's actual content
status_message.grid_remove()

def set_status_message(text: str, text_color: str = MUTED):
    status_message.configure(text=text, text_color=text_color)
    if text.strip():
        status_message.grid(row=1, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_XS))
    else:
        status_message.grid_remove()

answer_body = ctk.CTkFrame(answer_panel, fg_color=PRIMARY, corner_radius=0)
answer_body.grid(row=2, column=0, sticky="nsew", padx=SPACE_LG, pady=(0, SPACE_MD))
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
trail_panel.grid_rowconfigure(0, weight=0)  # Header bar
trail_panel.grid_rowconfigure(1, weight=1)  # Trail textbox (stretches)
trail_panel.grid_rowconfigure(2, weight=0)  # Meta chips (fixed)

trail_top_bar = ctk.CTkFrame(trail_panel, fg_color="transparent")
trail_top_bar.grid(row=0, column=0, sticky="ew", padx=SPACE_LG, pady=(SPACE_LG, SPACE_SM))
trail_top_bar.grid_columnconfigure(0, weight=1)

trail_header = make_section_header(trail_top_bar, "Solution Trail", "Scrollable derivation log")
trail_header.grid(row=0, column=0, sticky="w")

export_btn = ctk.CTkButton(
    trail_top_bar,
    text="Export TXT",
    width=100,
    height=36,
    corner_radius=RADIUS_MD,
    fg_color=PRIMARY,
    hover_color=SOFT_BG,
    border_color=SECONDARY,
    border_width=2,
    text_color=SECONDARY,
    font=font_btn,
    command=lambda: None
)
export_btn.grid(row=0, column=1, sticky="e")
export_btn.configure(state="disabled")

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

# ---------------------- META CHIPS (FIXED HEIGHT) ----------------------
meta_strip = ctk.CTkFrame(trail_panel, fg_color=PRIMARY, height=70)
meta_strip.grid(row=2, column=0, sticky="ew", padx=SPACE_LG, pady=(0, SPACE_LG))
meta_strip.grid_propagate(False)  # FIXED: chips row never changes height

for col in range(4):
    meta_strip.grid_columnconfigure(col, weight=1)
meta_strip.grid_rowconfigure(0, weight=1)

runtime_chip,    runtime_val    = make_stat_chip(meta_strip, "Runtime",    "--")
timestamp_chip,  timestamp_val  = make_stat_chip(meta_strip, "Timestamp",  "--")
iterations_chip, iterations_val = make_stat_chip(meta_strip, "Iterations", "--")
library_chip,    library_val    = make_stat_chip(meta_strip, "Library",    "SymPy")

runtime_chip.grid(   row=0, column=0, sticky="nsew", padx=(0,        SPACE_XS))
timestamp_chip.grid( row=0, column=1, sticky="nsew", padx=(SPACE_XS, SPACE_XS))
iterations_chip.grid(row=0, column=2, sticky="nsew", padx=(SPACE_XS, SPACE_XS))
library_chip.grid(   row=0, column=3, sticky="nsew", padx=(SPACE_XS, 0))

trail_meta = ctk.CTkLabel(meta_strip, text=DEFAULT_META, font=font_meta_label, text_color=MUTED)
trail_meta.grid_forget()

_original_meta_configure = trail_meta.configure

def _meta_configure(*args, **kwargs):
    result = _original_meta_configure(*args, **kwargs)
    apply_meta_to_chips(trail_meta.cget("text"))
    return result

trail_meta.configure = _meta_configure  # type: ignore
apply_meta_to_chips(DEFAULT_META)

# ---------------------- RESPONSIVE LAYOUT (RESIZE ONLY) ----------------------
# Layout is fixed structurally — resize only adjusts fonts & wraplength,
# never repositions panels or changes row weights.

def on_resize(event=None):
    if event and event.widget != app:
        return

    width  = app.winfo_width()
    height = app.winfo_height()

    # Switch between wide / narrow column layout
    if width < 940:
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        left_col.grid(row=0, column=0, sticky="nsew", pady=(0, SPACE_MD))
        right_col.grid(row=1, column=0, sticky="nsew")
    else:
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=6)
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, SPACE_MD))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(SPACE_MD, 0))

    # Font scaling (visual only — never triggers layout reflow)
    scale = min(1.0, max(0.6, (height - 100) / 800))
    font_title.configure(     size=int(28 * scale))
    font_heading.configure(   size=int(21 * scale))
    font_body.configure(      size=int(16 * scale))
    font_btn.configure(       size=int(16 * scale))
    font_symbol.configure(    size=int(15 * scale))
    font_output.configure(    size=max(20, int(26 * scale)))
    font_trail.configure(     size=int(17 * scale))
    font_meta_label.configure(size=int(14 * scale))
    font_meta_value.configure(size=int(16 * scale))
    font_label.configure(     size=max(11, int(13 * scale)))

    # Update wraplength for answer text (safe — doesn't affect layout size)
    try:
        w_left = int((width - SPACE_XL * 2) * 0.45)
        new_wrap = max(200, w_left - 60)
        final_value.configure(wraplength=new_wrap)
        status_message.configure(wraplength=new_wrap)
    except Exception:
        pass

app.bind("<Configure>", on_resize)

# ---------------------- INITIAL STATE ----------------------
entry.focus_set()
set_status_message(DEFAULT_STATUS, MUTED)
