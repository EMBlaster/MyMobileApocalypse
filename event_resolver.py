import random
from typing import List, Dict, Any, Tuple, Union # ADDED Union
from survivor import Survivor
from utils import roll_d100, chance_check # Assuming chance_check uses roll_d100
from quests import Quest
from base_jobs import BaseJob
from skills import AVAILABLE_SKILLS # To look up skill effects

# --- Constants for Event Resolution ---
BASE_SUCCESS_CHANCE = 50 # Default 50% chance if no specific modifiers
SKILL_BONUS_PER_LEVEL = 5 # +5% success chance per skill level
ATTRIBUTE_BONUS_PER_POINT = 2 # +2% success chance per relevant attribute point
CRITICAL_SUCCESS_THRESHOLD = 95 # Roll >= 95 for critical success
CRITICAL_FAILURE_THRESHOLD = 5 # Roll <= 5 for critical failure

def calculate_action_success_chance(
    survivors: List[Survivor],
    action_obj: Union[Quest, BaseJob], # CHANGED
    action_type: str,
    node_danger_modifier: int = 0
) -> float:
    """
    Calculates the combined success chance for a group of survivors on an action.
    This is a simplified model for now and will be expanded.
    """
    base_chance = BASE_SUCCESS_CHANCE
    total_skill_bonus = 0
    total_attribute_bonus = 0

    # For each survivor, check relevant skills and attributes
    for survivor in survivors:
        if action_type == "quest":
            recommended = action_obj.recommended_skills
        elif action_type == "base_job":
            recommended = action_obj.recommended_skills
        else:
            recommended = {} # Fallback

        for skill_name, recommended_level in recommended.items():
            if skill_name in survivor.skills:
                # Add bonus based on actual skill level vs. recommended
                skill_level = survivor.skills[skill_name]
                total_skill_bonus += (skill_level * SKILL_BONUS_PER_LEVEL) # Each level gives a bonus

        # Add attribute bonus for primary attributes relevant to the action
        # This is a very basic example; will need refinement per skill/quest
        if "Perception" in recommended or "Scouting" in recommended:
            total_attribute_bonus += (survivor.attributes["PER"] * ATTRIBUTE_BONUS_PER_POINT)
        if "Small Arms" in recommended or "Melee Weaponry" in recommended:
            total_attribute_bonus += ((survivor.attributes["AGI"] + survivor.attributes["STR"]) / 2 * ATTRIBUTE_BONUS_PER_POINT)
        if "Mechanics" in recommended or "Electronics" in recommended:
            total_attribute_bonus += (survivor.attributes["INT"] * ATTRIBUTE_BONUS_PER_POINT)
        # Add more attribute relevance as skills become more detailed

    # Danger modifier: Higher danger reduces success chance
    danger_penalty = node_danger_modifier * 5 # e.g., danger 1 = -5%, danger 5 = -25%

    final_chance = base_chance + total_skill_bonus + total_attribute_bonus - danger_penalty
    return max(0, min(100, final_chance)) # Cap between 0 and 100

