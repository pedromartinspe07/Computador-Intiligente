import pygame
import sys
import json
import os
import random
import threading
import time
import cv2
import pyttsx3

# =====================
# ======= VOZ =========
# =====================
engine = pyttsx3.init(driverName="espeak")
engine.setProperty("rate", 135)
engine.setProperty("volume", 1.0)

for voice in engine.getProperty("voices"):
    if "english" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break

fala_lock = threading.Lock()

def falar(texto):
    def _fala():
        with fala_lock:
            engine.say(texto)
            engine.runAndWait()
    threading.Thread(target=_fala, daemon=True).start()

# =====================
# ======= CPU =========
# =====================
registradores = {
    "A": 0,
    "B": 0,
    "C": 1,
    "STATE": "IDLE"
}

def add():
    registradores["A"] += registradores["B"]

def sub():
    registradores["A"] -= registradores["B"]

# =====================
# ======= RAM =========
# =====================
RAM_SIZE = 1024
ram = [0] * RAM_SIZE

# =====================
# ======= HD ==========
# =====================
HD_FILE = "hd_virtual.json"

def hd_init():
    if not os.path.exists(HD_FILE):
        with open(HD_FILE, "w", encoding="utf-8") as f:
            json.dump({"memory": []}, f, indent=4)

def hd_write(entry):
    with open(HD_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["memory"].append(entry)
        f.seek(0)
        json.dump(data, f, indent=4)

hd_init()

# =====================
# ======= GPU =========
# =====================
pygame.init()

display_info = pygame.display.Info()
SCREEN_W = display_info.current_w
SCREEN_H = display_info.current_h

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Computador Inteligente")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# =====================
# ======= SENSORES =====
# =====================
sensores = {
    "screen_width": SCREEN_W,
    "screen_height": SCREEN_H,
    "screen_area": SCREEN_W * SCREEN_H
}

# =====================
# ======= IA ==========
# =====================
ultimo_fala = 0

def ia_controller():
    global ultimo_fala

    if registradores["C"] != 1:
        return

    A = registradores["A"]

    # ---- Estados mentais ----
    if A < 40:
        registradores["STATE"] = "IDLE"
        registradores["B"] = random.randint(1, 3)
        add()
        texto = "System idle. Light processing."

    elif A < 120:
        registradores["STATE"] = "ACTIVE"
        registradores["B"] = random.randint(3, 6)
        add()
        texto = "System active. Optimizing tasks."

    else:
        registradores["STATE"] = "OVERLOAD"
        registradores["B"] = random.randint(1, 4)
        sub()
        texto = "Warning. Reducing load."

    hd_write({
        "A": registradores["A"],
        "B": registradores["B"],
        "STATE": registradores["STATE"],
        "SCREEN": sensores
    })

    agora = time.time()
    if agora - ultimo_fala > 4:
        falar(texto)
        ultimo_fala = agora

# =====================
# ======= CÂMERA ======
# =====================
camera = cv2.VideoCapture(0)
camera_ok = camera.isOpened()

# =====================
# ======= LOOP ========
# =====================
size = 80
direction = 1
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ia_controller()

    size += direction * 2
    if size > 200 or size < 60:
        direction *= -1

    # ---- Cor muda conforme estado ----
    if registradores["STATE"] == "IDLE":
        bg = (10, 30, 40)
    elif registradores["STATE"] == "ACTIVE":
        bg = (20, 80, 40)
    else:
        bg = (120, 30, 30)

    screen.fill(bg)

    pygame.draw.polygon(
        screen,
        (255, 255, 255),
        [
            (WIDTH//2, HEIGHT//2 - size),
            (WIDTH//2 - size, HEIGHT//2 + size),
            (WIDTH//2 + size, HEIGHT//2 + size)
        ]
    )

    screen.blit(font.render(f"A={registradores['A']}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"STATE={registradores['STATE']}", True, (255,255,255)), (10,30))
    screen.blit(
        font.render(
            f"Screen: {sensores['screen_width']}x{sensores['screen_height']}",
            True,
            (0,200,255)
        ),
        (10,50)
    )

    pygame.display.flip()

    if camera_ok:
        ret, frame = camera.read()
        if ret:
            frame = cv2.resize(frame, (320, 240))
            cv2.imshow("Camera Sensor", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

# =====================
# ======= FINAL =======
# =====================
pygame.quit()
if camera_ok:
    camera.release()
    cv2.destroyAllWindows()
sys.exit()
