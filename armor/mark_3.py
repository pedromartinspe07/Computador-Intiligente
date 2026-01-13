# armor/mark_3.py
from armor.mark_base import MarkBase

class MarkIII(MarkBase):
    def __init__(self):
        super().__init__("Mark III", "3.0")
        self.weapon_systems = ["Repulsor (simulado)"]
