import tkinter as tk
import customtkinter as ctk
from typing import Optional


def show_about_popup(parent, *, font_title: Optional[object] = None, font_body: Optional[object] = None, heading_family: Optional[str] = None):
    """Show an about popup as a semi-transparent overlay using a Toplevel.

    Accepts optional font objects (from ui_design) to match the app typography.
    """
    # Ensure parent geometry is up-to-date
    try:
        parent.update_idletasks()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty()
        w = parent.winfo_width()
        h = parent.winfo_height()
    except Exception:
        # Fallback to default placement
        x = y = 0
        w = 800
        h = 600

    # If popup is already open, close it (toggle behaviour)
    if getattr(parent, "_about_popup_open", False):
        try:
            _existing_close = getattr(parent, "_about_popup_close", None)
            if callable(_existing_close):
                _existing_close()
        except Exception:
            pass
        return
    # Create a semi-transparent overlay Toplevel that darkens the app
    overlay = tk.Toplevel(parent)
    overlay.withdraw()
    overlay.overrideredirect(True)
    overlay.geometry(f"{w}x{h}+{x}+{y}")
    # keep overlay subtle so app remains visible
    overlay.attributes("-alpha", 0.25)
    overlay.configure(bg="black")
    overlay.transient(parent)
    overlay.lift()
    overlay.deiconify()
    # make overlay topmost initially so it darkens the app
    try:
        overlay.attributes("-topmost", True)
    except Exception:
        pass

    # Create a separate opaque popup Toplevel above the overlay
    # Use CTkToplevel for consistent styling when available
    try:
        popup_win = ctk.CTkToplevel(parent)
    except Exception:
        popup_win = tk.Toplevel(parent)
    popup_win.withdraw()
    popup_win.overrideredirect(True)
    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    pw = int(screen_w * 0.7)
    ph = int(screen_h * 0.75)
    # center popup over parent
    px = (screen_w - pw) // 2
    py = (screen_h - ph) // 2
    ph = min(ph, screen_h - 80)  # leaves space for taskbar
    pw = min(pw, screen_w - 40)
    popup_win.geometry(f"{pw}x{ph}+{px}+{py}")
    popup_win.configure(bg="")
    popup_win.transient(parent)
    popup_win.deiconify()
    # ensure popup is above overlay: clear overlay topmost and set popup topmost
    try:
        overlay.attributes("-topmost", False)
    except Exception:
        pass
    try:
        popup_win.attributes("-topmost", True)
    except Exception:
        pass
    popup_win.lift()
    popup_win.focus_force()
    # make it modal so user must interact with popup
    try:
        popup_win.grab_set()
    except Exception:
        pass

    

    # Clicking the overlay closes both windows
    def _close_all(event=None):
        try:
            popup_win.grab_release()
        except Exception:
            pass
        try:
            popup_win.destroy()
        except Exception:
            pass
        try:
            overlay.destroy()
        except Exception:
            pass
        # clear stored refs on parent
        try:
            parent._about_popup_open = False
        except Exception:
            pass
        try:
            parent._about_overlay = None
        except Exception:
            pass
        try:
            parent._about_popup_close = None
        except Exception:
            pass

    def _on_overlay_click(event=None):
        _close_all()

    overlay.bind("<Button-1>", _on_overlay_click)
    # mark open and expose close handle for toggling
    try:
        parent._about_popup_open = True
        parent._about_popup_close = _close_all
        parent._about_overlay = overlay
    except Exception:
        pass
    # allow Escape key to close popup
    try:
        popup_win.bind("<Escape>", lambda e: _close_all())
    except Exception:
        pass
    # Center popup frame inside the opaque popup window
    popup = ctk.CTkFrame(
        popup_win,
        fg_color="#FFFFFF",
        corner_radius=14,
        border_width=2,
        border_color="#000000",
        width=pw,
        height=ph
    )
    popup.place(relx=0, rely=0, relwidth=1, relheight=1)
    
    # INNER CONTAINER (THIS WAS MISSING ❗)
    inner = ctk.CTkFrame(
        popup,
        fg_color="#FFFFFF",
        corner_radius=10,
        border_width=0
    )
    inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.97, relheight=0.97)

    inner.grid_rowconfigure(1, weight=1)
    inner.grid_columnconfigure(0, weight=1)

    # build inner layout with header, scrollable content, and footer button
    # ---------------------- HEADER (About + red bar) ----------------------
    header_wrap = ctk.CTkFrame(inner, fg_color="transparent")
    header_wrap.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
    header_wrap.grid_columnconfigure(1, weight=1)

    accent_bar = ctk.CTkFrame(
        header_wrap,
        fg_color="#d3191c",
        width=6,
        height=28,
        corner_radius=4
    )
    accent_bar.grid(row=0, column=0, sticky="nsw", padx=(0, 8))

    ctk.CTkLabel(
        header_wrap,
        text="About",
        font=font_title if font_title else ctk.CTkFont(size=18, weight="bold"),
        text_color="#000000"
    ).grid(row=0, column=1, sticky="w")

    # ---------------------- CONTENT BOX (like your panels) ----------------------
    content_box = ctk.CTkFrame(
        inner,
        fg_color="#F7F7F7",
        corner_radius=20,
        border_width=2,
        border_color="#000000"
    )
    content_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)

    content_box.grid_rowconfigure(1, weight=1)
    content_box.grid_columnconfigure(0, weight=1)

    # ---------------------- TITLE INSIDE BOX ----------------------
    title_frame = ctk.CTkFrame(content_box, fg_color="transparent")
    title_frame.grid(row=0, column=0, pady=(16, 6))

    ctk.CTkLabel(
        title_frame,
        text="∫",
        text_color="#d3191c",
        font=ctk.CTkFont(size=28, weight="bold")
    ).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(
        title_frame,
        text="SYMBOLIC DERIVATIVE GENERATOR\nUSING BASIC DIFFERENTIATION RULES",
        justify="center",
        font=font_title if font_title else ctk.CTkFont(size=14, weight="bold"),
        text_color="#000000"
    ).pack(side="left")

    # ---------------------- SCROLLABLE TEXT ----------------------
    
    textbox = ctk.CTkTextbox(
        content_box,   # ← IMPORTANT: direct parent
        fg_color="transparent",
        border_width=0,
        font=font_body if font_body else ctk.CTkFont(size=13),
        wrap="word"
    )
    textbox.grid(row=1, column=0, sticky="nsew", padx=16, pady=(6, 12))
    
    content_text = """DESCRIPTION:
The Symbolic Derivative Generator is a Python-based desktop application that computes derivatives and displays a complete step-by-step solution trail.

It supports multiple differentiation rules and ensures transparency by showing how results are obtained.

FEATURES:
• Rule-Based differentiation with detailed steps  
• Direct SymPy computation (fast method)  
• Solution Trail visualization  
• Input validation and error handling  
• Verification of results using SymPy  

HOW TO USE:
1. Enter a mathematical expression  
2. Select a method (Rule-Based or Direct SymPy)  
3. Click Compute  
4. View the solution trail and final answer  

DEVELOPERS:
Andino, Vanessa Mae M.  
Llantos, Roselyn G.  
Ochoa, Josephine Lorraine P.  
Palomar, Vhina May F.  

VERSION
Version 1.0 (Midterm)  

COURSE:
COSC 110 – Numerical and Symbolic Computation  

Instructor: Sir Ronald Joy Tengco

This application was developed as a midterm project for COSC 110, showcasing the implementation of symbolic differentiation using Python and SymPy.
    """

    # IMPORTANT: remove indentation in content_text
    clean_text = content_text.strip()

    textbox.insert("end", clean_text)
    textbox.configure(state="disabled")

    # ---------------------- CLOSE BUTTON ----------------------
    close_btn = ctk.CTkButton(
        inner,
        text="Close",
        width=140,
        height=40,
        corner_radius=12,
        fg_color="#d3191c",
        hover_color="#b22d32",
        text_color="#FFFFFF",
        font=font_body if font_body else ctk.CTkFont(size=14, weight="bold"),
        command=_close_all
    )
    close_btn.grid(row=2, column=0, pady=(6, 14))