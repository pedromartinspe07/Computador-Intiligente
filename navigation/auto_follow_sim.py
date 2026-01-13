# navigation/auto_follow_sim.py

class AutoFollowSim:
    def __init__(self):
        self.target_position = (0, 0)
        self.armor_position = (10, 10)

    def update_target(self, x, y):
        self.target_position = (x, y)

    def follow(self):
        self.armor_position = self.target_position
        return f"Posição simulada da armadura: {self.armor_position}"
