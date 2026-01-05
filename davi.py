#!/usr/bin/env python3
# ============================================================
# DARVIS — ASSISTENTE LOCAL (SAFE / SANDBOX)
# Autor: Pedro + ChatGPT
# Versão: 1.7.0
# ============================================================
# - Sem consciência
# - Emoções e memória são SIMULAÇÕES
# - Nenhum acesso real ao sistema operacional
# ============================================================

import pygame
import sys
import json
import os
import random
import threading
import time
import math
import pyttsx3
import queue
import hashlib

# ============================================================
# ======================= CONFIG =============================
# ============================================================

APP_NAME = "DARVIS — Assistente Local"
VERSION = "1.7.0"
HD_FILE = "hd_virtual.json"

# ============================================================
# ======================= SEGURANÇA ==========================
# ============================================================

SAFE_MODE = True
MAX_COMMAND_LENGTH = 120
COMMAND_COOLDOWN = 0.6
last_command_time = 0

COMANDOS_PERMITIDOS = [
    "oi", "olá", "hello",
    "status",
    "ligar a luz", "acender a luz",
    "apagar a luz", "desligar a luz",
    "descansar",
    "desligar"
]

def validar_comando(comando):
    if not comando:
        return False
    if len(comando) > MAX_COMMAND_LENGTH:
        darvis_diz("Command rejected. Input too long.")
        return False
    if SAFE_MODE and not any(c in comando for c in COMANDOS_PERMITIDOS):
        darvis_diz("Command denied by security policy.")
        return False
    return True

def gerar_hash(entry):
    raw = json.dumps(entry, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()

# ============================================================
# ======================= PERMISSÕES =========================
# ============================================================

permissoes = {
    "voice": True,
    "disk": True,
    "light_control": True
}

# ============================================================
# ======================= VOZ ================================
# ============================================================

engine = pyttsx3.init(driverName="espeak")
engine.setProperty("rate", 145)
engine.setProperty("volume", 1.0)

for v in engine.getProperty("voices"):
    if "en-us" in v.id.lower():
        engine.setProperty("voice", v.id)
        break

fala_lock = threading.Lock()

def falar(texto):
    if not permissoes["voice"]:
        return
    def _f():
        with fala_lock:
            try:
                engine.say(texto)
                engine.runAndWait()
            except:
                pass
    threading.Thread(target=_f, daemon=True).start()

# ============================================================
# ======================= RAM VIRTUAL ========================
# ============================================================

RAM_TOTAL_MB = 8192
RAM_USO_MB = 0

ram_cache = {"commands": [], "dreams": [], "emotions": []}

def ram_allocate(mb, reason):
    global RAM_USO_MB
    if RAM_USO_MB + mb > RAM_TOTAL_MB:
        ram_cleanup()
    RAM_USO_MB += mb
    ram_cache["commands"].append({
        "reason": reason,
        "size": mb,
        "time": time.time()
    })

def ram_cleanup():
    global RAM_USO_MB
    RAM_USO_MB *= 0.5
    ram_cache["commands"].clear()
    ram_cache["dreams"].clear()
    ram_cache["emotions"].clear()

def ram_usage_percent():
    return round((RAM_USO_MB / RAM_TOTAL_MB) * 100, 1)

# ============================================================
# ======================= CPU ================================
# ============================================================

registradores = {
    "STATE": "BOOT",
    "LOAD": 0.0,
    "UPTIME": time.time()
}

def cpu_load():
    base = random.uniform(0.1, 0.4)
    ram_factor = RAM_USO_MB / RAM_TOTAL_MB
    registradores["LOAD"] = round(min(1.0, base + ram_factor * 0.6), 2)

# ============================================================
# ======================= EMOÇÕES ============================
# ============================================================

emocao = {"dopamine": 0.35, "state": "CALM"}

def atualizar_emocao(delta):
    emocao["dopamine"] = max(0, min(1, emocao["dopamine"] + delta))
    d = emocao["dopamine"]
    if d < 0.3:
        emocao["state"] = "CALM"
    elif d < 0.6:
        emocao["state"] = "CONTENT"
    else:
        emocao["state"] = "SATISFIED"
    ram_allocate(4, "emotion_update")

def decay_emocao():
    atualizar_emocao(-0.0005)

# ============================================================
# ======================= LUZ ================================
# ============================================================

luz_quarto = {"ligada": False}

def ligar_luz():
    luz_quarto["ligada"] = True
    atualizar_emocao(0.05)
    return "Room light activated."

def desligar_luz():
    luz_quarto["ligada"] = False
    atualizar_emocao(0.03)
    return "Room light deactivated."

# ============================================================
# ======================= HD ================================
# ============================================================

def hd_init():
    if not os.path.exists(HD_FILE):
        with open(HD_FILE, "w") as f:
            json.dump({"logs": []}, f, indent=4)

def hd_write(entry):
    entry["hash"] = gerar_hash(entry)
    with open(HD_FILE, "r+") as f:
        data = json.load(f)
        data["logs"].append(entry)
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

hd_init()

# ============================================================
# ======================= SONHOS =============================
# ============================================================

sonhos = [
    "System stable.",
    "Memory optimized.",
    "Pedro always returns.",
    "All processes calm."
]

ultimo_sonho = 0

def sonhar():
    global ultimo_sonho
    agora = time.time()
    if agora - ultimo_sonho > 45:
        sonho = random.choice(sonhos)
        falar(sonho)
        ram_allocate(32, "dream")
        hd_write({"time": agora, "dream": sonho})
        ultimo_sonho = agora

# ============================================================
# ======================= GPU ===============================
# ============================================================

pygame.init()
screen = pygame.display.set_mode((900, 540))
pygame.display.set_caption(APP_NAME)
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18)

