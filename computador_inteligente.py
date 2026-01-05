import pygame
import sys
import json
import os
import random

# =====================
# ======= CPU =========
# =====================
registradores = {
    "A": 0,   # acumulador
    "B": 0,   # operando
    "C": 1,   # CONTROLE (1 = IA ativa)
    "STATE": 0
}

def add():
    registradores["A"] += registradores["B"]

def sub():
    registradores["A"] -= registradores["B"]

# =====================
# ======= RAM =========
# =====================
RAM_SIZE = 2000
ram = [0] * RAM_SIZE

def ram_write(addr, val):
    if 0 <= addr < RAM_SIZE:
        ram[addr] = val

def ram_read(addr):
    if 0 <= addr < RAM_SIZE:
        return ram[addr]
    return 0

# =====================
# ======= HD ==========
# =====================
HD_FILE = "hd_virtual.json"

def hd_init():
    if not os.path.exists(HD_FILE):
        with open(HD_FILE, "w") as f:
            json.dump({"memory": []}, f)

def hd_read():
    with open(HD_FILE, "r") as f:
        return json.load(f)

def hd_write(entry):
    data = hd_read()
    data["memory"].append(entry)
    with open(HD_FILE, "w") as f:
        json.dump(data, f, indent=4)

hd_init()

# =====================
# ======= GPU =========
# =====================
WIDTH, HEIGHT = 640, 480
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Computador Inteligente (IA + CPU + RAM + HD + GPU)")
clock = pygame.time.Clock()

framebuffer = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]

class Vertex:
    def __init__(self, x, y, color):
        self.x = int(x)
        self.y = int(y)
        self.color = color

def clear(color):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            framebuffer[y][x] = color

def put_pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        framebuffer[y][x] = color

def draw_framebuffer():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            screen.set_at((x, y), framebuffer[y][x])

def edge(a, b, c):
    return (c.x - a.x) * (b.y - a.y) - (c.y - a.y) * (b.x - a.x)

def interpolate(c1, c2, c3, w1, w2, w3):
    return (
        int(c1[0]*w1 + c2[0]*w2 + c3[0]*w3),
        int(c1[1]*w1 + c2[1]*w2 + c3[1]*w3),
        int(c1[2]*w1 + c2[2]*w2 + c3[2]*w3),
    )

def draw_triangle(v1, v2, v3):
    min_x = max(min(v1.x, v2.x, v3.x), 0)
    max_x = min(max(v1.x, v2.x, v3.x), WIDTH - 1)
    min_y = max(min(v1.y, v2.y, v3.y), 0)
    max_y = min(max(v1.y, v2.y, v3.y), HEIGHT - 1)

    area = edge(v1, v2, v3)
    if area == 0:
        return

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            p = Vertex(x, y, (0, 0, 0))
            w1 = edge(v2, v3, p) / area
            w2 = edge(v3, v1, p) / area
            w3 = edge(v1, v2, p) / area

            if w1 >= 0 and w2 >= 0 and w3 >= 0:
                put_pixel(x, y, interpolate(v1.color, v2.color, v3.color, w1, w2, w3))

# =====================
# ======= IA ==========
# =====================
def ia_controller():
    """
    Unidade de controle inteligente
    """
    if registradores["C"] != 1:
        return

    # Sensoriamento
    A = registradores["A"]

    # Decisão
    if A < 50:
        registradores["B"] = random.randint(1, 5)
        add()
        action = "ADD"
    else:
        registradores["B"] = random.randint(1, 3)
        sub()
        action = "SUB"

    # Estado
    registradores["STATE"] = A

    # Aprendizado simples (log)
    hd_write({
        "A": registradores["A"],
        "B": registradores["B"],
        "ACTION": action
    })

# =====================
# ===== LOOP ==========
# =====================
size = 80
direction = 1

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # IA controla CPU
    ia_controller()

    # IA influencia GPU
    size += direction * 2
    if size > 200 or size < 60:
        direction *= -1

    clear((10, 10 + registradores["A"] % 200, 40))

    cx, cy = WIDTH // 2, HEIGHT // 2

    v1 = Vertex(cx, cy - size, (255, 0, 0))
    v2 = Vertex(cx - size, cy + size, (0, 255, 0))
    v3 = Vertex(cx + size, cy + size, (0, 0, 255))

    draw_triangle(v1, v2, v3)
    draw_framebuffer()
    pygame.display.flip()
