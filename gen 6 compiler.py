import random
import ctypes
import time
import threading
import tkinter as tk

# Define POINT structure for cursor position tracking
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# Function to get the cursor position accurately
def get_cursor_position():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

# Function to get the active window handle
def get_active_window():
    return ctypes.windll.user32.GetForegroundWindow()

# Function to simulate a mouse click at a given position (only if outside GUI)
def mouse_click(x, y):
    if get_active_window() != gui_window_handle:  # Ensure click is external
        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left button down
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left button up

# Function to type numbers directly into the selected window (only if external)
def type_number(number):
    if get_active_window() != gui_window_handle:  # Prevent typing inside GUI
        for char in str(number):
            vk_code = ctypes.windll.user32.VkKeyScanA(ord(char))
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)  # Key down
            ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)  # Key up

# Variables to store user-selected positions
bar_x, bar_y = None, None
target_x, target_y = None, None
running = False  # Tracks automation status
program_active = False  # Controls whether automation is allowed to run
hover_start = None  # Tracks when the mouse started hovering

# Function to start the automation loop
def generate_number():
    global running
    while running and program_active:
        if bar_x and bar_y and target_x and target_y:  # Ensure positions are set
            mouse_click(target_x, target_y)  # Click input window
            time.sleep(0.5)
            random_number = random.randint(100000, 999999)
            type_number(random_number)  # Type the random number
            number_display.config(text=f"Last Generated: {random_number}")
            time.sleep(0.5)
            mouse_click(bar_x, bar_y)  # Click button after typing number
            time.sleep(4)  # Wait before generating new number

# Function to toggle automation state
def toggle_running():
    global running
    if program_active:
        running = not running
        if running:
            threading.Thread(target=generate_number, daemon=True).start()  # Run automation in background
        status_display.config(text="Running..." if running else "Paused")

# Function to toggle program activation
def toggle_program():
    global program_active
    program_active = not program_active
    status_display.config(text="Program Active" if program_active else "Program Off")
    if not program_active:
        global running
        running = False  # Ensure automation stops

# Function to auto-detect button position via hover tracking
def track_hover_bar(event):
    global bar_x, bar_y, hover_start
    if program_active and hover_start is None:
        hover_start = time.time()

def check_hover_bar():
    global hover_start, bar_x, bar_y
    if hover_start and time.time() - hover_start >= 4:  # 4-second hover detection
        bar_x, bar_y = get_cursor_position()
        bar_confirm.config(bg="lightgreen", text="✔ Button Auto-Selected")
        hover_start = None
        root.after(4000, auto_detect_input_window)  # Wait 4 sec, then detect input

    root.after(500, check_hover_bar)  # Recursively check hover status

# Function to auto-detect input window position
def auto_detect_input_window():
    global target_x, target_y
    if program_active:
        target_x, target_y = get_cursor_position()
        input_confirm.config(bg="lightgreen", text="✔ Input Window Auto-Selected")
        toggle_running()  # Start automation after detection

# GUI for control panel
root = tk.Tk()
root.title("Automated Number Generator")

# Store GUI window handle to prevent self-clicking
gui_window_handle = get_active_window()

status_display = tk.Label(root, text="Turn program ON to auto-detect positions", font=("Arial", 14))
status_display.pack(pady=10)

number_display = tk.Label(root, text="No number generated yet", font=("Arial", 12))
number_display.pack(pady=10)

bar_confirm = tk.Label(root, text="❌ Button Not Detected", font=("Arial", 12), bg="red", fg="white")
bar_confirm.pack(pady=5)

input_confirm = tk.Label(root, text="❌ Input Window Not Detected", font=("Arial", 12), bg="red", fg="white")
input_confirm.pack(pady=5)

program_toggle = tk.Button(root, text="Turn On/Off", command=toggle_program, font=("Arial", 14))
program_toggle.pack(pady=5)

pause_button = tk.Button(root, text="Pause/Resume", command=toggle_running, font=("Arial", 14))
pause_button.pack(pady=5)

# Track hover over the button selection area
root.bind("<Motion>", track_hover_bar)
root.after(500, check_hover_bar)  # Start hover-check loop

# Run the GUI
root.mainloop()