def resolve_action(
    survivors: List[Survivor],
    action_obj: Quest | BaseJob,
    action_type: str,
    game_instance: Any, # We'll pass the Game object to modify resources etc.
    node_danger: int = 0
) -> Tuple[bool, bool]: # Returns (was_successful, was_critical)
    """
    Resolves the outcome of a quest or base job for a group of survivors.
    """
    print(f"\n--- Resolving {action_obj.name} ({action_type}) ---")
    
    # Calculate success chance
    success_chance = calculate_action_success_chance(survivors, action_obj, action_type, node_danger)
    roll = roll_d100()
    
    is_successful = roll <= success_chance
    is_critical_success = is_successful and roll >= CRITICAL_SUCCESS_THRESHOLD
    is_critical_failure = not is_successful and roll <= CRITICAL_FAILURE_THRESHOLD # Roll low and still fail

    print(f"Chance: {success_chance}%, Roll: {roll}")
    if is_critical_success:
        print("CRITICAL SUCCESS!")
    elif is_successful:
        print("SUCCESS!")
    elif is_critical_failure:
        print("CRITICAL FAILURE!")
    else:
        print("FAILURE.")

    # --- Apply Rewards/Consequences ---
    if is_successful:
        # Apply rewards
        rewards = action_obj.rewards
        for res, qty in rewards.items():
            if res == "Experience":
                for s in survivors:
                    # Placeholder for actual EXP system
                    print(f"{s.name} gained {qty} Experience.")
            elif res.endswith("_crafted"): # Special handling for crafted items
                item_name = res.replace("_crafted", "")
                game_instance.add_resource(item_name, qty * (2 if is_critical_success else 1)) # Crit success for double
                print(f"  Crafted {qty * (2 if is_critical_success else 1)} {item_name}.")
            else:
                game_instance.add_resource(res, qty * (2 if is_critical_success else 1)) # Crit success for double
        print(f"  Rewards received: {rewards}")

        # Minor stress reduction for success
        for s in survivors:
            s.reduce_stress(10 * (2 if is_critical_success else 1))
    else: # Failure
        # Apply consequences
        consequences = action_obj.fail_consequences
        for effect, value in consequences.items():
            if effect == "HP_loss_per_survivor":
                for s in survivors:
                    s.take_damage(value * (2 if is_critical_failure else 1)) # Crit failure for double
            elif effect == "Stress_gain_per_survivor":
                for s in survivors:
                    s.gain_stress(value * (2 if is_critical_failure else 1)) # Crit failure for double
            elif effect == "Injury_chance" and value > 0:
                for s in survivors:
                    if chance_check(value * (2 if is_critical_failure else 1)): # Crit failure doubles chance
                        # Placeholder for specific injury types
                        print(f"  {s.name} suffered an injury!")
                        s.is_injured = True # Ensure flag is set

        print(f"  Consequences applied: {consequences}")
        
        # Stress gain for failure
        for s in survivors:
            s.gain_stress(15 * (2 if is_critical_failure else 1))


    # TODO: Implement more complex interactions for specific effects (e.g., unlocking upgrades)
    # TODO: Skill experience gain based on action type and success

    return is_successful, is_critical_success

# --- Example Usage (for testing the event resolver) ---
if __name__ == "__main__":
    from game import Game # Import Game for testing context
    from character_creator import create_new_survivor

    print("--- Setting up test scenario for Event Resolver ---")
    test_game = Game()
    test_game.add_resource("Food", 50)
    test_game.add_resource("Scrap", 50)
    test_game.add_resource("Ammunition", 10)

    # Create survivors
    survivor_a = create_new_survivor() # Use creator
    survivor_b = Survivor(name="Brenda", str_val=6, agi_val=7, int_val=5, per_val=8, chr_val=5, con_8=8, san_val=7)
    survivor_b.learn_skill("Scouting", 2) # Give Brenda a skill
    survivor_b.learn_skill("Small Arms", 1)
    test_game.add_survivor(survivor_a)
    test_game.add_survivor(survivor_b)

    # Get a test quest and base job
    scavenge_quest = AVAILABLE_QUESTS["ScavengeFood"]
    craft_ammo_job = AVAILABLE_BASE_JOBS["CraftAmmunition"]
    clear_infestation_quest = AVAILABLE_QUESTS["ClearInfestation"]

    # Test Quest Resolution
    print("\n--- Testing Scavenge Food Quest (with one survivor) ---")
    resolve_action([survivor_b], scavenge_quest, "quest", test_game, node_danger=2)
    test_game.display_game_state()
    print(f"Brenda's HP: {survivor_b.current_hp:.2f}, Stress: {survivor_b.current_stress:.2f}")

    # Test Base Job Resolution
    print("\n--- Testing Craft Ammunition Base Job (with one survivor) ---")
    resolve_action([survivor_b], craft_ammo_job, "base_job", test_game)
    test_game.display_game_state()
    print(f"Brenda's HP: {survivor_b.current_hp:.2f}, Stress: {survivor_b.current_stress:.2f}")

    # Test a more dangerous quest with multiple survivors
    print("\n--- Testing Clear Infestation Quest (with two survivors) ---")
    resolve_action([survivor_a, survivor_b], clear_infestation_quest, "quest", test_game, node_danger=4)
    test_game.display_game_state()
    print(f"Alpha's HP: {survivor_a.current_hp:.2f}, Stress: {survivor_a.current_stress:.2f}")
    print(f"Brenda's HP: {survivor_b.current_hp:.2f}, Stress: {survivor_b.current_stress:.2f}")