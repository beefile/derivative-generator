step_counter = 1


def clear_trail(trail_box):
    global step_counter
    step_counter = 1

    trail_box.configure(state="normal")
    trail_box.delete("1.0", "end")
    trail_box.configure(state="disabled")


def append_line(trail_box, text):
    trail_box.configure(state="normal")
    trail_box.insert("end", text + "\n")
    trail_box.see("end")
    trail_box.configure(state="disabled")


def add_step(trail_box, text):
    global step_counter

    trail_box.configure(state="normal")
    trail_box.insert("end", f"{step_counter}. {text}\n")
    trail_box.see("end")
    trail_box.configure(state="disabled")

    step_counter += 1


def get_step_count():
    return step_counter - 1