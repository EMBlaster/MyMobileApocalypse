import logging

logger = logging.getLogger(__name__)


class Trait:
    """
    Represents a character trait with its effects and point cost.
    """
    def __init__(self, name: str, description: str, point_cost: int, effects: dict, conflicts: list = None):
        self.name = name
        self.description = description
        self.point_cost = point_cost # Positive for benefits, negative for drawbacks (adds points)
        self.effects = effects # Dictionary of modifiers (e.g., {"STR_mod": 1, "food_consumption_mod": 0.2})
        self.conflicts = conflicts if conflicts is not None else [] # List of trait names this trait conflicts with

    def __str__(self):
        return f"{self.name} (Cost: {self.point_cost})"

    def __repr__(self):
        return self.name

# --- Global Dictionary of Available Traits ---
# This will hold all the traits that can be chosen during character creation
# and potentially gained/lost during gameplay.

# Trait effects structure:
# "attribute_mod": {"ATTR_NAME": value}
# "skill_mod": {"SKILL_NAME": value}
# "resource_consumption_mod": {"RESOURCE_NAME": percentage_change} (e.g., -0.2 for 20% less)
# "stress_gain_mod": percentage_change (e.g., -0.1 for 10% less stress gain)
# "sanity_gain_mod": percentage_change (e.g., 0.05 for 5% more SAN gain)
# "action_availability": {"ACTION_NAME": True/False} (e.g., {"Cannibalism": True})
# "interaction_mod": {"TRAIT_NAME_OF_ALLY": percentage_change}
# "event_chance_mod": {"EVENT_NAME": percentage_change}

AVAILABLE_TRAITS = {
    # Positive Traits (Cost points)
    "Brave": Trait(
        name="Brave",
        description="Less prone to stress and fear.",
        point_cost=4,
        effects={"stress_gain_mod": -0.20, "SAN_mod": 1}, # 20% less stress gain, +1 SAN
        conflicts=["Cowardly"]
    ),
    "Optimist": Trait(
        name="Optimist",
        description="Boosts morale and stress recovery.",
        point_cost=2,
        effects={"stress_reduction_mod": 0.10}, # 10% more stress reduction
        conflicts=["Pessimist"]
    ),
    "Strong": Trait(
        name="Strong",
        description="Physically powerful, can carry more and deal more melee damage.",
        point_cost=6,
        effects={"STR_mod": 2, "carrying_capacity_mod": 0.25}, # +2 STR, 25% more carrying capacity
        conflicts=["Weak"]
    ),
    "Thrifty": Trait(
        name="Thrifty",
        description="Consumes less food and water.",
        point_cost=3,
        effects={"resource_consumption_mod": {"Food": -0.15, "Water": -0.15}}, # 15% less food/water
        conflicts=["Glutton"]
    ),
    "Lucky": Trait(
        name="Lucky",
        description="Slightly increased chance for good outcomes and finding rare loot.",
        point_cost=5,
        effects={"event_chance_mod": {"GoodLoot": 0.10, "SkillCheckSuccess": 0.05}}, # 10% more chance for good loot, 5% more skill check success
        conflicts=["Unlucky"]
    ),

    # Negative Traits (Add points)
    "Cowardly": Trait(
        name="Cowardly",
        description="Prone to panic, gains more stress.",
        point_cost=-4, # Adds 4 points to pool
        effects={"stress_gain_mod": 0.25, "SAN_mod": -1}, # 25% more stress gain, -1 SAN
        conflicts=["Brave"]
    ),
    "Pessimist": Trait(
        name="Pessimist",
        description="Lowers morale and stress recovery.",
        point_cost=-2, # Adds 2 points to pool
        effects={"stress_reduction_mod": -0.05}, # 5% less stress reduction
        conflicts=["Optimist"]
    ),
    "Weak": Trait(
        name="Weak",
        description="Physically frail, carries less, deals less melee damage.",
        point_cost=-6, # Adds 6 points to pool
        effects={"STR_mod": -2, "carrying_capacity_mod": -0.20}, # -2 STR, 20% less carrying capacity
        conflicts=["Strong"]
    ),
    "Glutton": Trait(
        name="Glutton",
        description="Consumes more food and water.",
        point_cost=-3, # Adds 3 points to pool
        effects={"resource_consumption_mod": {"Food": 0.20, "Water": 0.20}}, # 20% more food/water
        conflicts=["Thrifty"]
    ),
    "Unlucky": Trait(
        name="Unlucky",
        description="Slightly increased chance for bad outcomes or finding broken items.",
        point_cost=-5, # Adds 5 points to pool
        effects={"event_chance_mod": {"BadEvent": 0.10, "SkillCheckFailure": 0.05}}, # 10% more chance for bad events, 5% more skill check failure
        conflicts=["Lucky"]
    ),
    "Pacifist": Trait(
        name="Pacifist",
        description="Refuses to engage in direct combat unless absolutely necessary. Gains stress from violence.",
        point_cost=-5,
        effects={"action_availability": {"DirectCombat": False}, "stress_gain_on_violence": 0.30},
        conflicts=["Aggressive"] # Example of a conflicting trait to be added later
    ),
    "Claustrophobic": Trait(
        name="Claustrophobic",
        description="Gains stress faster in enclosed spaces (e.g., inside vehicle for too long).",
        point_cost=-3,
        effects={"stress_gain_in_enclosed_spaces": 0.15},
        conflicts=[]
    )
}

# --- Example Usage (for testing your code) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Available Traits ---")
    for name, trait in AVAILABLE_TRAITS.items():
        logger.info("- %s: %s (Cost: %s points)", name, trait.description, trait.point_cost)
        if trait.conflicts:
            logger.info("  Conflicts with: %s", ', '.join(trait.conflicts))
        if trait.effects:
            logger.info("  Effects: %s", trait.effects)

    # Example of accessing a trait
    brave_trait = AVAILABLE_TRAITS["Brave"]
    logger.info("\nDetails for Brave trait: %s, STR mod: %s", brave_trait.description, brave_trait.effects.get('STR_mod', 'N/A'))