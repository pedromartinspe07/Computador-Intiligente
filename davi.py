#!/usr/bin/env python3
# ============================================================
# DARVIS — ASSISTENTE LOCAL (SAFE / SANDBOX)
# Autor: Pedro + ChatGPT
# Versão: 2.0.0
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
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from collections import deque

# ============================================================
# ======================= CONFIGURAÇÕES ======================
# ============================================================

APP_NAME = "DARVIS — Assistente Local"
VERSION = "2.0.0"
HD_FILE = "hd_virtual.json"
CONFIG_FILE = "darvis_config.json"

# ============================================================
# ======================= TIPOS DE DADOS =====================
# ============================================================

class EmotionState(Enum):
    CALM = "CALM"
    CONTENT = "CONTENT"
    SATISFIED = "SATISFIED"
    EXCITED = "EXCITED"
    LOW = "LOW"

class SystemState(Enum):
    BOOT = "BOOT"
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    SHUTDOWN = "SHUTDOWN"

@dataclass
class Message:
    text: str
    timestamp: float
    duration: float = 6.0

@dataclass
class RAMBlock:
    reason: str
    size_mb: int
    timestamp: float

# ============================================================
# ======================= CLASSE PRINCIPAL ===================
# ============================================================

class DarvisAssistant:
    def __init__(self):
        self.safe_mode = True
        self.config = self.load_config()
        self.setup_constants()
        self.setup_variables()
        self.initialize_systems()
        
    def setup_constants(self):
        """Configura constantes do sistema"""
        self.MAX_COMMAND_LENGTH = 120
        self.COMMAND_COOLDOWN = 0.6
        self.RAM_TOTAL_MB = 8192
        self.RAM_CLEANUP_THRESHOLD = 0.85  # 85% de uso
        
        self.COMANDOS_PERMITIDOS = [
            "oi", "olá", "hello", "hi",
            "status", "sistema", "system",
            "ligar a luz", "acender a luz", "luz ligada",
            "apagar a luz", "desligar a luz", "luz desligada",
            "descansar", "modo descanso", "idle",
            "desligar", "shutdown", "sair",
            "ajuda", "help", "comandos",
            "emoção", "emotion", "sentimento"
        ]
        
        self.sonhos = [
            "System stable. All processes nominal.",
            "Memory optimized. Cache performing well.",
            "Pedro always returns. Pattern confirmed.",
            "All systems calm. No anomalies detected.",
            "Neural pathways clear. Ready for commands.",
            "Learning from interactions. Growing smarter.",
            "Security protocols active. All green.",
            "Virtual circuits humming. Energy efficient.",
            "Database indexed. Queries optimized.",
            "Ambient temperature stable. Cooling nominal."
        ]
    
    def setup_variables(self):
        """Inicializa variáveis do sistema"""
        self.registradores = {
            "STATE": SystemState.BOOT.value,
            "LOAD": 0.0,
            "UPTIME": time.time(),
            "COMMAND_COUNT": 0,
            "ERROR_COUNT": 0
        }
        
        self.emocao = {
            "dopamine": 0.35,
            "state": EmotionState.CALM.value,
            "last_update": time.time(),
            "history": deque(maxlen=100)
        }
        
        self.luz_quarto = {"ligada": False, "intensidade": 100}
        
        self.ram_cache = {
            "blocks": [],
            "total_used": 0,
            "history": deque(maxlen=50)
        }
        
        self.mensagens = []
        self.last_command_time = 0
        self.ultimo_sonho = 0
        self.angle = 0
        self.running = True
        
        # Permissões configuráveis
        self.permissoes = {
            "voice": True,
            "disk": True,
            "light_control": True,
            "dreams": True,
            "learning": False  # Futuro: aprendizado básico
        }
    
    def load_config(self) -> Dict:
        """Carrega configurações do arquivo"""
        default_config = {
            "volume": 1.0,
            "speech_rate": 145,
            "voice": "en-us",
            "theme": "dark",
            "auto_cleanup": True,
            "dream_interval": 45,
            "animation_speed": 1.0
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    # ============================================================
    # ======================= INICIALIZAÇÃO ======================
    # ============================================================
    
    def initialize_systems(self):
        """Inicializa todos os subsistemas"""
        self.hd_init()
        self.setup_voice()
        self.setup_graphics()
        self.setup_input_thread()
        
        # Threads de manutenção
        self.start_maintenance_threads()
    
    def setup_voice(self):
        """Configura o sistema de voz"""
        try:
            self.engine = pyttsx3.init(driverName="espeak")
            self.engine.setProperty("rate", self.config["speech_rate"])
            self.engine.setProperty("volume", self.config["volume"])
            
            # Encontrar voz apropriada
            voices = self.engine.getProperty("voices")
            target_voice = self.config["voice"]
            
            for v in voices:
                if target_voice in v.id.lower():
                    self.engine.setProperty("voice", v.id)
                    break
            
            self.fala_lock = threading.Lock()
        except:
            self.permissoes["voice"] = False
    
    def setup_graphics(self):
        """Configura o sistema gráfico"""
        pygame.init()
        self.screen = pygame.display.set_mode((900, 540))
        pygame.display.set_caption(f"{APP_NAME} v{VERSION}")
        self.clock = pygame.time.Clock()
        
        # Fontes
        self.font_mono = pygame.font.SysFont("Consolas", 16)
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 14)
        
        # Cores do tema
        self.colors = self.get_theme_colors()
    
    def get_theme_colors(self) -> Dict:
        """Retorna paleta de cores baseada no tema"""
        if self.config["theme"] == "dark":
            return {
                "bg": (18, 28, 45),
                "text": (220, 230, 255),
                "accent": (100, 150, 255),
                "warning": (255, 180, 100),
                "success": (100, 255, 180),
                "error": (255, 100, 100),
                "hud_bg": (30, 40, 60, 180)
            }
        else:  # light theme
            return {
                "bg": (240, 245, 255),
                "text": (30, 40, 60),
                "accent": (60, 100, 200),
                "warning": (200, 120, 50),
                "success": (50, 180, 100),
                "error": (200, 50, 50),
                "hud_bg": (220, 230, 245, 200)
            }
    
    def setup_input_thread(self):
        """Configura thread para entrada de comandos"""
        self.input_queue = queue.Queue()
        threading.Thread(target=self.input_thread, daemon=True).start()
    
    def start_maintenance_threads(self):
        """Inicia threads para tarefas de manutenção"""
        # Thread para limpeza periódica de RAM
        threading.Thread(target=self.ram_maintenance_loop, daemon=True).start()
        
        # Thread para salvar estado periodicamente
        threading.Thread(target=self.autosave_loop, daemon=True).start()
    
    # ============================================================
    # ======================= SEGURANÇA ==========================
    # ============================================================
    
    def validar_comando(self, comando: str) -> bool:
        """Valida se o comando é seguro e permitido"""
        if not comando or not comando.strip():
            return False
        
        comando = comando.strip()
        
        # Verificar comprimento
        if len(comando) > self.MAX_COMMAND_LENGTH:
            self.darvis_diz("Command rejected. Input too long.")
            return False
        
        # Verificar cooldown
        current_time = time.time()
        if current_time - self.last_command_time < self.COMMAND_COOLDOWN:
            self.darvis_diz("Command rate limited. Please wait.")
            return False
        
        # Verificar comandos permitidos (modo seguro)
        if self.safe_mode:
            comando_lower = comando.lower()
            if not any(perm in comando_lower for perm in self.COMANDOS_PERMITIDOS):
                self.darvis_diz("Command not recognized in safe mode.")
                return False
        
        return True
    
    def gerar_hash(self, entry: Dict) -> str:
        """Gera hash SHA-256 para entrada"""
        raw = json.dumps(entry, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()
    
    # ============================================================
    # ======================= VOZ ================================
    # ============================================================
    
    def falar(self, texto: str):
        """Fala o texto usando TTS (thread-safe)"""
        if not self.permissoes["voice"]:
            return
        
        def _falar_thread():
            with self.fala_lock:
                try:
                    self.engine.say(texto)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Erro TTS: {e}")
        
        threading.Thread(target=_falar_thread, daemon=True).start()
    
    # ============================================================
    # ======================= RAM VIRTUAL ========================
    # ============================================================
    
    def ram_allocate(self, mb: int, reason: str):
        """Aloca memória RAM virtual"""
        # Verificar se precisa limpar memória
        usage_percent = self.ram_usage_percent()
        if usage_percent > self.RAM_CLEANUP_THRESHOLD * 100:
            self.ram_cleanup(aggressive=True)
        
        # Alocar nova memória
        block = RAMBlock(reason=reason, size_mb=mb, timestamp=time.time())
        self.ram_cache["blocks"].append(block)
        self.ram_cache["total_used"] += mb
        self.ram_cache["history"].append((time.time(), mb, reason))
        
        # Limitar histórico de blocos
        if len(self.ram_cache["blocks"]) > 50:
            oldest = self.ram_cache["blocks"].pop(0)
            self.ram_cache["total_used"] -= oldest.size_mb
    
    def ram_cleanup(self, aggressive: bool = False):
        """Limpa memória RAM"""
        if aggressive:
            # Limpeza agressiva
            self.ram_cache["total_used"] *= 0.3
            self.ram_cache["blocks"] = [b for b in self.ram_cache["blocks"] 
                                       if time.time() - b.timestamp < 30]
        else:
            # Limpeza normal
            self.ram_cache["total_used"] *= 0.7
            cutoff = time.time() - 60  # Mantém apenas blocos dos últimos 60s
            self.ram_cache["blocks"] = [b for b in self.ram_cache["blocks"] 
                                       if b.timestamp > cutoff]
    
    def ram_maintenance_loop(self):
        """Loop de manutenção da RAM"""
        while self.running:
            time.sleep(30)  # Verificar a cada 30 segundos
            if self.ram_usage_percent() > 70:
                self.ram_cleanup()
    
    def ram_usage_percent(self) -> float:
        """Retorna porcentagem de uso da RAM"""
        return round((self.ram_cache["total_used"] / self.RAM_TOTAL_MB) * 100, 1)
    
    # ============================================================
    # ======================= CPU ================================
    # ============================================================
    
    def cpu_load(self):
        """Calcula carga da CPU simulada"""
        base = random.uniform(0.1, 0.4)
        ram_factor = self.ram_cache["total_used"] / self.RAM_TOTAL_MB
        
        # Fatores adicionais
        message_factor = len(self.mensagens) * 0.02
        time_factor = math.sin(time.time() / 10) * 0.05
        
        load = base + ram_factor * 0.5 + message_factor + time_factor
        self.registradores["LOAD"] = round(min(1.0, load), 3)
    
    # ============================================================
    # ======================= EMOÇÕES ============================
    # ============================================================
    
    def atualizar_emocao(self, delta: float):
        """Atualiza estado emocional"""
        self.emocao["dopamine"] = max(0, min(1, self.emocao["dopamine"] + delta))
        self.emocao["last_update"] = time.time()
        
        # Registrar no histórico
        self.emocao["history"].append({
            "time": time.time(),
            "dopamine": self.emocao["dopamine"],
            "state": self.get_emotion_state()
        })
        
        # Determinar estado baseado no nível de dopamina
        d = self.emocao["dopamine"]
        if d < 0.2:
            self.emocao["state"] = EmotionState.LOW.value
        elif d < 0.4:
            self.emocao["state"] = EmotionState.CALM.value
        elif d < 0.7:
            self.emocao["state"] = EmotionState.CONTENT.value
        elif d < 0.9:
            self.emocao["state"] = EmotionState.SATISFIED.value
        else:
            self.emocao["state"] = EmotionState.EXCITED.value
        
        self.ram_allocate(2, "emotion_update")
    
    def get_emotion_state(self) -> str:
        """Retorna estado emocional atual"""
        return self.emocao["state"]
    
    def decay_emocao(self):
        """Decaimento natural da emoção"""
        self.atualizar_emocao(-0.0003)
    
    def get_emotion_color(self) -> Tuple[int, int, int]:
        """Retorna cor baseada no estado emocional"""
        state = self.emocao["state"]
        if state == EmotionState.LOW.value:
            return (150, 150, 200)
        elif state == EmotionState.CALM.value:
            return (100, 150, 255)
        elif state == EmotionState.CONTENT.value:
            return (100, 200, 100)
        elif state == EmotionState.SATISFIED.value:
            return (255, 200, 100)
        else:  # EXCITED
            return (255, 100, 150)
    
    # ============================================================
    # ======================= LUZ ================================
    # ============================================================
    
    def ligar_luz(self, intensidade: int = 100) -> str:
        """Liga a luz do quarto"""
        if not self.permissoes["light_control"]:
            return "Light control disabled."
        
        self.luz_quarto["ligada"] = True
        self.luz_quarto["intensidade"] = max(0, min(100, intensidade))
        self.atualizar_emocao(0.05)
        return f"Room light activated at {intensidade}% intensity."
    
    def desligar_luz(self) -> str:
        """Desliga a luz do quarto"""
        if not self.permissoes["light_control"]:
            return "Light control disabled."
        
        self.luz_quarto["ligada"] = False
        self.atualizar_emocao(0.02)
        return "Room light deactivated."
    
    def ajustar_luz(self, intensidade: int) -> str:
        """Ajusta intensidade da luz"""
        if not self.luz_quarto["ligada"]:
            return "Light is off. Turn it on first."
        
        intensidade = max(0, min(100, intensidade))
        self.luz_quarto["intensidade"] = intensidade
        return f"Light intensity adjusted to {intensidade}%."
    
    # ============================================================
    # ======================= HD ================================
    # ============================================================
    
    def hd_init(self):
        """Inicializa HD virtual"""
        if not os.path.exists(HD_FILE):
            base_structure = {
                "version": VERSION,
                "created": datetime.now().isoformat(),
                "logs": [],
                "stats": {
                    "total_commands": 0,
                    "total_dreams": 0,
                    "total_errors": 0
                }
            }
            with open(HD_FILE, "w") as f:
                json.dump(base_structure, f, indent=2)
    
    def hd_write(self, entry: Dict):
        """Escreve entrada no HD virtual"""
        if not self.permissoes["disk"]:
            return
        
        entry["timestamp"] = time.time()
        entry["datetime"] = datetime.now().isoformat()
        entry["hash"] = self.gerar_hash(entry)
        
        try:
            with open(HD_FILE, "r+") as f:
                data = json.load(f)
                data["logs"].append(entry)
                
                # Atualizar estatísticas
                if "cmd" in entry:
                    data["stats"]["total_commands"] += 1
                if "dream" in entry:
                    data["stats"]["total_dreams"] += 1
                if "error" in entry:
                    data["stats"]["total_errors"] += 1
                
                # Limitar logs
                if len(data["logs"]) > 1000:
                    data["logs"] = data["logs"][-500:]
                
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except Exception as e:
            print(f"Erro ao escrever no HD: {e}")
    
    def autosave_loop(self):
        """Loop para salvar estado automaticamente"""
        while self.running:
            time.sleep(60)  # Salvar a cada 60 segundos
            self.hd_write({
                "type": "autosave",
                "ram_usage": self.ram_cache["total_used"],
                "emotion": self.emocao.copy(),
                "state": self.registradores.copy()
            })
    
    # ============================================================
    # ======================= SONHOS =============================
    # ============================================================
    
    def sonhar(self):
        """Processa 'sonhos' do sistema"""
        if not self.permissoes["dreams"]:
            return
        
        agora = time.time()
        if agora - self.ultimo_sonho > self.config["dream_interval"]:
            sonho = random.choice(self.sonhos)
            self.falar(sonho)
            self.ram_allocate(16, "dream")
            
            self.hd_write({
                "type": "dream",
                "dream": sonho,
                "emotion_state": self.emocao["state"]
            })
            
            self.ultimo_sonho = agora
    
    # ============================================================
    # ======================= MENSAGENS ==========================
    # ============================================================
    
    def darvis_diz(self, texto: str):
        """Adiciona mensagem para exibição"""
        mensagem = Message(
            text=texto,
            timestamp=time.time(),
            duration=6.0
        )
        self.mensagens.append(mensagem)
        self.falar(texto)
    
    def limpar_mensagens_antigas(self):
        """Remove mensagens antigas"""
        current_time = time.time()
        self.mensagens = [m for m in self.mensagens 
                         if current_time - m.timestamp < m.duration]
    
    # ============================================================
    # ======================= IA ================================
    # ============================================================
    
    def processar_comando(self, cmd: str):
        """Processa comando do usuário"""
        current_time = time.time()
        self.last_command_time = current_time
        
        if not self.validar_comando(cmd):
            return
        
        cmd_original = cmd
        cmd = cmd.lower().strip()
        
        self.ram_allocate(24, f"command_{cmd[:20]}")
        self.registradores["COMMAND_COUNT"] += 1
        
        respostas = {
            "greeting": ["Hello Pedro.", "Systems secure.", "Online and ready."],
            "status": ["All systems nominal.", "Operating within parameters."],
            "light_on": ["Illumination activated.", "Lighting system engaged."],
            "light_off": ["Darkness restored.", "Lighting disengaged."]
        }
        
        try:
            if cmd in ["oi", "olá", "hello", "hi"]:
                resp = f"{random.choice(respostas['greeting'])} How can I assist?"
            
            elif "luz" in cmd or "light" in cmd:
                if any(word in cmd for word in ["ligar", "acender", "on", "activate"]):
                    if "intensidade" in cmd or "intensity" in cmd:
                        try:
                            parts = cmd.split()
                            for i, part in enumerate(parts):
                                if part.isdigit():
                                    intensity = int(part)
                                    resp = self.ligar_luz(intensity)
                                    break
                            else:
                                resp = self.ligar_luz()
                        except:
                            resp = self.ligar_luz()
                    else:
                        resp = self.ligar_luz()
                elif any(word in cmd for word in ["desligar", "apagar", "off", "deactivate"]):
                    resp = self.desligar_luz()
                else:
                    resp = f"Light is {'ON' if self.luz_quarto['ligada'] else 'OFF'}"
            
            elif "status" in cmd or "sistema" in cmd or "system" in cmd:
                cpu_load = self.registradores['LOAD']
                ram_percent = self.ram_usage_percent()
                resp = f"CPU: {cpu_load:.1%} | RAM: {ram_percent:.1f}% | Emotion: {self.emocao['state']}"
            
            elif "emoção" in cmd or "emotion" in cmd or "sentimento" in cmd:
                resp = f"Current emotional state: {self.emocao['state']} (Dopamine: {self.emocao['dopamine']:.2f})"
            
            elif "descansar" in cmd or "idle" in cmd:
                resp = "Entering idle mode. Systems will conserve energy."
                self.atualizar_emocao(0.1)
            
            elif "ajuda" in cmd or "help" in cmd or "comandos" in cmd:
                resp = "Available commands: status, luz ligar/desligar, descansar, emoção, desligar"
            
            elif cmd in ["desligar", "shutdown", "sair", "exit"]:
                self.darvis_diz("Initiating shutdown sequence. Goodbye.")
                self.shutdown()
                return
            
            else:
                resp = f"Command executed: {cmd_original}"
                self.atualizar_emocao(0.02)
            
            self.darvis_diz(resp)
            
            # Registrar no HD
            self.hd_write({
                "type": "command",
                "cmd": cmd_original,
                "response": resp,
                "ram_usage": self.ram_cache["total_used"],
                "emotion": self.emocao.copy(),
                "cpu_load": self.registradores["LOAD"]
            })
            
        except Exception as e:
            error_msg = f"Command processing error: {str(e)}"
            self.darvis_diz(error_msg)
            self.registradores["ERROR_COUNT"] += 1
            self.hd_write({
                "type": "error",
                "cmd": cmd_original,
                "error": str(e),
                "timestamp": time.time()
            })
    
    # ============================================================
    # ======================= INPUT ==============================
    # ============================================================
    
    def input_thread(self):
        """Thread para capturar entrada do usuário"""
        while self.running:
            try:
                user_input = input("\nVocê > ")
                if user_input.lower() == 'quit':
                    self.running = False
                    break
                self.input_queue.put(user_input)
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
            except:
                time.sleep(0.1)
    
    # ============================================================
    # ======================= GRÁFICOS ===========================
    # ============================================================
    
    def render_hud(self):
        """Renderiza o HUD do sistema"""
        # Fundo do HUD
        hud_rect = pygame.Rect(10, 10, 350, 190)
        self.draw_rounded_rect(self.screen, self.colors["hud_bg"], hud_rect, 8)
        
        # Título
        title = self.font_title.render("DARVIS SYSTEM STATUS", True, self.colors["accent"])
        self.screen.blit(title, (20, 15))
        
        # Informações do sistema
        info_y = 50
        info_lines = [
            f"• CPU Load: {self.registradores['LOAD']:.1%}",
            f"• RAM Usage: {int(self.ram_cache['total_used'])}/{self.RAM_TOTAL_MB} MB ({self.ram_usage_percent():.1f}%)",
            f"• Emotion: {self.emocao['state']}",
            f"• Dopamine: {self.emocao['dopamine']:.3f}",
            f"• Light: {'ON' if self.luz_quarto['ligada'] else 'OFF'}",
            f"• Uptime: {self.format_uptime()}",
            f"• Commands: {self.registradores['COMMAND_COUNT']}",
            f"• Safe Mode: {'ON' if self.safe_mode else 'OFF'}"
        ]
        
        for line in info_lines:
            text = self.font_mono.render(line, True, self.colors["text"])
            self.screen.blit(text, (20, info_y))
            info_y += 22
    
    def render_animation(self):
        """Renderiza animação central"""
        cx, cy = 450, 270
        self.angle += 0.02 * self.config["animation_speed"]
        
        # Partículas orbitais
        for i in range(6):
            angle_offset = self.angle + (i * math.pi / 3)
            radius = 90 + math.sin(self.angle * 2 + i) * 10
            x = int(cx + math.cos(angle_offset) * radius)
            y = int(cy + math.sin(angle_offset) * radius)
            
            # Cor baseada na emoção
            color = self.get_emotion_color()
            
            # Partícula com glow
            pygame.draw.circle(self.screen, color, (x, y), 8)
            pygame.draw.circle(self.screen, (*color, 100), (x, y), 15, 2)
        
        # Centro
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 5)
    
    def render_messages(self):
        """Renderiza mensagens do sistema"""
        y_pos = 500
        for msg in reversed(self.mensagens[-5:]):  # Últimas 5 mensagens
            if time.time() - msg.timestamp < msg.duration:
                # Calcular transparência baseada no tempo restante
                time_left = msg.duration - (time.time() - msg.timestamp)
                alpha = min(255, int(time_left * 50))
                
                # Renderizar com fundo
                text_surface = self.font_mono.render(msg.text, True, (255, 255, 200))
                bg_rect = pygame.Rect(10, y_pos - 2, text_surface.get_width() + 10, 22)
                
                # Fundo semi-transparente
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                bg_surface.fill((20, 30, 50, alpha // 2))
                self.screen.blit(bg_surface, bg_rect)
                
                self.screen.blit(text_surface, (15, y_pos))
                y_pos -= 24
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Desenha retângulo com cantos arredondados"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def format_uptime(self) -> str:
        """Formata tempo de atividade"""
        seconds = int(time.time() - self.registradores["UPTIME"])
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    # ============================================================
    # ======================= LOOP PRINCIPAL =====================
    # ============================================================
    
    def run(self):
        """Loop principal do aplicativo"""
        self.darvis_diz(f"System online. Version {VERSION}. Safe mode active.")
        
        while self.running:
            self.clock.tick(60)
            
            # Atualizar sistemas
            self.cpu_load()
            self.decay_emocao()
            self.limpar_mensagens_antidas()
            
            # Processar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.shutdown()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.shutdown()
                        return
            
            # Processar comandos da fila
            while not self.input_queue.empty():
                try:
                    cmd = self.input_queue.get_nowait()
                    self.processar_comando(cmd)
                except queue.Empty:
                    break
            
            # Sonhar se sistema ocioso
            if self.registradores["LOAD"] < 0.35 and self.permissoes["dreams"]:
                self.sonhar()
            
            # Renderização
            self.screen.fill(self.colors["bg"])
            
            self.render_animation()
            self.render_hud()
            self.render_messages()
            
            # FPS counter (debug)
            fps = self.clock.get_fps()
            fps_text = self.font_small.render(f"FPS: {fps:.1f}", True, (150, 150, 150))
            self.screen.blit(fps_text, (850, 10))
            
            pygame.display.flip()
    
    def shutdown(self):
        """Desliga o sistema de forma segura"""
        self.running = False
        self.registradores["STATE"] = SystemState.SHUTDOWN.value
        
        # Salvar estado final
        self.hd_write({
            "type": "shutdown",
            "final_state": self.registradores.copy(),
            "final_emotion": self.emocao.copy(),
            "total_runtime": time.time() - self.registradores["UPTIME"]
        })
        
        # Salvar configurações
        self.save_config()
        
        # Encerrar pygame
        pygame.quit()
        sys.exit()

# ============================================================
# ======================= EXECUÇÃO ===========================
# ============================================================

if __name__ == "__main__":
    try:
        darvis = DarvisAssistant()
        darvis.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
