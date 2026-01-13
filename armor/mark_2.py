# armor/mark_2.py
from armor.mark_base import MarkBase

class MarkII(MarkBase):
    def __init__(self):
        super().__init__("Mark II", "2.0")
        self.flight_stability = 0.7
