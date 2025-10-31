import random
from typing import List, Dict, Any, Tuple, Union
import logging

logger = logging.getLogger(__name__)
from survivor import Survivor
from utils import roll_d100, chance_check
from quests import Quest
from base_jobs import BaseJob
from skills import AVAILABLE_SKILLS
from crafting import craft_item

# --- Constants for Event Resolution ---
BASE_SUCCESS_CHANCE = 50
SKILL_BONUS_PER_LEVEL = 5
ATTRIBUTE_BONUS_PER_POINT = 2
CRITICAL_SUCCESS_THRESHOLD = 95
CRITICAL_FAILURE_THRESHOLD = 5

def calculate_action_success_chance(
    survivors: List[Survivor],
    action_obj: Union[Quest, BaseJob],
    action_type: str,
    node_danger_modifier: int = 0
) -> float:
    """
    Calculates the combined success chance for a group of survivors on an action.
    """
    base_chance = BASE_SUCCESS_CHANCE
    total_skill_bonus = 0
    total_attribute_bonus = 0

    for survivor in survivors:
        if action_type == "quest":
            recommended = action_obj.recommended_skills
        elif action_type == "base_job":
            recommended = action_obj.recommended_skills
        else:
            recommended = {}

        for skill_name, recommended_level in recommended.items():
            if skill_name in survivor.skills:
                skill_level = survivor.skills[skill_name]
                total_skill_bonus += (skill_level * SKILL_BONUS_PER_LEVEL)

        if "Perception" in recommended or "Scouting" in recommended:
            total_attribute_bonus += (survivor.attributes["PER"] * ATTRIBUTE_BONUS_PER_POINT)
        if "Small Arms" in recommended or "Melee Weaponry" in recommended:
            total_attribute_bonus += ((survivor.attributes["AGI"] + survivor.attributes["STR"]) / 2 * ATTRIBUTE_BONUS_PER_POINT)
        if "Mechanics" in recommended or "Electronics" in recommended:
            total_attribute_bonus += (survivor.attributes["INT"] * ATTRIBUTE_BONUS_PER_POINT)

    danger_penalty = node_danger_modifier * 5
    final_chance = base_chance + total_skill_bonus + total_attribute_bonus - danger_penalty
    return max(0, min(100, final_chance))

def resolve_action(
    survivors: List[Survivor],
    action_obj: Union[Quest, BaseJob],
    action_type: str, # <--- THIS IS THE MISSING PARAMETER THAT CAUSED THE ERROR
    game_instance: Any,
    node_danger: int = 0
) -> Tuple[bool, bool]:
    """
    Resolves the outcome of a quest or base job for a group of survivors.
    """
    print(f"\n--- Resolving {action_obj.name} ({action_type}) ---")
    
    success_chance = calculate_action_success_chance(survivors, action_obj, action_type, node_danger)
    roll = roll_d100()
    
    is_successful = roll <= success_chance
    is_critical_success = is_successful and roll >= CRITICAL_SUCCESS_THRESHOLD
    is_critical_failure = not is_successful and roll <= CRITICAL_FAILURE_THRESHOLD

    print(f"Chance: {success_chance}%, Roll: {roll}")
    if is_critical_success:
        print("CRITICAL SUCCESS!")
    elif is_successful:
        print("SUCCESS!")
    elif is_critical_failure:
        print("CRITICAL FAILURE!")
    else:
        print("FAILURE.")

    if is_successful:
        rewards = action_obj.rewards
        for res, qty in rewards.items():
            if res == "Experience":
                for s in survivors:
                    print(f"{s.name} gained {qty} Experience.")
            elif res.endswith("_crafted"):
                # Map "Medkit_crafted" -> recipe id "Medkit"
                item_name = res.replace("_crafted", "")
                qty_final = qty * (2 if is_critical_success else 1)
                # If a survivor performed the base job, give the item to the first survivor; otherwise put into global resources
                target_survivor = survivors[0] if survivors else None
                craft_result = craft_item(game_instance, item_name, quantity=qty_final, survivor=target_survivor)
                if craft_result.get("success"):
                    if target_survivor:
                        print(f"  Crafted {craft_result.get('produced_qty')} {item_name} for {target_survivor.name}.")
                    else:
                        print(f"  Crafted {craft_result.get('produced_qty')} {item_name} into global storage.")
                else:
                    # Fall back to original behavior: if crafting failed due to insufficient resources, apply as resource if possible
                    if craft_result.get("consumed"):
                        # resources were consumed but crafting failed — this is a bad outcome; apply fail consequences if present
                        print(f"  Crafting of {item_name} failed after consuming resources.")
                    else:
                        game_instance.add_resource(item_name, qty_final)
                        print(f"  Insufficient resources for crafting {item_name}; added raw {item_name} as resource.")
            else:
                game_instance.add_resource(res, qty * (2 if is_critical_success else 1))
        print(f"  Rewards received: {rewards}")

        for s in survivors:
            s.reduce_stress(10 * (2 if is_critical_success else 1))
    else:
        consequences = action_obj.fail_consequences
        for effect, value in consequences.items():
            if effect == "HP_loss_per_survivor":
                for s in survivors:
                    s.take_damage(value * (2 if is_critical_failure else 1))
            elif effect == "Stress_gain_per_survivor":
                for s in survivors:
                    s.gain_stress(value * (2 if is_critical_failure else 1))
            elif effect == "Injury_chance" and value > 0:
                for s in survivors:
                    if chance_check(value * (2 if is_critical_failure else 1)):
                        print(f"  {s.name} suffered an injury!")
                        s.is_injured = True

        print(f"  Consequences applied: {consequences}")
        
        for s in survivors:
            s.gain_stress(15 * (2 if is_critical_failure else 1))

    return is_successful, is_critical_success

if __name__ == "__main__":
    # Quick demo / smoke-run for local manual testing.
    # Creates a single survivor and resolves a simple base job to show expected logs.
    logging.basicConfig(level=logging.INFO)
    class DummyAction:
        def __init__(self, name, recommended_skills=None, rewards=None, fail_consequences=None):
            self.name = name
            self.recommended_skills = recommended_skills if recommended_skills is not None else {}
            self.rewards = rewards if rewards is not None else {}
            self.fail_consequences = fail_consequences if fail_consequences is not None else {}

    class MockGame:
        def __init__(self):
            self.resources = {}

        def add_resource(self, name, qty):
            self.resources[name] = self.resources.get(name, 0) + qty
            logger.info("MockGame: added %s x %s. Total now: %s", qty, name, self.resources[name])
    logger.info("--- event_resolver demo ---")
    tester = Survivor(name="Demo", str_val=5, agi_val=5, int_val=6, per_val=4, chr_val=3, con_val=5, san_val=4)
    tester.learn_skill("Mechanics", 2)

    demo_action = DummyAction(
        name="RepairGenerator",
        recommended_skills={"Mechanics": 1},
        rewards={"Scrap": 15},
        fail_consequences={"HP_loss_per_survivor": 5, "Stress_gain_per_survivor": 10}
    )

    game = MockGame()
    resolve_action([tester], demo_action, "base_job", game, node_danger=0)
