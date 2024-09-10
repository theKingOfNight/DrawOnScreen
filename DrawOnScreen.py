import tkinter as tk
from tkinter import simpledialog
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import time
import os
import keyboard

class DrawingApp:
    def __init__(self, root, color_window):
        self.root = root
        self.color_window = color_window

        self.configure_windows()
        self.setup_main_window()
        self.setup_canvas()
        self.setup_color_window()

        self.pen_color = 'red'
        self.pen_width = 5
        self.last_escape_time = 0

        self.drawing_enabled = True
        self.text_mode = False
        self.old_x = None
        self.old_y = None

        self.bind_hotkeys()
        self.bind_events()

    def configure_windows(self):
        """Set up window configurations"""
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 1.0)  # Set window transparency
        self.root.configure(bg='white')

        self.color_window.attributes('-topmost', True)
        self.color_window.attributes('-alpha', 1.0)
        self.color_window.configure(bg='white')

    def setup_main_window(self):
        """Initialize the main drawing window"""
        self.canvas = tk.Canvas(self.root, cursor='cross', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def setup_canvas(self):
        """Set up the drawing canvas"""
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        screen_image = ImageGrab.grab(bbox=(0, 0, width, height))
        self.tk_screen_image = ImageTk.PhotoImage(screen_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_screen_image)

    def setup_color_window(self):
        """Initialize the color and pen width selection window"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        color_window_width = 600
        color_window_height = 150
        x_position = (screen_width // 2) - (color_window_width // 2)
        y_position = screen_height - color_window_height - 50
        self.color_window.geometry(f'{color_window_width}x{color_window_height}+{x_position}+{y_position}')

        color_frame = tk.Frame(self.color_window, bg='white', padx=10, pady=10)
        color_frame.pack(fill=tk.BOTH, expand=True)

        self.create_color_buttons(color_frame)
        self.create_pen_width_buttons(color_frame)
        self.create_text_mode_button(color_frame)
        self.create_draw_mode_button(color_frame)

    def create_color_buttons(self, frame):
        """Create buttons for color selection"""
        tk.Label(frame, text="选择颜色:", bg='white', font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        colors = ['red', 'black', 'green', 'blue', 'yellow', 'purple', 'orange']
        for idx, color in enumerate(colors):
            btn = tk.Button(frame, bg=color, width=4, height=2, command=lambda col=color: self.set_color(col))
            btn.grid(row=0, column=idx+1, padx=5, pady=5)

    def create_pen_width_buttons(self, frame):
        """Create buttons for pen width selection"""
        tk.Label(frame, text="选择画笔粗细:", bg='white', font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        for idx, width in enumerate(range(2, 12, 2)):
            btn = tk.Button(frame, text=str(width), width=4, height=2, command=lambda w=width: self.set_width(w))
            btn.grid(row=1, column=idx+1, padx=5, pady=5)

    def create_text_mode_button(self, frame):
        """Create button to enable text mode"""
        self.text_button = tk.Button(frame, text="文本框", width=6, height=2, command=self.enable_text_mode)
        self.text_button.grid(row=1, column=len(range(2, 12, 2))+1, padx=5, pady=5)

    def create_draw_mode_button(self, frame):
        """Create button to enable drawing mode"""
        self.draw_button = tk.Button(frame, text="画图", width=6, height=2, command=self.enable_draw_mode)
        self.draw_button.grid(row=1, column=len(range(2, 12, 2))+2, padx=5, pady=5)

    def set_color(self, color):
        """Set the pen color"""
        self.pen_color = color

    def set_width(self, width):
        """Set the pen width"""
        self.pen_width = width

    def bind_hotkeys(self):
        """Bind global hotkeys for drawing actions"""
        keyboard.add_hotkey('F1', lambda: self.start_drawing(), suppress=True)
        keyboard.add_hotkey('F2', lambda: self.save_and_clear(), suppress=True)
        keyboard.add_hotkey('Esc', lambda: self.handle_escape(), suppress=True)

    def bind_events(self):
        """Bind events for drawing actions"""
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

    def start_drawing(self):
        """Enable drawing mode"""
        self.drawing_enabled = True
        self.text_mode = False
        self.capture_screen_background()
        self.bring_to_front(self.root)

    def enable_draw_mode(self):
        """Enable drawing mode"""
        self.drawing_enabled = True
        self.text_mode = False
        self.canvas.bind('<Button-1>', self.paint)

    def enable_text_mode(self):
        """Enable text mode"""
        self.text_mode = True
        self.drawing_enabled = False
        self.canvas.bind('<Button-1>', self.place_text)

    def place_text(self, event):
        """Place text on the canvas at the specified coordinates"""
        if self.text_mode:
            text_input = simpledialog.askstring("输入文本", "请输入文本:")
            if text_input:
                self.canvas.create_text(event.x, event.y, text=text_input, fill=self.pen_color, font=('Arial', self.pen_width * 4))

    def capture_screen_background(self):
        """Capture the screen background for drawing"""
        self.root.withdraw()  # Hide the root window
        time.sleep(0.2)  # Wait briefly to ensure the root window is hidden
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        screen_image = ImageGrab.grab(bbox=(0, 0, width, height))
        self.root.deiconify()  # Show the root window again
        self.tk_screen_image = ImageTk.PhotoImage(screen_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_screen_image)

    def paint(self, event):
        """Draw on the canvas"""
        if self.drawing_enabled:
            if self.old_x and self.old_y:
                self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, width=self.pen_width, fill=self.pen_color, capstyle=tk.ROUND, smooth=tk.TRUE)
            self.old_x = event.x
            self.old_y = event.y

    def reset(self, event):
        """Reset the drawing coordinates"""
        self.old_x = None
        self.old_y = None

    def handle_escape(self):
        """Handle the escape key press event"""
        current_time = time.time()
        if current_time - self.last_escape_time < 1:
            self.save_drawing()
            self.exit_drawing()
        else:
            self.save_drawing()
        self.last_escape_time = current_time

    def save_and_clear(self):
        """Save the drawing and clear the canvas"""
        self.save_drawing()
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_screen_image)

    def save_drawing(self):
        """Save the current drawing to a file"""
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        if not os.path.exists('DrawingAppImg'):
            os.makedirs('DrawingAppImg')

        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f'DrawingAppImg/DrawOnScreen-{timestamp}.png'
        ImageGrab.grab(bbox=(x, y, x1, y1)).save(filename)
        print(f'Saved drawing as {filename}')

    def exit_drawing(self):
        """Exit the drawing mode"""
        self.root.quit()
        self.color_window.quit()

    def bring_to_front(self, window):
        """Bring the specified window to the front"""
        window.attributes('-topmost', True)
        window.update()
        window.attributes('-topmost', False)

if __name__ == '__main__':
    root = tk.Tk()
    color_window = tk.Toplevel(root)
    app = DrawingApp(root, color_window)
    root.mainloop()