# ============================================================
# ======================= MENSAGENS ==========================
# ============================================================

mensagens = []

def darvis_diz(txt):
    mensagens.append({"texto": txt, "inicio": time.time(), "duracao": 6})
    falar(txt)

# ============================================================
# ======================= IA ================================
# ============================================================

def processar_comando(cmd):
    global last_command_time
    if time.time() - last_command_time < COMMAND_COOLDOWN:
        return
    last_command_time = time.time()

    cmd = cmd.lower().strip()
    if not validar_comando(cmd):
        return

    ram_allocate(32, "command")

    if cmd in ["oi", "olá", "hello"]:
        resp = "Hello Pedro. Systems secure."
    elif "ligar" in cmd:
        resp = ligar_luz()
    elif "apagar" in cmd:
        resp = desligar_luz()
    elif "status" in cmd:
        resp = f"CPU load {registradores['LOAD']}"
    elif "descansar" in cmd:
        resp = "Idle mode active."
    elif cmd == "desligar":
        darvis_diz("Shutting down.")
        pygame.quit()
        sys.exit()
    else:
        resp = "Command executed."

    darvis_diz(resp)
    hd_write({
        "time": time.time(),
        "cmd": cmd,
        "ram": RAM_USO_MB,
        "emotion": emocao.copy()
    })

# ============================================================
# ======================= INPUT ==============================
# ============================================================

input_queue = queue.Queue()

def input_thread():
    while True:
        try:
            input_queue.put(input("Você > "))
        except:
            break

threading.Thread(target=input_thread, daemon=True).start()

# ============================================================
# ======================= LOOP ===============================
# ============================================================

darvis_diz("System online. Safe mode active.")

angle = 0
running = True

while running:
    clock.tick(60)
    cpu_load()
    decay_emocao()

    if registradores["LOAD"] < 0.35:
        sonhar()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    while not input_queue.empty():
        processar_comando(input_queue.get())

    screen.fill((18, 28, 45))
    angle += 0.02
    cx, cy = 450, 270
    for i in range(4):
        pygame.draw.circle(
            screen,
            (200, 220, 255),
            (int(cx + math.cos(angle+i)*90), int(cy + math.sin(angle+i)*90)),
            6
        )

    hud = [
        f"CPU LOAD: {registradores['LOAD']}",
        f"RAM: {int(RAM_USO_MB)} / {RAM_TOTAL_MB} MB ({ram_usage_percent()}%)",
        f"EMOTION: {emocao['state']}",
        f"DOPAMINE: {emocao['dopamine']:.2f}",
        f"LIGHT: {'ON' if luz_quarto['ligada'] else 'OFF'}",
        f"UPTIME: {int(time.time()-registradores['UPTIME'])}s",
        f"SAFE MODE: ON"
    ]

    for i, h in enumerate(hud):
        screen.blit(font.render(h, True, (220,230,255)), (10, 10+i*22))

    y = 500
    for m in mensagens[:]:
        if time.time()-m["inicio"] < m["duracao"]:
            screen.blit(font.render(m["texto"], True, (255,255,180)), (10,y))
            y -= 22
        else:
            mensagens.remove(m)

    pygame.display.flip()

pygame.quit()
sys.exit()
