# armor/mark_5.py
from armor.mark_base import MarkBase

class MarkV(MarkBase):
    def __init__(self):
        super().__init__("Mark V", "5.0")
        self.deploy_time = 2.5  # segundos (simulado)
