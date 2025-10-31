from typing import Dict


class Item:
    def __init__(self, id: str, name: str, description: str, stackable: bool = True):
        self.id = id
        self.name = name
        self.description = description
        self.stackable = stackable

    def __repr__(self):
        return f"Item({self.id}, {self.name})"


# Simple item registry
ITEMS: Dict[str, Item] = {
    "Medkit": Item(id="Medkit", name="Medkit", description="Restores HP when used.", stackable=True),
    "Bandage": Item(id="Bandage", name="Bandage", description="Basic wound dressing.", stackable=True),
    "Ammo": Item(id="Ammo", name="Ammunition", description="Ammunition for small arms.", stackable=True),
}


# Crafting recipes: recipe_id -> dict
# Each recipe defines required global resources and produced items (to survivor inventory or global_resources)
RECIPES = {
    "Medkit": {
        "requires": {"Scrap": 5, "ElectronicParts": 2},
        "produces": {"item": "Medkit", "quantity": 1}
    },
    "Bandage": {
        "requires": {"Scrap": 1},
        "produces": {"item": "Bandage", "quantity": 1}
    },
    "Ammo": {
        "requires": {"Scrap": 3},
        "produces": {"resource": "Ammunition", "quantity": 5}
    }
}

# Additional recipes
RECIPES["AdvancedMedkit"] = {
    "requires": {"Scrap": 8, "ElectronicParts": 4},
    "produces": {"item": "Medkit", "quantity": 2}
}

RECIPES["RepairKit"] = {
    "requires": {"Scrap": 6, "ElectronicParts": 1},
    "produces": {"item": "RepairKit", "quantity": 1}
}

# Ensure ITEMS registry contains any produced items not already declared
if "RepairKit" not in ITEMS:
    from typing import Dict
    ITEMS["RepairKit"] = Item(id="RepairKit", name="Repair Kit", description="Used for repairing machinery.")
    if "Pistol" not in ITEMS:
        ITEMS["Pistol"] = Item(id="Pistol", name="Rusty Pistol", description="A basic sidearm.")

    # Alias recipe keys for convenience: map produced resource names to a recipe
    RECIPES["Ammunition"] = RECIPES.get("Ammo")
    # Weapon recipes
    RECIPES["Pistol"] = {
        "requires": {"Scrap": 10, "ElectronicParts": 4},
        "produces": {"item": "Pistol", "quantity": 1},
        "base_success_chance": 0.8
    }

    # Advanced ammo crafting (larger batch)
    RECIPES["AmmoBulk"] = {
        "requires": {"Scrap": 10},
        "produces": {"resource": "Ammunition", "quantity": 25},
        "base_success_chance": 0.95
    }
