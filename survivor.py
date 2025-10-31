import math # Import math for rounding in damage/stress calculations
import logging

logger = logging.getLogger(__name__)

class Survivor:
    def __init__(self, name="Unnamed",
                     str_val=1, agi_val=1, int_val=1, per_val=1,
                     chr_val=1, con_val=1, san_val=1):
        self.name = name

        # Attributes (1-10 range) - Defaulting to 1 as per discussion
        self.attributes = {
            "STR": str_val,
            "AGI": agi_val,
            "INT": int_val,
            "PER": per_val,
            "CHR": chr_val,
            "CON": con_val,
            "SAN": san_val,
        }

        # Skills (New) - Dictionary mapping skill name to level
        self.skills: dict[str, int] = {}

        # Traits (New) - List of trait names (will be expanded with objects later)
        self.traits: list[str] = []

        # Individual Inventory (New) - Dictionary mapping item name to quantity
        self.inventory: dict[str, int] = {}

        # Health
        self.base_max_hp = 40
        self.max_hp = self.calculate_max_hp() # CON * 10 bonus
        self.current_hp = self.max_hp

        # Stress
        self.base_max_stress = 40
        self.max_stress = self.calculate_max_stress() # SAN * 10 bonus
        self.current_stress = 0 # Starts at 0

        # Status Flags
        self.is_alive = True
        self.is_injured = False # New: True if HP is below a certain threshold or has specific injury
        self.is_stressed = False # New: True if Stress is above a certain threshold

        print(f"Survivor {self.name} created with attributes: {self.attributes}")
        print(f"Max HP: {self.max_hp}, Max Stress: {self.max_stress}")

    def calculate_max_hp(self):
        # Base 40 + CON * 10
        return self.base_max_hp + (self.attributes["CON"] * 10)

    def calculate_max_stress(self):
        # Base 40 + SAN * 10
        return self.base_max_stress + (self.attributes["SAN"] * 10)

    def take_damage(self, amount: float):
        if not self.is_alive:
            print(f"{self.name} is already incapacitated.")
            return

        # Apply CON damage reduction (5% per CON point, cap at 50% for CON 10)
        damage_reduction_percent = min(self.attributes["CON"] * 5, 50)
        actual_damage = amount * (1 - damage_reduction_percent / 100)
        actual_damage = math.ceil(actual_damage) # Round up damage

        self.current_hp -= actual_damage
        print(f"{self.name} took {actual_damage} damage. HP: {self.current_hp:.2f}/{self.max_hp:.2f}")

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            self.is_injured = True # Definitely injured if dead/incapacitated
            print(f"{self.name} has been incapacitated or died.")
        elif self.current_hp < self.max_hp * 0.5: # Example threshold for being injured
            self.is_injured = True
            print(f"{self.name} is injured!")
        else:
            self.is_injured = False

    def gain_stress(self, amount: float):
        if not self.is_alive:
            print(f"{self.name} is incapacitated, cannot gain stress.")
            return

        # Apply SAN stress mitigation (e.g., 5% per SAN point, cap at 50% for SAN 10)
        stress_mitigation_percent = min(self.attributes["SAN"] * 5, 50)
        actual_stress_gain = amount * (1 - stress_mitigation_percent / 100)
        actual_stress_gain = math.ceil(actual_stress_gain) # Round up stress gain

        self.current_stress += actual_stress_gain
        if self.current_stress > self.max_stress:
            self.current_stress = self.max_stress # Cap stress at max
            self.is_stressed = True # New: Mark as stressed if at max
            print(f"{self.name} is critically stressed!")
        elif self.current_stress > self.max_stress * 0.75: # Example threshold for being stressed
            self.is_stressed = True
            print(f"{self.name} is feeling highly stressed.")
        else:
            self.is_stressed = False

        print(f"{self.name} gained {actual_stress_gain} stress. Current Stress: {self.current_stress:.2f}/{self.max_stress:.2f}")

    def reduce_stress(self, amount: float):
        if not self.is_alive:
            return
        self.current_stress -= amount
        if self.current_stress < 0:
            self.current_stress = 0
        if self.current_stress <= self.max_stress * 0.75: # Below stress threshold
            self.is_stressed = False
        print(f"{self.name} reduced stress by {amount}. Current Stress: {self.current_stress:.2f}/{self.max_stress:.2f}")

    def heal(self, amount: float):
        if not self.is_alive:
            print(f"{self.name} is incapacitated, cannot heal normally.")
            return
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        if self.current_hp >= self.max_hp * 0.5: # Above injured threshold
            self.is_injured = False
        print(f"{self.name} healed {amount}. Current HP: {self.current_hp:.2f}/{self.max_hp:.2f}")

    # New: Methods for skills, traits, and inventory
    def learn_skill(self, skill_name: str, level: int = 1):
        """Adds or updates a skill for the survivor."""
        if level < 0:
            raise ValueError("Skill level cannot be negative.")
        self.skills[skill_name] = level
        print(f"{self.name} learned/updated skill '{skill_name}' to level {level}.")

    def add_trait(self, trait_name: str):
        """Adds a trait to the survivor."""
        if trait_name not in self.traits:
            self.traits.append(trait_name)
            print(f"{self.name} gained trait '{trait_name}'.")
        else:
            print(f"{self.name} already has trait '{trait_name}'.")

    def remove_trait(self, trait_name: str):
        """Removes a trait from the survivor."""
        if trait_name in self.traits:
            self.traits.remove(trait_name)
            print(f"{self.name} lost trait '{trait_name}'.")
        else:
            print(f"{self.name} does not have trait '{trait_name}'.")

    def add_item_to_inventory(self, item_name: str, quantity: int = 1):
        """Adds an item to the survivor's individual inventory."""
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        self.inventory[item_name] = self.inventory.get(item_name, 0) + quantity
        print(f"{self.name} added {quantity} of '{item_name}' to inventory. Total: {self.inventory[item_name]}")

    def remove_item_from_inventory(self, item_name: str, quantity: int = 1) -> bool:
        """Removes an item from the survivor's inventory, if available."""
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        if self.inventory.get(item_name, 0) >= quantity:
            self.inventory[item_name] -= quantity
            if self.inventory[item_name] <= 0:
                del self.inventory[item_name] # Remove if quantity reaches zero
            print(f"{self.name} removed {quantity} of '{item_name}' from inventory. Remaining: {self.inventory.get(item_name, 0)}")
            return True
        else:
            print(f"{self.name} does not have {quantity} of '{item_name}'. Current: {self.inventory.get(item_name, 0)}")
            return False

    # --- Serialization for save/load ---
    def to_dict(self) -> dict:
        """Serialize the survivor to a plain dict for JSON storage."""
        return {
            "name": self.name,
            "attributes": dict(self.attributes),
            "skills": dict(self.skills),
            "traits": list(self.traits),
            "inventory": dict(self.inventory),
            "base_max_hp": self.base_max_hp,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "base_max_stress": self.base_max_stress,
            "max_stress": self.max_stress,
            "current_stress": self.current_stress,
            "is_alive": self.is_alive,
            "is_injured": self.is_injured,
            "is_stressed": self.is_stressed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Survivor":
        """Create a Survivor instance from a serialized dict."""
        s = cls(name=data.get("name", "Unnamed"),
                str_val=data.get("attributes", {}).get("STR", 1),
                agi_val=data.get("attributes", {}).get("AGI", 1),
                int_val=data.get("attributes", {}).get("INT", 1),
                per_val=data.get("attributes", {}).get("PER", 1),
                chr_val=data.get("attributes", {}).get("CHR", 1),
                con_val=data.get("attributes", {}).get("CON", 1),
                san_val=data.get("attributes", {}).get("SAN", 1))

        # Restore other fields
        s.skills = dict(data.get("skills", {}))
        s.traits = list(data.get("traits", []))
        s.inventory = dict(data.get("inventory", {}))
        s.base_max_hp = data.get("base_max_hp", s.base_max_hp)
        s.max_hp = data.get("max_hp", s.max_hp)
        s.current_hp = data.get("current_hp", s.current_hp)
        s.base_max_stress = data.get("base_max_stress", s.base_max_stress)
        s.max_stress = data.get("max_stress", s.max_stress)
        s.current_stress = data.get("current_stress", s.current_stress)
        s.is_alive = data.get("is_alive", s.is_alive)
        s.is_injured = data.get("is_injured", s.is_injured)
        s.is_stressed = data.get("is_stressed", s.is_stressed)
        return s

# --- Example Usage (for testing your code) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Creating Survivors ---")
    survivor_alice = Survivor(name="Alice", str_val=5, agi_val=6, int_val=7, per_val=8, chr_val=5, con_val=7, san_val=6)
    survivor_bob = Survivor(name="Bob", str_val=8, agi_val=4, int_val=3, per_val=5, chr_val=4, con_val=9, san_val=3)

    logger.info("--- Testing Alice's Skills, Traits, Inventory ---")
    survivor_alice.learn_skill("Mechanics", 1)
    survivor_alice.learn_skill("Driving", 2)
    survivor_alice.add_trait("Optimist")
    survivor_alice.add_trait("Brave")
    survivor_alice.add_item_to_inventory("Bandage", 3)
    survivor_alice.add_item_to_inventory("Pistol", 1)

    logger.info("Alice's skills: %s", survivor_alice.skills)
    logger.info("Alice's traits: %s", survivor_alice.traits)
    logger.info("Alice's inventory: %s", survivor_alice.inventory)
    survivor_alice.remove_item_from_inventory("Bandage", 1)
    survivor_alice.remove_item_from_inventory("NonExistentItem")

    logger.info("--- Testing Bob's HP/Stress thresholds ---")
    logger.info("Bob's HP: %s/%s, Is Injured: %s", survivor_bob.current_hp, survivor_bob.max_hp, survivor_bob.is_injured)
    survivor_bob.take_damage(50) # Should make Bob injured (CON 9, so good reduction)
    logger.info("Bob's HP: %s/%s, Is Injured: %s", survivor_bob.current_hp, survivor_bob.max_hp, survivor_bob.is_injured)
    survivor_bob.heal(30)
    logger.info("Bob's HP: %s/%s, Is Injured: %s", survivor_bob.current_hp, survivor_bob.max_hp, survivor_bob.is_injured)

    logger.info("Bob's Stress: %s/%s, Is Stressed: %s", survivor_bob.current_stress, survivor_bob.max_stress, survivor_bob.is_stressed)
    survivor_bob.gain_stress(100) # Should make Bob highly stressed (SAN 3, so not much reduction)
    logger.info("Bob's Stress: %s/%s, Is Stressed: %s", survivor_bob.current_stress, survivor_bob.max_stress, survivor_bob.is_stressed)
    survivor_bob.reduce_stress(50)
    logger.info("Bob's Stress: %s/%s, Is Stressed: %s", survivor_bob.current_stress, survivor_bob.max_stress, survivor_bob.is_stressed)

    logger.info("--- Final Status ---")
    logger.info("Alice alive: %s, HP: %.2f, Stress: %.2f, Injured: %s, Stressed: %s", survivor_alice.is_alive, survivor_alice.current_hp, survivor_alice.current_stress, survivor_alice.is_injured, survivor_alice.is_stressed)
    logger.info("Bob alive: %s, HP: %.2f, Stress: %.2f, Injured: %s, Stressed: %s", survivor_bob.is_alive, survivor_bob.current_hp, survivor_bob.current_stress, survivor_bob.is_injured, survivor_bob.is_stressed)