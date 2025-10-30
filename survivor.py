class Survivor:
    def __init__(self, name="Unnamed",
                 str_val=1, agi_val=1, int_val=1, per_val=1,
                 chr_val=1, con_val=1, san_val=1):
        self.name = name

        # Attributes (1-10 range)
        self.attributes = {
            "STR": str_val,
            "AGI": agi_val,
            "INT": int_val,
            "PER": per_val,
            "CHR": chr_val,
            "CON": con_val,
            "SAN": san_val,
        }

        # Health
        self.base_max_hp = 40 # Base for all
        self.current_hp = self.calculate_max_hp()
        self.max_hp = self.calculate_max_hp() # CON * 10 bonus

        # Stress
        self.base_max_stress = 40 # Base for all
        self.current_stress = 0 # Starts at 0
        self.max_stress = self.calculate_max_stress() # SAN * 10 bonus

        # Status
        self.is_alive = True

        print(f"Survivor {self.name} created with attributes: {self.attributes}")
        print(f"Max HP: {self.max_hp}, Max Stress: {self.max_stress}")

    def calculate_max_hp(self):
        # Base 40 + CON * 10
        return self.base_max_hp + (self.attributes["CON"] * 10)

    def calculate_max_stress(self):
        # Base 40 + SAN * 10
        return self.base_max_stress + (self.attributes["SAN"] * 10)

    def take_damage(self, amount):
        if not self.is_alive:
            return

        # Apply CON damage reduction (5% per CON point, cap at 50% for CON 10)
        damage_reduction_percent = min(self.attributes["CON"] * 5, 50)
        actual_damage = amount * (1 - damage_reduction_percent / 100)

        self.current_hp -= actual_damage
        print(f"{self.name} took {actual_damage:.2f} damage. HP: {self.current_hp:.2f}")

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"{self.name} has been incapacitated or died.")
        elif self.current_hp > self.max_hp:
            self.current_hp = self.max_hp # Cap HP at max

    def gain_stress(self, amount):
        if not self.is_alive:
            return

        # Apply SAN stress mitigation (e.g., 5% per SAN point, cap at 50% for SAN 10)
        stress_mitigation_percent = min(self.attributes["SAN"] * 5, 50)
        actual_stress_gain = amount * (1 - stress_mitigation_percent / 100)

        self.current_stress += actual_stress_gain
        if self.current_stress > self.max_stress:
            self.current_stress = self.max_stress # Cap stress at max
            print(f"{self.name} is critically stressed!")
        print(f"{self.name} gained {actual_stress_gain:.2f} stress. Current Stress: {self.current_stress:.2f}")

    def reduce_stress(self, amount):
        if not self.is_alive:
            return
        self.current_stress -= amount
        if self.current_stress < 0:
            self.current_stress = 0
        print(f"{self.name} reduced stress by {amount}. Current Stress: {self.current_stress:.2f}")

    def heal(self, amount):
        if not self.is_alive:
            return
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        print(f"{self.name} healed {amount}. Current HP: {self.current_hp:.2f}")

# --- Example Usage (for testing your code) ---
if __name__ == "__main__":
    print("--- Creating Survivors ---")
    survivor1 = Survivor(name="Alice", str_val=5, agi_val=6, int_val=7, per_val=8, chr_val=5, con_val=7, san_val=6)
    survivor2 = Survivor(name="Bob", str_val=8, agi_val=4, int_val=3, per_val=5, chr_val=4, con_val=9, san_val=3)

    print("\n--- Testing Alice's Stats ---")
    print(f"Alice's CON: {survivor1.attributes['CON']}")
    print(f"Alice's SAN: {survivor1.attributes['SAN']}")
    print(f"Alice's Max HP: {survivor1.max_hp}")
    print(f"Alice's Max Stress: {survivor1.max_stress}")

    print("\n--- Alice takes damage ---")
    survivor1.take_damage(50) # Raw damage, will be reduced by CON
    survivor1.take_damage(100)
    survivor1.take_damage(500) # Should die

    print("\n--- Bob gains and reduces stress ---")
    survivor2.gain_stress(30)
    survivor2.gain_stress(40)
    survivor2.gain_stress(100) # Should hit max stress
    survivor2.reduce_stress(50)
    survivor2.heal(20) # Healing a non-injured Bob

    print("\n--- Final Status ---")
    print(f"Alice alive: {survivor1.is_alive}, HP: {survivor1.current_hp:.2f}, Stress: {survivor1.current_stress:.2f}")
    print(f"Bob alive: {survivor2.is_alive}, HP: {survivor2.current_hp:.2f}, Stress: {survivor2.current_stress:.2f}")