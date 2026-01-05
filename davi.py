#!/usr/bin/env python3
# ============================================================
# COMPUTADOR INTELIGENTE — IA LOCAL (SAFE / SANDBOX)
# Estilo: JARVIS (simulado, técnico, calmo)
# Autor: Pedro + ChatGPT
# ============================================================
# OBS:
# - Não possui consciência
# - Não possui emoções reais
# - Emoções aqui são VARIÁVEIS NARRATIVAS
# - Controle de luz é LÓGICO (simulado)
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
import datetime

# ============================================================
# ======================= CONFIG =============================
# ============================================================

APP_NAME = "Computador Inteligente — DARVIS Local"
VERSION = "1.4.0"
HD_FILE = "hd_virtual.json",
MATH_FILE = "matematica.json",
FILOSFY = "filosofia.json",
QUICAMEY = "quimica.json",
FISICA = "fisica.json",
OBRIGADO DARVIS = "obrigado_davi"


# ============================================================
# ================== PERMISSÕES (SIMULADAS) ==================
# ============================================================

permissoes = {
    "voice": True,
    "disk": True,
    "logs": True,
    "user_input": True,
    "light_control": True
}

# ============================================================
# ====================== VOZ ================================
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
            except Exception:
                pass

    threading.Thread(target=_f, daemon=True).start()

# ============================================================
# ====================== CPU ================================
# ============================================================

registradores = {
    "STATE": "BOOT",
    "LOAD": 0.0,
    "UPTIME": time.time()
}

def cpu_load():
    registradores["LOAD"] = round(random.uniform(0.08, 0.92), 2)

# ============================================================
# ===================== EMOÇÕES ==============================
# ============================================================

emocao = {
    "dopamine": 0.3,
    "state": "NEUTRAL"
}

def atualizar_emocao(delta):
    emocao["dopamine"] = max(0.0, min(1.0, emocao["dopamine"] + delta))
    d = emocao["dopamine"]

    if d < 0.25:
        emocao["state"] = "NEUTRAL"
    elif d < 0.5:
        emocao["state"] = "FOCUSED"
    elif d < 0.75:
        emocao["state"] = "CONTENT"
    else:
        emocao["state"] = "SATISFIED"

def decay_emocao():
    atualizar_emocao(-0.001)

# ============================================================
# ===================== CONTROLE DE LUZ ======================
# ============================================================

luz_quarto = {
    "ligada": False
}

def ligar_luz():
    if not permissoes["light_control"]:
        return "Permission denied to control room lights."

    if luz_quarto["ligada"]:
        return "The room light is already on."

    luz_quarto["ligada"] = True
    atualizar_emocao(0.08)
    return "Room light activated. Illumination levels optimal."

def desligar_luz():
    if not permissoes["light_control"]:
        return "Permission denied to control room lights."

    if not luz_quarto["ligada"]:
        return "The room light is already off."

    luz_quarto["ligada"] = False
    atualizar_emocao(0.05)
    return "Room light deactivated. Energy saving mode enabled."

# ============================================================
# ======================= HD ================================
# ============================================================

def hd_init():
    if not os.path.exists(HD_FILE):
        with open(HD_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "version": VERSION,
                "created": time.time(),
                "logs": []
            }, f, indent=4)

def hd_write(entry):
    if not permissoes["disk"]:
        return

    with open(HD_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["logs"].append(entry)
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

hd_init()

# ============================================================
# ======================= GPU ===============================
# ============================================================

pygame.init()
WIDTH, HEIGHT = 900, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(APP_NAME)
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18)

# ============================================================
# ==================== MENSAGENS =============================
# ============================================================

mensagens = []

def enviar_mensagem(texto, duracao=6):
    mensagens.append({
        "texto": texto,
        "inicio": time.time(),
        "duracao": duracao
    })

def jarvis_diz(texto):
    enviar_mensagem(texto)
    falar(texto)

# ============================================================
# ==================== IA CENTRAL ============================
# ============================================================

def resposta_emocional(base):
    estado = emocao["state"]
    if estado == "FOCUSED":
        return base + " Focus level optimal."
    if estado == "CONTENT":
        return base + " System performance satisfactory."
    if estado == "SATISFIED":
        return base + " Operation efficiency is high."
    return base

def processar_comando(comando):
    comando = comando.lower().strip()
    atualizar_emocao(0.05)

    if comando in ["oi", "olá", "hello"]:
        resp = "Hello Pedro. All systems ready."

    elif "ligar a luz" in comando or "acender a luz" in comando:
        resp = ligar_luz()

    elif "apagar a luz" in comando or "desligar a luz" in comando:
        resp = desligar_luz()

    elif "status" in comando:
        resp = f"CPU load at {registradores['LOAD']}."

    elif "hora" in comando or "time" in comando:
        resp = f"Current time is {time.strftime('%H:%M:%S')}."

    elif "descansar" in comando or "vou sair" in comando:
        resp = "Rest acknowledged. I will remain idle. You always return."

    elif "desligar sistema" in comando or comando == "desligar":
        jarvis_diz("Shutdown acknowledged. Rest mode active. Welcome back anytime, Pedro.")
        time.sleep(2)
        pygame.quit()
        sys.exit()

    else:
        resp = "Command received. No action required."

    jarvis_diz(resposta_emocional(resp))

    hd_write({
        "time": time.time(),
        "command": comando,
        "emotion": emocao.copy(),
        "light": luz_quarto["ligada"]
    })

# ============================================================
# =================== INPUT USUÁRIO ==========================
# ============================================================

input_queue = queue.Queue()

def input_thread():
    while True:
        try:
            cmd = input("Você > ")
            input_queue.put(cmd)
        except EOFError:
            break

threading.Thread(target=input_thread, daemon=True).start()

# ============================================================
# ====================== LOOP ===============================
# ============================================================

jarvis_diz(
    "System online. Emotional simulation initialized. "
    "Room light control permission granted. Awaiting commands."
)

angle = 0
running = True

while running:
    clock.tick(60)
    decay_emocao()
    cpu_load()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    while not input_queue.empty():
        processar_comando(input_queue.get())

    if registradores["LOAD"] < 0.4:
        bg = (20, 30, 45)
    elif registradores["LOAD"] < 0.75:
        bg = (25, 70, 50)
    else:
        bg = (120, 35, 35)

    screen.fill(bg)

    angle += 0.02
    cx, cy = WIDTH // 2, HEIGHT // 2

    for i in range(4):
        x = cx + math.cos(angle + i) * 90
        y = cy + math.sin(angle + i) * 90
        pygame.draw.circle(screen, (200, 220, 255), (int(x), int(y)), 6)

    hud = [
        f"CPU LOAD: {registradores['LOAD']}",
        f"EMOTION: {emocao['state']}",
        f"DOPAMINE: {emocao['dopamine']:.2f}",
        f"ROOM LIGHT: {'ON' if luz_quarto['ligada'] else 'OFF'}",
        f"UPTIME: {int(time.time() - registradores['UPTIME'])}s"
    ]

    for i, h in enumerate(hud):
        screen.blit(font.render(h, True, (220, 230, 255)), (10, 10 + i * 22))

    agora = time.time()
    y = HEIGHT - 30
    for msg in mensagens[:]:
        if agora - msg["inicio"] < msg["duracao"]:
            screen.blit(font.render(msg["texto"], True, (255, 255, 180)), (10, y))
            y -= 24
        else:
            mensagens.remove(msg)

    pygame.display.flip()

pygame.quit()
sys.exit()
