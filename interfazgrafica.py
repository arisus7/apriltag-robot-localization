from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import math
import time


FIELD_LENGTH = 3.60
FIELD_WIDTH = 2.80
FIELD_LENGTH = 3.00
FIELD_WIDTH = 3.00

TAGS = [
(0, 0.0,   1.11,  "right"),
    (1, 1.230, 0.0,   "down"),
    (1, 1.230, 0.0,   "up"),
(2, 0.0,   2.197, "right"),
(3, 3.60,  1.038, "left"),
    (4, 2.634, 0.0,   "down"),
    (5, 2.51,  2.8,   "up"),
    (6, 1.35,  2.8,   "up"),
    (4, 2.634, 0.0,   "up"),
    (5, 2.51,  2.8,   "down"),
    (6, 1.35,  2.8,   "down"),
(7, 3.60,  1.985, "left")
]

def dir_to_vector(direction):
    """Convierte texto -> vector de dirección"""
if direction == "right": return (0.20, 0)
if direction == "left":  return (-0.20, 0)
if direction == "up":    return (0, 0.20)
if direction == "down":  return (0, -0.20)
return (0, 0)

# FUNCIÓN genérica para obtener posición cámara
# Ajustar un tag al borde más cercano
def snap_to_wall(x, y):
    margin = 0.02  # qué tan pegado queda

    # Distancias a paredes
    dist_left   = x
    dist_right  = FIELD_LENGTH - x
    dist_bottom = y
    dist_top    = FIELD_WIDTH - y

    min_dist = min(dist_left, dist_right, dist_bottom, dist_top)

    # Moverlo a la pared más cercana
    if min_dist == dist_left:
        x = margin
    elif min_dist == dist_right:
        x = FIELD_LENGTH - margin
    elif min_dist == dist_bottom:
        y = margin
    else:
        y = FIELD_WIDTH - margin

def get_camera_position():
    """
    Reemplazar estaparn NetworkTables o JSON.
    """
    # EJEMPLO SIMULADO (moverse en un círculo)
    import math, time
    t = time.time()
    x = 1.8 + 0.8 * math.cos(t)
    y = 1.4 + 0.8 * math.sin(t)
return x, y

# ACTUALIZAR EL PLOT

def get_camera_position():
    try:
        response = requests.get("http://10.34.23.233:5000/posicion/actual", timeout=0.3)
        if response.status_code == 200:
            datos = response.json()
            return float(datos["x"]), float(datos["y"])
    except:
        pass
    return 1.8, 1.4


def update_plot():
ax.clear()

    # Campo
    ax.set_title("Mapa del Campo con AprilTags y Cámara")
    ax.set_xlim(0, FIELD_LENGTH)
    ax.set_title("Mapa del Campo con AprilTags y Cámara", pad= 25)
    ax.set_xlim(0, FIELD_LENGTH + -0.05)   # más espacio a la derecha
ax.set_ylim(0, FIELD_WIDTH)
ax.set_aspect("equal")
ax.grid(True)

    # Dibujar bordes
    ax.plot(
        [0, FIELD_LENGTH, FIELD_LENGTH, 0, 0],
        [0, 0, FIELD_WIDTH, FIELD_WIDTH, 0],
        color="black"
    )
    ax.plot([0, FIELD_LENGTH, FIELD_LENGTH, 0, 0],
            [0, 0, FIELD_WIDTH, FIELD_WIDTH, 0],
            color="black")

    cam_x, cam_y = get_camera_position()

    try:
        response = requests.get("http://10.34.23.233:5000/posicion/actual", timeout=0.3)
        rot = float(response.json().get("rotation", 0))
    except:
        rot = 0

    # Delay anti-saturación
    time.sleep(0.1)

    # Dibujar Tags
    FOV_ANGLE = 60
    VIEW_DISTANCE = 3.0

    center_rad = math.radians(rot)
    left_rad = math.radians(rot + FOV_ANGLE/2)
    right_rad = math.radians(rot - FOV_ANGLE/2)

    p_left = (cam_x + VIEW_DISTANCE * math.cos(left_rad),
              cam_y + VIEW_DISTANCE * math.sin(left_rad))
    p_right = (cam_x + VIEW_DISTANCE * math.cos(right_rad),
               cam_y + VIEW_DISTANCE * math.sin(right_rad))

    ax.plot([cam_x, p_left[0]],  [cam_y, p_left[1]],  color="cyan")
    ax.plot([cam_x, p_right[0]], [cam_y, p_right[1]], color="cyan")
    ax.plot([p_left[0], p_right[0]],
            [p_left[1], p_right[1]],
            color="cyan", linestyle="dashed")

    def punto_en_fov(px, py):
        dx = px - cam_x
        dy = py - cam_y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist > VIEW_DISTANCE:
            return False

        ang = math.degrees(math.atan2(dy, dx))
        diff = (ang - rot + 180) % 360 - 180
        return abs(diff) <= (FOV_ANGLE / 2)

    # DIBUJAR TAGS
for tag_id, x, y, direction in TAGS:
        dx, dy = dir_to_vector(direction)

        ax.scatter(x, y, s=250, color="gold", edgecolor="black")
        ax.text(x, y + 0.12, f"Tag {tag_id}", ha="center")
        # Pegar tag a la pared si no lo está
        x_snap, y_snap = snap_to_wall(x, y)

        ax.arrow(
            x, y, dx, dy,
            head_width=0.12, head_length=0.12,
            fc="green", ec="green"
        )
        color_tag = "red" if punto_en_fov(x_snap, y_snap) else "gold"
        dx, dy = dir_to_vector(direction)

    # Dibujar cámara
    cam_x, cam_y = get_camera_position()
        ax.scatter(x_snap, y_snap, s=250, color=color_tag, edgecolor="black")

        # TEXTO FUERA DEL CUADRO, PEGADO AL TAG
        offset = 0.18
        text_x = x_snap
        text_y = y_snap

        # Si está en la pared izquierda → texto afuera a la izquierda
        if x_snap <= 0.03:
            text_x = -0.25
        # pared derecha
        elif x_snap >= FIELD_LENGTH - 0.03:
            text_x = FIELD_LENGTH + 0.1
        # pared inferior
        elif y_snap <= 0.03:
            text_y = -0.15
        # pared superior
        elif y_snap >= FIELD_WIDTH - 0.03:
            text_y = FIELD_WIDTH + 0.1

        ax.text(text_x, text_y, f"Tag {tag_id}", ha="center", va="center")

        ax.arrow(x_snap, y_snap, dx, dy,
                 head_width=0.12, head_length=0.12,
                 fc="green", ec="green")

    # Cámara
ax.scatter(cam_x, cam_y, s=300, color="lime")
ax.text(cam_x, cam_y + 0.12, "CAM", ha="center", color="lime")

canvas.draw()
    root.after(100, update_plot)

    root.after(150, update_plot)

# GUI TKINTER

# GUI
root = tk.Tk()
root.title("GUI AprilTags + Cámara")
root.geometry("700x600")
root.geometry("900x600")

fig, ax = plt.subplots(figsize=(7, 5))
fig, ax = plt.subplots(figsize=(8, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=BOTH, expand=True)

update_plot()
root.mainloop()
root.mainloop()