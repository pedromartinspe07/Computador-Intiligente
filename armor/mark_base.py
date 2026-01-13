# armor/mark_base.py

class MarkBase:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.energy_level = 100.0
        self.integrity = 100.0
        self.active = False

    def activate(self):
        self.active = True
        return f"{self.name} ativada."

    def deactivate(self):
        self.active = False
        return f"{self.name} desativada."

    def consume_energy(self, amount):
        self.energy_level = max(0, self.energy_level - amount)

    def status(self):
        return {
            "Armadura": self.name,
            "Versão": self.version,
            "Energia (%)": self.energy_level,
            "Integridade (%)": self.integrity,
            "Ativa": self.active
        }
