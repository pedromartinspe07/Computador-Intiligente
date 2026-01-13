# armor/mark_4.py
from armor.mark_base import MarkBase

class MarkIV(MarkBase):
    def __init__(self):
        super().__init__("Mark IV", "4.0")
        self.energy_efficiency = 1.2
