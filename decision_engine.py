from typing import List, Dict, Any, Tuple
from survivor import Survivor
from utils import roll_d100, chance_check # Need chance_check, might need roll_d100 directly
from skills import AVAILABLE_SKILLS # To potentially check skill levels for prerequisites/bonuses
from event_resolver import CRITICAL_SUCCESS_THRESHOLD, CRITICAL_FAILURE_THRESHOLD


class Choice:
    """
    Represents a single decision option for the player.
    """
    def __init__(self, text: str, description: str, base_success_chance: float,
                 effects_on_success: dict = None, effects_on_failure: dict = None,
                 prerequisites: dict = None, known_consequences_text: str = ""):
        self.text = text # Short text displayed to player (e.g., "Fight")
        self.description = description # Longer explanation of the choice
        self.base_success_chance = base_success_chance # Base % chance for this specific choice
        # Dictionary of effects (e.g., {"resource_gain": {"Food": 10}, "hp_loss_per_survivor": 5})
        self.effects_on_success = effects_on_success if effects_on_success is not None else {}
        self.effects_on_failure = effects_on_failure if effects_on_failure is not None else {}
        # Prerequisites for this choice to even be available (e.g., {"skill": {"Scouting": 1}, "attribute": {"INT": 5}})
        self.prerequisites = prerequisites if prerequisites is not None else {}
        self.known_consequences_text = known_consequences_text # Text summary of known outcomes

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Choice('{self.text}', Chance: {self.base_success_chance}%)"


def calculate_choice_specific_chance(
    choice: Choice,
    survivors: List[Survivor],
    game_instance: Any # Pass game_instance if choices need to check global state (e.g., vehicle upgrades)
) -> float:
    """
    Calculates the actual success chance for a specific choice, factoring in survivor skills/attributes.
    """
    final_chance = choice.base_success_chance
    
    # Placeholder for detailed calculation logic
    # Iterate through survivors and apply bonuses from relevant skills/attributes
    for survivor in survivors:
        # Example: if a choice is related to "Ambush" and survivor has "Stealth" skill
        if "skill" in choice.prerequisites:
            for skill_name, req_level in choice.prerequisites["skill"].items():
                if skill_name in survivor.skills and survivor.skills[skill_name] >= req_level:
                    # Simple bonus: +5% per skill level above prerequisite (or just a flat bonus)
                    final_chance += (survivor.skills[skill_name] - req_level + 1) * 5 # +5% for having the skill, +5% for each level above
        
        # Example: if a choice needs high INT and survivor has it
        if "attribute" in choice.prerequisites:
            for attr_name, req_val in choice.prerequisites["attribute"].items():
                if survivor.attributes.get(attr_name, 0) >= req_val:
                    final_chance += (survivor.attributes[attr_name] - req_val + 1) * 2 # +2% for each attribute point above prerequisite
                    
        # TODO: Add trait effects, item effects, vehicle effects here later

    return max(0, min(100, final_chance)) # Cap between 0 and 100

def make_decision(
    prompt: str,
    choices: List[Choice],
    game_instance: Any, # Game instance to interact with (resources, survivors, etc.)
    affected_survivors: List[Survivor] = None, # Survivors directly involved in the decision
    node_danger: int = 0 # Contextual danger level
) -> Tuple[str, dict]: # Returns (outcome_type: "success"/"failure"/"critical_success"/"critical_failure", effects_applied)
    """
    Presents a decision prompt to the player and processes their chosen action.
    """
    if affected_survivors is None:
        affected_survivors = []

    print(f"\n--- DECISION POINT ---")
    print(f"PROMPT: {prompt}")

    available_choices = []
    for i, choice_obj in enumerate(choices):
        # Check prerequisites (basic for now, can expand)
        can_choose = True
        if "skill" in choice_obj.prerequisites:
            has_required_skill = False
            for s in affected_survivors:
                for skill_name, req_level in choice_obj.prerequisites["skill"].items():
                    if s.skills.get(skill_name, 0) >= req_level:
                        has_required_skill = True
                        break
                if has_required_skill:
                    break
            if not has_required_skill:
                can_choose = False
        
        if "attribute" in choice_obj.prerequisites:
            has_required_attribute = False
            for s in affected_survivors:
                for attr_name, req_val in choice_obj.prerequisites["attribute"].items():
                    if s.attributes.get(attr_name, 0) >= req_val:
                        has_required_attribute = True
                        break
                if has_required_attribute:
                    break
            if not has_required_attribute:
                can_choose = False

        if not can_choose:
            # print(f"  {i+1}. [LOCKED] {choice_obj.text} - {choice_obj.description} (Prerequisites not met)")
            continue # Don't display if prerequisites aren't met

        calculated_chance = calculate_choice_specific_chance(choice_obj, affected_survivors, game_instance)
        available_choices.append((i + 1, choice_obj, calculated_chance))
        print(f"  {i+1}. {choice_obj.text} ({calculated_chance:.0f}% chance) - {choice_obj.known_consequences_text}")

    if not available_choices:
        print("No viable choices available for this situation. Defaulting to 'Wait'.")
        # Handle default action or forced failure
        return "failure", {"info": "No viable choices, forced to wait/fail."}

    choice_map = {str(opt[0]): (opt[1], opt[2]) for opt in available_choices} # Map display number to (choice_obj, calculated_chance)

    while True:
        player_input = input(f"Enter your choice (1-{len(available_choices)}): ").strip()
        if player_input in choice_map:
            chosen_choice_obj, final_chance = choice_map[player_input]
            break
        else:
            print("Invalid choice. Please enter a valid number.")
            
    print(f"You chose: '{chosen_choice_obj.text}' (Calculated Chance: {final_chance:.0f}%)")

    # --- Resolve Outcome ---
    roll = roll_d100()
    print(f"Roll: {roll}")

    is_successful = roll <= final_chance
    is_critical_success = is_successful and roll >= CRITICAL_SUCCESS_THRESHOLD # Reusing thresholds from event_resolver
    is_critical_failure = not is_successful and roll <= CRITICAL_FAILURE_THRESHOLD # Reusing thresholds from event_resolver

    outcome_type = "failure"
    effects_to_apply = {}

    if is_critical_success:
        print("CRITICAL SUCCESS!")
        outcome_type = "critical_success"
        effects_to_apply = chosen_choice_obj.effects_on_success
        # Potentially add critical success bonus to effects_to_apply
    elif is_successful:
        print("SUCCESS!")
        outcome_type = "success"
        effects_to_apply = chosen_choice_obj.effects_on_success
    elif is_critical_failure:
        print("CRITICAL FAILURE!")
        outcome_type = "critical_failure"
        effects_to_apply = chosen_choice_obj.effects_on_failure
        # Potentially add critical failure penalty to effects_to_apply
    else:
        print("FAILURE.")
        outcome_type = "failure"
        effects_to_apply = chosen_choice_obj.effects_on_failure
    
    # Placeholder for actually applying effects
    # This will typically involve calling methods on game_instance and affected_survivors
    # For now, we'll just print them and return for the caller to handle.
    print(f"Outcome Effects: {effects_to_apply}")

    return outcome_type, effects_to_apply


