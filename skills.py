class Skill:
    """
    Represents a character skill with its prerequisites, effects by level, and point cost.
    """
    def __init__(self, name: str, description: str, attribute_prerequisites: dict,
                 level_effects: dict, cost_to_learn: int):
        self.name = name
        self.description = description
        # Attribute prerequisites for learning this skill (e.g., {"INT": 4})
        self.attribute_prerequisites = attribute_prerequisites
        # Effects that apply at different skill levels
        # e.g., {1: {"success_chance_bonus": 0.05, "unlocks_action": "Bandage"},
        #       2: {"success_chance_bonus": 0.10, "unlocks_action": "Suture"}}
        self.level_effects = level_effects
        # Cost to learn Level 1 of this skill during character creation
        self.cost_to_learn = cost_to_learn

    def __str__(self):
        return f"{self.name} (Cost: {self.cost_to_learn})"

    def __repr__(self):
        return self.name

# --- Global Dictionary of Available Skills ---
# This will hold all the skills that can be chosen during character creation
# and potentially learned/leveled up during gameplay.

# Skill level effects structure:
# "success_chance_bonus": float (e.g., 0.05 for +5% success chance)
# "damage_bonus": int/float
# "defense_bonus": int/float
# "resource_efficiency_mod": {"RESOURCE_NAME": percentage_change} (e.g., -0.1 for 10% less resource usage)
# "unlocks_action": str (e.g., "Suture Wound")
# "unlocks_crafting_recipe": str (e.g., "Basic Medkit")
# "unlocks_base_job": str (e.g., "Infirmary Duty")

