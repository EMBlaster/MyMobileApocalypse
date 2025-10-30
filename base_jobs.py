class BaseJob:
    """
    Represents a job that survivors can perform while remaining at the mobile base.
    """
    def __init__(self, id: str, name: str, description: str,
                 recommended_skills: dict = None,
                 rewards: dict = None,
                 risk_level: int = 1, # e.g., 1-5, affects chance of base events
                 fail_consequences: dict = None):
        self.id = id
        self.name = name
        self.description = description
        # e.g., {"Mechanics": 1, "Perception": 1}
        self.recommended_skills = recommended_skills if recommended_skills is not None else {}
        # e.g., {"Scrap": 10, "Experience": 5, "Stress_reduction": 10}
        self.rewards = rewards if rewards is not None else {}
        self.risk_level = risk_level # Higher risk means higher chance of negative base events
        # e.g., {"Vehicle_damage": 5, "Stress_gain_per_survivor": 5}
        self.fail_consequences = fail_consequences if fail_consequences is not None else {}

    def __str__(self):
        return f"BaseJob(ID: {self.id}, Name: {self.name}, Risk: {self.risk_level})"

    def __repr__(self):
        return self.id

# --- Global Dictionary of Available Base Jobs ---
AVAILABLE_BASE_JOBS = {
    "ScrapSalvage": BaseJob(
        id="ScrapSalvage",
        name="Scrap Salvage",
        description="Scour the surrounding area for scrap metal and usable parts.",
        recommended_skills={"Perception": 1, "Strength": 1},
        rewards={"Scrap": 20, "Experience": 3},
        risk_level=2,
        fail_consequences={"Stress_gain_per_survivor": 5}
    ),
    "VehicleMaintenance": BaseJob(
        id="VehicleMaintenance",
        name="Vehicle Maintenance",
        description="Perform routine checks and minor repairs on the mobile base.",
        recommended_skills={"Mechanics": 1, "Intellect": 1},
        rewards={"Vehicle_HP_repair": 10, "Experience": 5}, # Will require a Vehicle class later
        risk_level=1,
        fail_consequences={"Scrap_loss": 5}
    ),
    "GuardDuty": BaseJob(
        id="GuardDuty",
        name="Guard Duty",
        description="Stand watch around the mobile base to deter threats.",
        recommended_skills={"Small Arms": 1, "Perception": 1},
        rewards={"Base_Defense_Bonus": 0.10, "Experience": 5}, # Placeholder for future defense system
        risk_level=3,
        fail_consequences={"Stress_gain_per_survivor": 10, "Base_Intrusion_chance": 0.05} # 5% chance of intrusion
    ),
    "RestAndRecover": BaseJob(
        id="RestAndRecover",
        name="Rest and Recover",
        description="Focus on rest to reduce stress and heal minor wounds.",
        recommended_skills={}, # No specific skills, anyone can rest
        rewards={"HP_recovery_flat": 10, "Stress_reduction_flat": 15, "Experience": 1},
        risk_level=0, # Very low risk
        fail_consequences={}
    ),
     "CraftAmmunition": BaseJob(
        id="CraftAmmunition",
        name="Craft Ammunition",
        description="Use available scrap to craft new ammunition.",
        recommended_skills={"Mechanics": 1},
        rewards={"Ammunition_crafted": 10, "Experience": 7},
        risk_level=1,
        fail_consequences={"Scrap_loss": 10, "Stress_gain_per_survivor": 5}
    ),
}

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Available Base Jobs ---")
    for job_id, job in AVAILABLE_BASE_JOBS.items():
        print(f"\nID: {job.id}")
        print(f"Name: {job.name}")
        print(f"Description: {job.description}")
        print(f"Risk Level: {job.risk_level}")
        print(f"Recommended Skills: {job.recommended_skills}")
        print(f"Rewards: {job.rewards}")
        print(f"Fail Consequences: {job.fail_consequences}")