# --- Example Usage (for testing the decision engine) ---
if __name__ == "__main__":
    from game import Game # Need Game context for some checks
    from character_creator import create_new_survivor

    print("--- Setting up test scenario for Decision Engine ---")
    test_game = Game()
    test_survivor1 = create_new_survivor() # Create a survivor
    test_survivor1.learn_skill("Scouting", 2) # Give a skill
    test_survivor1.attributes["INT"] = 7 # Boost an attribute
    test_game.add_survivor(test_survivor1)

    # Example Choices
    choice_fight = Choice(
        text="Fight Zombies",
        description="Engage the zombie horde directly.",
        base_success_chance=60,
        effects_on_success={"resource_gain": {"Scrap": 10}, "exp_gain": 15},
        effects_on_failure={"hp_loss_per_survivor": 10, "stress_gain_per_survivor": 20},
        known_consequences_text="Risk of injury, gain scrap."
    )
    
    choice_flee = Choice(
        text="Attempt to Flee",
        description="Try to disengage and escape the area.",
        base_success_chance=85,
        effects_on_success={"info": "Escaped successfully."},
        effects_on_failure={"stress_gain_per_survivor": 15, "info": "Failed to escape, more stressed."},
        prerequisites={"skill": {"Driving": 1}}, # Requires Driving skill for best chance (not implemented in calculator yet)
        known_consequences_text="Consumes time, risk of stress."
    )

    choice_ambush = Choice(
        text="Set Up Ambush",
        description="Prepare a trap and surprise the horde.",
        base_success_chance=50,
        effects_on_success={"info": "Ambush successful, combat advantage."},
        effects_on_failure={"hp_loss_per_survivor": 5, "info": "Ambush failed, disadvantage in combat."},
        prerequisites={"skill": {"Stealth": 1}, "attribute": {"PER": 5}},
        known_consequences_text="High risk, high reward. Requires Stealth and Perception."
    )

    choice_int_check = Choice(
        text="Analyze Situation",
        description="Use intellect to find a clever solution.",
        base_success_chance=70,
        effects_on_success={"info": "Found a weak spot."},
        effects_on_failure={"stress_gain_per_survivor": 5, "info": "Couldn't figure it out."},
        prerequisites={"attribute": {"INT": 6}},
        known_consequences_text="Requires high Intellect."
    )

    # --- Run some decisions ---
    print("\n--- Decision 1: Encountering Zombies ---")
    outcome, effects = make_decision(
        prompt="A small horde of zombies blocks your path. What do you do?",
        choices=[choice_fight, choice_flee, choice_ambush, choice_int_check],
        game_instance=test_game,
        affected_survivors=[test_survivor1],
        node_danger=3
    )
    print(f"Decision Outcome: {outcome}, Effects: {effects}")
    print(f"Survivor HP: {test_survivor1.current_hp:.2f}, Stress: {test_survivor1.current_stress:.2f}")

    # Test with no matching prereqs (flee and ambush will be effectively unavailable if driving/stealth not on survivor1)
    print("\n--- Decision 2: No obvious solution ---")
    test_survivor2 = Survivor(name="Clumsy", str_val=3, agi_val=3, int_val=3, per_val=3, chr_val=3, con_val=3, san_val=3)
    test_game.add_survivor(test_survivor2) # Add a new survivor without skills
    outcome, effects = make_decision(
        prompt="A locked door blocks your way. No obvious key.",
        choices=[
            Choice("Force Door", "Try to brute-force the door.", 60, {"resource_loss": {"Scrap": 5}}, {"hp_loss": 5}, {"attribute": {"STR": 6}}, "Requires high STR."),
            Choice("Pick Lock", "Attempt to pick the lock.", 70, {"resource_gain": {"ElectronicParts": 2}}, {"stress_gain": 10}, {"skill": {"Mechanics": 1}}, "Requires Mechanics skill.")
        ],
        game_instance=test_game,
        affected_survivors=[test_survivor2],
        node_danger=1
    )
    print(f"Decision Outcome: {outcome}, Effects: {effects}")