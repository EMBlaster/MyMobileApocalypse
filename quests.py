class Quest:
    """
    Represents a quest or expedition that survivors can undertake.
    """
    def __init__(self, id: str, name: str, description: str,
                 required_survivors: int = 1, recommended_skills: dict = None,
                 danger_rating: int = 1, rewards: dict = None,
                 fail_consequences: dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.required_survivors = required_survivors # Minimum number of survivors needed
        # e.g., {"Scouting": 1, "Small Arms": 1}
        self.recommended_skills = recommended_skills if recommended_skills is not None else {}
        self.danger_rating = danger_rating # Higher means more risk, higher potential reward/consequence
        # e.g., {"Food": 50, "Scrap": 20, "Experience": 10}
        self.rewards = rewards if rewards is not None else {}
        # e.g., {"HP_loss_per_survivor": 10, "Stress_gain_per_survivor": 15}
        self.fail_consequences = fail_consequences if fail_consequences is not None else {}

    def __str__(self):
        return f"Quest(ID: {self.id}, Name: {self.name}, Danger: {self.danger_rating})"

    def __repr__(self):
        return self.id

# --- Global Dictionary of Available Quests ---
AVAILABLE_QUESTS = {
    "ScavengeFood": Quest(
        id="ScavengeFood",
        name="Scavenge for Food",
        description="Search an abandoned grocery store for vital food supplies.",
        required_survivors=1,
        recommended_skills={"Perception": 1, "Scouting": 1},
        danger_rating=2,
        rewards={"Food": 40, "Scrap": 10, "Experience": 5},
        fail_consequences={"HP_loss_per_survivor": 5, "Stress_gain_per_survivor": 10}
    ),
    "ClearInfestation": Quest(
        id="ClearInfestation",
        name="Clear Zombie Infestation",
        description="A building is swarming with zombies. Clear it out to secure a path or resources.",
        required_survivors=2,
        recommended_skills={"Small Arms": 1, "Melee Weaponry": 1, "Tactics": 1}, # Tactics will be a skill later
        danger_rating=4,
        rewards={"Ammunition": 20, "Scrap": 30, "Experience": 15},
        fail_consequences={"HP_loss_per_survivor": 20, "Stress_gain_per_survivor": 30, "Injury_chance": 0.5} # 50% chance of injury
    ),
    "FindMissingTrader": Quest(
        id="FindMissingTrader",
        name="Find Missing Trader",
        description="A friendly trader hasn't returned. Investigate their last known route.",
        required_survivors=1,
        recommended_skills={"Scouting": 1, "Charisma": 1},
        danger_rating=3,
        rewards={"Scrap": 50, "RandomItem": 1, "Experience": 10},
        fail_consequences={"Stress_gain_per_survivor": 20}
    ),
     "RepairLocalGenerator": Quest(
        id="RepairLocalGenerator",
        name="Repair Local Generator",
        description="A nearby generator could provide power if repaired. Requires mechanical skill.",
        required_survivors=1,
        recommended_skills={"Mechanics": 1, "Electronics": 1},
        danger_rating=3,
        rewards={"ElectronicParts": 10, "Scrap": 20, "Experience": 10, "UnlocksBaseUpgrade": "Generator"},
        fail_consequences={"HP_loss_per_survivor": 5, "Stress_gain_per_survivor": 10}
    ),
}

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Available Quests ---")
    for q_id, quest in AVAILABLE_QUESTS.items():
        print(f"\nID: {quest.id}")
        print(f"Name: {quest.name}")
        print(f"Description: {quest.description}")
        print(f"Danger: {quest.danger_rating}")
        print(f"Required Survivors: {quest.required_survivors}")
        print(f"Recommended Skills: {quest.recommended_skills}")
        print(f"Rewards: {quest.rewards}")
        print(f"Fail Consequences: {quest.fail_consequences}")