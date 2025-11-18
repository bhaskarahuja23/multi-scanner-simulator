import tkinter as tk
from tkinter import ttk
import math
import random

CANVAS_SIZE = 360  # size of each sensor map (square)

# Conceptual detection abilities:
# Radar: surface stuff (ship, iceberg)
# Sonar: underwater / animals (whale, submarine)
# LiDAR: surface, near range (ship, iceberg)
SENSOR_CAPABILITIES = {
    "radar": {"Ship", "Iceberg"},
    "sonar": {"Whale", "Submarine"},
    "lidar": {"Ship", "Iceberg"},
}


class MultiScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Radar / Sonar / LiDAR Multi Scanner")
        self.geometry("1300x640")
        self.configure(bg="#111111")

        # Shared list of objects in the ocean:
        # each is {"angle_deg": float, "dist_norm": float, "kind": str}
        self.objects = []

        # Sweep angle for each sensor
        self.sweep = {"radar": 0.0, "sonar": 0.0, "lidar": 0.0}
        # Blips for each sensor (for fading)
        self.blips = {"radar": [], "sonar": [], "lidar": []}

        # Current object type selection (Ship / Whale / Submarine / Iceberg)
        self.object_type = tk.StringVar(value="Ship")
        self.object_buttons = {}  # to recolor buttons when selection changes

        # Text for last-added object
        self.last_object_text = tk.StringVar(value="No objects added yet.")

        # Layout
        self.rowconfigure(0, weight=0)   # top controls row
        self.rowconfigure(1, weight=1)   # scanners row
        for c in range(3):
            self.columnconfigure(c, weight=1)

        self.create_top_controls()
        self.create_canvases()

        # Start animation
        self.after(50, self.update_frame)

    # ---------------------------------------------------
    # Top controls (object buttons + actions)
    # ---------------------------------------------------
    def create_top_controls(self):
        # Use tk.Frame so we can control background color
        top = tk.Frame(self, bg="#111111", padx=10, pady=10)
        top.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Row 0: object type label + 4 buttons
        tk.Label(
            top,
            text="Object type:",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#111111",
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))

        types = ["Ship", "Whale", "Submarine", "Iceberg"]
        for i, kind in enumerate(types, start=1):
            btn = tk.Button(
                top,
                text=kind,
                width=10,
                command=lambda k=kind: self.select_object_type(k),
                relief="raised",
                bg="#333333",
                fg="white",
                activebackground="#555555",
            )
            btn.grid(row=0, column=i, padx=3)
            self.object_buttons[kind] = btn

        # Initialize selection color
        self.update_object_buttons()

        # Row 1: action buttons
        add_btn = ttk.Button(top, text="Add random object", command=self.add_random_object)
        add_btn.grid(row=1, column=0, padx=3, pady=(5, 0), sticky="w")

        clear_btn = ttk.Button(top, text="Clear objects", command=self.clear_objects)
        clear_btn.grid(row=1, column=1, padx=3, pady=(5, 0), sticky="w")

        # Row 1: sensor logic info
        info_label = tk.Label(
            top,
            text=(
                "Radar: ships & icebergs   |   "
                "Sonar: whales & submarines   |   "
                "LiDAR: close ships & icebergs"
            ),
            font=("Segoe UI", 10),
            fg="#dddddd",
            bg="#111111",
        )
        info_label.grid(row=1, column=2, columnspan=3, padx=12, pady=(5, 0), sticky="w")

        # Row 2: last object info bar (bright text on dark background)
        last_obj_label = tk.Label(
            top,
            textvariable=self.last_object_text,
            font=("Segoe UI", 11, "bold"),
            fg="#00FF99",       # bright radar-style color
            bg="#111111",       # dark background
        )
        last_obj_label.grid(row=2, column=0, columnspan=6, pady=(8, 0), sticky="w")

    def select_object_type(self, kind):
        """Called when user clicks one of the object selector buttons."""
        self.object_type.set(kind)
        self.update_object_buttons()

    def update_object_buttons(self):
        """Color the selected object button green, others dark."""
        selected = self.object_type.get()
        for kind, btn in self.object_buttons.items():
            if kind == selected:
                btn.config(bg="#00aa00", fg="white", relief="sunken")
            else:
                btn.config(bg="#333333", fg="white", relief="raised")

    # ---------------------------------------------------
    # Three canvases: Radar, Sonar, LiDAR
    # ---------------------------------------------------
    def create_canvases(self):
        # Radar canvas (left)
        self.radar_canvas = tk.Canvas(
            self,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="black",
            highlightthickness=1,
            highlightbackground="white",
        )
        self.radar_canvas.grid(row=1, column=0, padx=10, pady=10)

        # Sonar canvas (middle)
        self.sonar_canvas = tk.Canvas(
            self,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="black",
            highlightthickness=1,
            highlightbackground="white",
        )
        self.sonar_canvas.grid(row=1, column=1, padx=10, pady=10)

        # LiDAR canvas (right)
        self.lidar_canvas = tk.Canvas(
            self,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="black",
            highlightthickness=1,
            highlightbackground="white",
        )
        self.lidar_canvas.grid(row=1, column=2, padx=10, pady=10)

        # Draw static background for each sensor
        self.draw_background(self.radar_canvas, "Radar")
        self.draw_background(self.sonar_canvas, "Sonar")
        self.draw_background(self.lidar_canvas, "Laser")

    def draw_background(self, canvas, sensor_type):
        """Draw circular map, range rings, cross-lines, and sensor label."""
        canvas.delete("bg")
        cx = CANVAS_SIZE // 2
        cy = CANVAS_SIZE // 2
        r = CANVAS_SIZE // 2 - 20  # some margin

        color = self.get_sensor_color(sensor_type, 0.9)

        # Outer circle
        canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            outline=color,
            width=2,
            tags="bg",
        )

        # Range rings
        for frac in [0.25, 0.5, 0.75]:
            rr = int(r * frac)
            canvas.create_oval(
                cx - rr,
                cy - rr,
                cx + rr,
                cy + rr,
                outline="#004400",
                width=1,
                tags="bg",
            )

        # Cross-lines
        canvas.create_line(
            cx - r, cy, cx + r, cy, fill="#004400", width=1, tags="bg"
        )
        canvas.create_line(
            cx, cy - r, cx, cy + r, fill="#004400", width=1, tags="bg"
        )

        # Angle labels (inside, so numbers are not cut off)
        canvas.create_text(
            cx, cy - r + 12, text="0°", fill=color, tags="bg"
        )
        canvas.create_text(
            cx + r - 12, cy, text="90°", fill=color, tags="bg"
        )
        canvas.create_text(
            cx, cy + r - 12, text="180°", fill=color, tags="bg"
        )
        canvas.create_text(
            cx - r + 20, cy, text="270°", fill=color, tags="bg"
        )

        # Ship at center
        canvas.create_oval(
            cx - 5,
            cy - 5,
            cx + 5,
            cy + 5,
            fill="#aaaaaa",
            outline="#ffffff",
            tags="bg",
        )

        # Sensor label in the center
        canvas.create_text(
            cx,
            cy,
            text=sensor_type,
            fill=color,
            font=("Segoe UI", 12, "bold"),
            tags="bg",
        )

    def get_sensor_color(self, sensor, intensity=1.0):
        """Return bright-ish color per sensor type."""
        if sensor == "Radar":
            base = (0, 255, 0)  # green
        elif sensor == "Sonar":
            base = (0, 220, 255)  # cyan
        else:  # Laser / LiDAR
            base = (255, 255, 0)  # yellow

        r = int(base[0] * intensity)
        g = int(base[1] * intensity)
        b = int(base[2] * intensity)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ---------------------------------------------------
    # Objects (shared ocean)
    # ---------------------------------------------------
    def add_random_object(self):
        """Add one random object at random angle and distance, update text bar."""
        angle_deg = random.uniform(0, 360)
        dist_norm = random.uniform(0, 0.95)  # 0=center, 1=edge
        kind = self.object_type.get()

        obj = {
            "angle_deg": angle_deg,
            "dist_norm": dist_norm,
            "kind": kind,
        }
        self.objects.append(obj)

        # Update info bar text (bright color label)
        self.last_object_text.set(
            f"Last object added → {kind} at angle {angle_deg:.1f}°, range ≈ {dist_norm * 100:.0f}% of max."
        )

        # Optional console print
        print("Added object:", obj)

    def clear_objects(self):
        """Remove all objects and visual blips."""
        self.objects = []
        for key in self.blips:
            self.blips[key] = []

        for cv in (self.radar_canvas, self.sonar_canvas, self.lidar_canvas):
            cv.delete("sweep")
            cv.delete("blip")

        self.last_object_text.set("Objects cleared. No objects in the ocean.")

    # ---------------------------------------------------
    # Animation loop
    # ---------------------------------------------------
    def update_frame(self):
        # Rotate each sweep
        self.sweep["radar"] = (self.sweep["radar"] + 2) % 360
        self.sweep["sonar"] = (self.sweep["sonar"] + 2) % 360
        self.sweep["lidar"] = (self.sweep["lidar"] + 2) % 360

        # Draw sweeps
        self.draw_sweep(self.radar_canvas, "Radar", self.sweep["radar"])
        self.draw_sweep(self.sonar_canvas, "Sonar", self.sweep["sonar"])
        self.draw_sweep(self.lidar_canvas, "Laser", self.sweep["lidar"])

        # Check detections (with capability logic)
        self.check_detections("radar", self.radar_canvas, "Radar")
        self.check_detections("sonar", self.sonar_canvas, "Sonar")
        self.check_detections("lidar", self.lidar_canvas, "Laser")

        # Update fading blips
        self.update_blips("radar", self.radar_canvas, "Radar")
        self.update_blips("sonar", self.sonar_canvas, "Sonar")
        self.update_blips("lidar", self.lidar_canvas, "Laser")

        # Schedule next frame
        self.after(50, self.update_frame)

    def draw_sweep(self, canvas, sensor_type, angle_deg):
        canvas.delete("sweep")
        cx = CANVAS_SIZE // 2
        cy = CANVAS_SIZE // 2
        r = CANVAS_SIZE // 2 - 20

        angle_rad = math.radians(angle_deg)
        ex = cx + r * math.sin(angle_rad)
        ey = cy - r * math.cos(angle_rad)

        color = self.get_sensor_color(sensor_type, 1.0)
        canvas.create_line(
            cx, cy, ex, ey, fill=color, width=2, tags="sweep"
        )

    @staticmethod
    def ang_diff(a, b):
        """Smallest signed angle difference in degrees."""
        return (a - b + 180) % 360 - 180

    def check_detections(self, key, canvas, sensor_label):
        """Create blips if sweep passes close to an object, respecting physics logic."""
        cx = CANVAS_SIZE // 2
        cy = CANVAS_SIZE // 2
        r = CANVAS_SIZE // 2 - 20

        # Max usable range for each sensor
        if key == "radar":
            max_range = 1.0
        elif key == "sonar":
            max_range = 1.0
        else:  # lidar
            max_range = 0.6

        beam_angle = self.sweep[key]
        beam_half_width = 4.0  # ±4°

        allowed_kinds = SENSOR_CAPABILITIES[key]

        for obj in self.objects:
            dn = obj["dist_norm"]
            if dn > max_range:
                continue

            kind = obj["kind"]

            # Core logic: only detect if sensor is capable of this object type
            if kind not in allowed_kinds:
                continue

            diff = abs(self.ang_diff(beam_angle, obj["angle_deg"]))
            if diff <= beam_half_width:
                angle_rad = math.radians(obj["angle_deg"])
                dist_px = r * dn
                x = cx + dist_px * math.sin(angle_rad)
                y = cy - dist_px * math.cos(angle_rad)

                color = self.get_sensor_color(sensor_label, 1.0)
                item = canvas.create_oval(
                    x - 5,
                    y - 5,
                    x + 5,
                    y + 5,
                    fill=color,
                    outline="",
                    tags="blip",
                )
                self.blips[key].append({"item": item, "age": 0, "max_age": 25})

    def update_blips(self, key, canvas, sensor_label):
        """Fade out previously detected blips."""
        new_list = []
        for blip in self.blips[key]:
            blip["age"] += 1
            if blip["age"] >= blip["max_age"]:
                canvas.delete(blip["item"])
                continue

            intensity = max(0.0, 1.0 - blip["age"] / blip["max_age"])
            color = self.get_sensor_color(sensor_label, intensity)
            canvas.itemconfig(blip["item"], fill=color)
            new_list.append(blip)

        self.blips[key] = new_list


if __name__ == "__main__":
    app = MultiScannerApp()
    app.mainloop()