AVAILABLE_SKILLS = {
    # INT-based Skills
    "Mechanics": Skill(
        name="Mechanics",
        description="Ability to repair and maintain vehicles and machinery.",
        attribute_prerequisites={"INT": 4},
        level_effects={
            1: {"success_chance_bonus": 0.05, "unlocks_action": "Repair Minor Damage", "unlocks_crafting_recipe": "Basic Tools"},
            2: {"success_chance_bonus": 0.10, "unlocks_action": "Craft Basic Vehicle Parts", "resource_efficiency_mod": {"Scrap": -0.05}},
            3: {"success_chance_bonus": 0.15, "unlocks_action": "Diagnose Complex Issues", "unlocks_crafting_recipe": "Reinforced Plating"},
            4: {"success_chance_bonus": 0.20, "resource_efficiency_mod": {"Scrap": -0.10}},
            5: {"success_chance_bonus": 0.25, "unlocks_action": "Engine Overhaul", "unlocks_crafting_recipe": "Advanced Vehicle Mod"},
        },
        cost_to_learn=4 # Cost for Level 1
    ),
    "First Aid": Skill(
        name="First Aid",
        description="Ability to treat injuries and illnesses.",
        attribute_prerequisites={"INT": 4},
        level_effects={
            1: {"success_chance_bonus": 0.05, "unlocks_action": "Bandage Wound", "resource_efficiency_mod": {"Bandage": -0.05}},
            2: {"success_chance_bonus": 0.10, "unlocks_action": "Suture Wound", "attribute_prerequisites": {"CHR": 2}}, # Level 2 requires CHR 2
            3: {"success_chance_bonus": 0.15, "unlocks_action": "Treat Illness", "unlocks_crafting_recipe": "Basic Medicine", "attribute_prerequisites": {"CHR": 3}}, # Level 3 requires CHR 3
            4: {"success_chance_bonus": 0.20, "healing_bonus": 0.10},
            5: {"success_chance_bonus": 0.25, "unlocks_action": "Advanced Surgery", "unlocks_crafting_recipe": "Advanced Medicine"},
        },
        cost_to_learn=4
    ),
    "Electronics": Skill(
        name="Electronics",
        description="Knowledge of electronic devices, repair, and crafting.",
        attribute_prerequisites={"INT": 4},
        level_effects={
            1: {"success_chance_bonus": 0.05, "unlocks_action": "Repair Simple Electronics"},
            2: {"success_chance_bonus": 0.10, "unlocks_crafting_recipe": "Basic Comms Device"},
            3: {"success_chance_bonus": 0.15, "unlocks_action": "Advanced Salvage"},
            4: {"success_chance_bonus": 0.20, "resource_efficiency_mod": {"ElectronicParts": -0.10}},
            5: {"success_chance_bonus": 0.25, "unlocks_crafting_recipe": "Cybernetic Implant"}, # Placeholder for future
        },
        cost_to_learn=4
    ),

    # AGI-based Skills
    "Driving": Skill(
        name="Driving",
        description="Proficiency in operating and navigating vehicles.",
        attribute_prerequisites={"AGI": 3},
        level_effects={
            1: {"success_chance_bonus": 0.05, "resource_efficiency_mod": {"Fuel": -0.05}},
            2: {"success_chance_bonus": 0.10, "unlocks_action": "Evasive Maneuver"},
            3: {"success_chance_bonus": 0.15, "event_chance_mod": {"VehicleDamage": -0.10}}, # 10% less chance of vehicle damage
            4: {"success_chance_bonus": 0.20, "resource_efficiency_mod": {"Fuel": -0.10}},
            5: {"success_chance_bonus": 0.25, "unlocks_action": "Ramming Speed"},
        },
        cost_to_learn=4
    ),
    "Small Arms": Skill(
        name="Small Arms",
        description="Proficiency with pistols, SMGs, and other small firearms.",
        attribute_prerequisites={"AGI": 4},
        level_effects={
            1: {"success_chance_bonus": 0.05, "damage_bonus": 1},
            2: {"success_chance_bonus": 0.10, "unlocks_action": "Double Tap"},
            3: {"success_chance_bonus": 0.15, "resource_efficiency_mod": {"Ammunition": -0.05}}, # 5% chance to not consume ammo
            4: {"success_chance_bonus": 0.20, "damage_bonus": 2},
            5: {"success_chance_bonus": 0.25, "unlocks_action": "Quick Reload"},
        },
        cost_to_learn=4
    ),

    # PER-based Skills
    "Scouting": Skill(
        name="Scouting",
        description="Ability to observe the environment, detect hazards, and find paths.",
        attribute_prerequisites={"PER": 4},
        level_effects={
            1: {"success_chance_bonus": 0.05, "event_chance_mod": {"Ambush": -0.05}}, # 5% less chance of ambush
            2: {"success_chance_bonus": 0.10, "unlocks_action": "Identify Zombie Types"},
            3: {"success_chance_bonus": 0.15, "resource_discovery_mod": 0.10}, # 10% more resources found
            4: {"success_chance_bonus": 0.20, "event_chance_mod": {"HazardSurprise": -0.10}}, # 10% less chance of surprise hazard
            5: {"success_chance_bonus": 0.25, "unlocks_action": "Optimal Route Planning"},
        },
        cost_to_learn=4
    ),

    # STR-based Skills
    "Melee Weaponry": Skill(
        name="Melee Weaponry",
        description="Proficiency with blunt and edged melee weapons.",
        attribute_prerequisites={"STR": 4},
        level_effects={
            1: {"success_chance_bonus": 0.05, "damage_bonus": 1},
            2: {"success_chance_bonus": 0.10, "unlocks_action": "Sweep Attack"},
            3: {"success_chance_bonus": 0.15, "event_chance_mod": {"WeaponBreak": -0.10}}, # 10% less chance of weapon breaking
            4: {"success_chance_bonus": 0.20, "damage_bonus": 2},
            5: {"success_chance_bonus": 0.25, "unlocks_action": "Weapon Maintenance"},
        },
        cost_to_learn=4
    ),
}

# --- Example Usage (for testing the Skill class) ---
if __name__ == "__main__":
    print("--- Available Skills ---")
    for name, skill in AVAILABLE_SKILLS.items():
        print(f"\n- {name}: {skill.description} (Cost: {skill.cost_to_learn} points)")
        print(f"  Prerequisites: {skill.attribute_prerequisites}")
        for level, effects in skill.level_effects.items():
            print(f"    Level {level} Effects: {effects}")

    # Example of accessing a skill
    mechanics_skill = AVAILABLE_SKILLS["Mechanics"]
    print(f"\nDetails for Mechanics skill: {mechanics_skill.description}")
    print(f"Level 1 success bonus: {mechanics_skill.level_effects.get(1, {}).get('success_chance_bonus')}")

    first_aid_lvl2_prereq = AVAILABLE_SKILLS["First Aid"].level_effects.get(2, {}).get('attribute_prerequisites')
    print(f"First Aid Level 2 prerequisite: {first_aid_lvl2_prereq}")