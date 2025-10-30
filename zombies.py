from typing import List, Dict

class Zombie:
    """
    Represents a single zombie creature type.
    """
    def __init__(self, id: str, name: str, description: str,
                 base_hp: int, damage: int, speed: int, defense: int,
                 traits: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.base_hp = base_hp
        self.current_hp = base_hp # Start with full HP
        self.damage = damage
        self.speed = speed # Could affect initiative, dodge chance
        self.defense = defense # Affects chance to be hit
        self.traits = traits if traits is not None else [] # e.g., ["Fast", "Armored", "ExplodesOnDeath"]
        self.is_alive = True

    def __str__(self):
        return f"{self.name} (HP: {self.current_hp}/{self.base_hp})"

    def __repr__(self):
        return self.id

    def take_damage(self, amount: int):
        """Reduces zombie's current HP."""
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            print(f"{self.name} ({self.id}) was defeated!")
        else:
            print(f"{self.name} ({self.id}) took {amount} damage. Remaining HP: {self.current_hp}")


# --- Global Dictionary of Available Zombie Types ---
AVAILABLE_ZOMBIES = {
    "shambler": Zombie(
        id="shambler",
        name="Shambler",
        description="The most common type, slow and weak, but dangerous in numbers.",
        base_hp=30,
        damage=10,
        speed=1,
        defense=5,
        traits=[]
    ),
    "charger": Zombie(
        id="charger",
        name="Charger",
        description="Fast and aggressive, they try to close distance quickly.",
        base_hp=50,
        damage=15,
        speed=8,
        defense=10,
        traits=["Fast", "Aggressive"]
    ),
    "screamer": Zombie(
        id="screamer",
        name="Screamer",
        description="Emits piercing screams that attract more undead.",
        base_hp=25,
        damage=5,
        speed=4,
        defense=8,
        traits=["AttractsHorde", "WeakAttack"]
    ),
    "bloater": Zombie(
        id="bloater",
        name="Bloater",
        description="A bloated mass that explodes upon death, leaving a toxic cloud.",
        base_hp=70,
        damage=12,
        speed=2,
        defense=15,
        traits=["ExplodesOnDeath", "ToxicAura"]
    ),
    "mutant": Zombie( # Example of a "Plague Cloud infested zombie"
        id="mutant",
        name="Mutant Zombie",
        description="Twisted by the plague, stronger and resistant to some damage.",
        base_hp=80,
        damage=20,
        speed=6,
        defense=20,
        traits=["PlagueResistant", "StrongAttack", "Resilient"]
    ),
}

# --- Example Usage (for testing the Zombie class) ---
if __name__ == "__main__":
    print("--- Available Zombie Types ---")
    for z_id, zombie in AVAILABLE_ZOMBIES.items():
        print(f"\nID: {zombie.id}")
        print(f"Name: {zombie.name}")
        print(f"Description: {zombie.description}")
        print(f"HP: {zombie.current_hp}/{zombie.base_hp}")
        print(f"Damage: {zombie.damage}")
        print(f"Speed: {zombie.speed}")
        print(f"Defense: {zombie.defense}")
        print(f"Traits: {', '.join(zombie.traits) if zombie.traits else 'None'}")

    # Example of a zombie taking damage
    test_shambler = AVAILABLE_ZOMBIES["shambler"]
    print(f"\nTesting: {test_shambler.name} (HP: {test_shambler.current_hp})")
    test_shambler.take_damage(15)
    test_shambler.take_damage(20) # Should defeat it
    print(f"Is Shambler alive: {test_shambler.is_alive}")

    # Create a new instance for a fresh HP pool if needed for repeated testing
    new_charger = Zombie(
        id="charger_instance_1", name="Charger", description="Fast and aggressive",
        base_hp=50, damage=15, speed=8, defense=10, traits=["Fast", "Aggressive"]
    )
    print(f"\nTesting: {new_charger.name} (HP: {new_charger.current_hp})")
    new_charger.take_damage(20)