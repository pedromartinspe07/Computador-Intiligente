# energy/arc_reactor_sim.py

class ArcReactorSim:
    def __init__(self):
        self.output = 100.0
        self.stability = 1.0

    def accelerate_particles(self):
        self.output += 10
        self.stability -= 0.05

    def decelerate_particles(self):
        self.output -= 5
        self.stability += 0.03

    def status(self):
        return {
            "Energia Gerada": self.output,
            "Estabilidade": round(self.stability, 2)
        }
