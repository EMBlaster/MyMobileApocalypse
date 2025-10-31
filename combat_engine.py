import random
import logging

logger = logging.getLogger(__name__)
from typing import List, Dict, Any, Tuple, Union # Make sure Union is imported here
from survivor import Survivor
from zombies import Zombie, AVAILABLE_ZOMBIES # Import Zombie class and predefined types
from utils import roll_dice, chance_check

# --- Combat Constants (can be adjusted later) ---
SURVIVOR_BASE_HIT_CHANCE = 70  # Base % chance for a survivor to hit a zombie
ZOMBIE_BASE_HIT_CHANCE = 50    # Base % chance for a zombie to hit a survivor
SKILL_HIT_BONUS_PER_LEVEL = 5  # % bonus to hit per relevant skill level
ATTRIBUTE_HIT_BONUS_PER_POINT = 2 # % bonus to hit per relevant attribute point
SURVIVOR_MELEE_DAMAGE_MULTIPLIER = 5 # Base damage multiplier for STR in melee
SURVIVOR_RANGED_DAMAGE_MULTIPLIER = 4 # Base damage multiplier for AGI in ranged
ZOMBIE_HP_PER_DANGER_LEVEL = 10 # Zombies gain HP based on node danger

def get_combat_stats(entity: Union[Survivor, Zombie]) -> dict:
    """Helper to get relevant combat stats for an entity."""
    if isinstance(entity, Survivor):
        return {
            "is_survivor": True,
            "hp": entity.current_hp,
            "max_hp": entity.max_hp,
            "str": entity.attributes["STR"],
            "agi": entity.attributes["AGI"],
            "per": entity.attributes["PER"],
            "con": entity.attributes["CON"],
            "skills": entity.skills,
            "traits": entity.traits,
            # Placeholder for weapon damage from inventory
            "weapon_damage": 10 + entity.attributes["STR"] * 2 # Simple placeholder
        }
    elif isinstance(entity, Zombie):
        return {
            "is_survivor": False,
            "hp": entity.current_hp,
            "max_hp": entity.base_hp,
            "damage": entity.damage,
            "speed": entity.speed,
            "defense": entity.defense,
            "traits": entity.traits
        }
    return {}

def calculate_survivor_hit_chance(attacker: Survivor, target: Zombie, environment_mods: dict) -> float:
    """Calculates the chance for a survivor to hit a zombie."""
    chance = SURVIVOR_BASE_HIT_CHANCE
    
    # Simple attribute/skill bonus for now
    # Assumes survivors prioritize relevant skills/attributes
    if attacker.skills.get("Small Arms", 0) > 0:
        chance += attacker.skills["Small Arms"] * SKILL_HIT_BONUS_PER_LEVEL
        chance += attacker.attributes["AGI"] * ATTRIBUTE_HIT_BONUS_PER_POINT
    elif attacker.skills.get("Melee Weaponry", 0) > 0:
        chance += attacker.skills["Melee Weaponry"] * SKILL_HIT_BONUS_PER_LEVEL
        chance += attacker.attributes["STR"] * ATTRIBUTE_HIT_BONUS_PER_POINT
    else: # Unskilled survivor relies on basic AGI/STR
        chance += (attacker.attributes["AGI"] + attacker.attributes["STR"]) / 2 * (ATTRIBUTE_HIT_BONUS_PER_POINT / 2)
    
    # Adjust for zombie defense
    chance -= target.defense * 0.5 # A higher defense reduces hit chance

    # Apply environment modifiers (e.g., fog reduces hit chance)
    if environment_mods.get("Fog", False):
        chance -= 15 # Example: 15% penalty in fog

    return max(0, min(100, chance))

def calculate_zombie_hit_chance(attacker: Zombie, target: Survivor, environment_mods: dict) -> float:
    """Calculates the chance for a zombie to hit a survivor."""
    chance = ZOMBIE_BASE_HIT_CHANCE
    
    # Adjust for survivor agility (dodging)
    chance -= target.attributes["AGI"] * 2 # Higher AGI means lower chance to be hit

    # Apply environment modifiers (e.g., fog for stealthy survivors)
    if environment_mods.get("Fog", False) and target.skills.get("Stealth", 0) > 0:
        chance -= 20 # Example: 20% penalty for zombies if survivor is stealthy in fog

    return max(0, min(100, chance))


def resolve_combat(
    survivors: List[Survivor],
    zombies: List[Zombie],
    game_instance: Any, # Game instance to interact with (resources, etc.)
    environment_mods: Dict[str, Any] = None, # e.g., {"Fog": True}
    node_danger: int = 1 # Danger level of the current node
) -> Dict[str, Any]:
    """
    Simulates automatic combat between a group of survivors and a group of zombies.
    Returns a summary of the combat outcome.
    """
    if environment_mods is None:
        environment_mods = {}

    print("\n--- COMBAT ENGAGED! ---")
    print(f"Survivors: {[s.name for s in survivors if s.is_alive]}")
    print(f"Zombies: {[z.name for z in zombies if z.is_alive]}")
    
    active_survivors = [s for s in survivors if s.is_alive]
    active_zombies = [z for z in zombies if z.is_alive]

    # Scale zombie HP based on node danger (making higher danger nodes tougher)
    for zombie in active_zombies:
        if node_danger > 1: # Only scale if danger is above base
            bonus_hp = (node_danger - 1) * ZOMBIE_HP_PER_DANGER_LEVEL
            zombie.base_hp += bonus_hp
            zombie.current_hp += bonus_hp
            print(f"  {zombie.name} gained {bonus_hp} bonus HP from Danger Level {node_danger}. Total HP: {zombie.current_hp}")


    combat_round = 0
    while active_survivors and active_zombies and combat_round < 100: # Max rounds to prevent infinite loop
        combat_round += 1
        print(f"\n--- Round {combat_round} ---")

        # --- Survivors Attack ---
        random.shuffle(active_survivors) # Randomize survivor attack order
        for attacker in active_survivors:
            if not attacker.is_alive or not active_zombies:
                continue

            target_zombie = random.choice(active_zombies) # Survivors target random active zombie

            print(f"  {attacker.name} attacks {target_zombie.name}...")
            hit_chance = calculate_survivor_hit_chance(attacker, target_zombie, environment_mods)
            
            if chance_check(hit_chance):
                damage_dealt = get_combat_stats(attacker)["weapon_damage"] # Use placeholder weapon damage
                
                # Critical hit chance (e.g., 10% chance for double damage)
                if chance_check(10): # Reusing utils.chance_check
                    damage_dealt *= 2
                    print(f"    CRITICAL HIT! {attacker.name} deals {damage_dealt} damage to {target_zombie.name}.")
                else:
                    print(f"    Hit! {attacker.name} deals {damage_dealt} damage to {target_zombie.name}.")
                
                target_zombie.take_damage(damage_dealt)
                if not target_zombie.is_alive:
                    active_zombies.remove(target_zombie)
                    print(f"    {target_zombie.name} defeated!")
            else:
                print(f"    {attacker.name} missed {target_zombie.name}.")

        if not active_zombies:
            break # All zombies defeated

        # --- Zombies Attack ---
        random.shuffle(active_zombies) # Randomize zombie attack order
        for attacker_zombie in active_zombies:
            if not attacker_zombie.is_alive or not active_survivors:
                continue
            
            target_survivor = random.choice(active_survivors) # Zombies target random active survivor

            print(f"  {attacker_zombie.name} attacks {target_survivor.name}...")
            hit_chance = calculate_zombie_hit_chance(attacker_zombie, target_survivor, environment_mods)
            
            if chance_check(hit_chance):
                damage_dealt = attacker_zombie.damage
                
                # Critical hit chance for zombies (e.g., 5% for double damage)
                if chance_check(5):
                    damage_dealt *= 2
                    print(f"    CRITICAL HIT! {attacker_zombie.name} deals {damage_dealt} damage to {target_survivor.name}.")
                else:
                    print(f"    Hit! {attacker_zombie.name} deals {damage_dealt} damage to {target_survivor.name}.")
                
                target_survivor.take_damage(damage_dealt)
                target_survivor.gain_stress(damage_dealt / 2) # Zombies also cause stress
                if not target_survivor.is_alive:
                    active_survivors.remove(target_survivor)
                    print(f"    {target_survivor.name} incapacitated!")
            else:
                print(f"    {attacker_zombie.name} missed {target_survivor.name}.")

        if not active_survivors:
            break # All survivors incapacitated


    # --- Combat Summary ---
    outcome_summary = {
        "survivors_remaining": len(active_survivors),
        "zombies_remaining": len(active_zombies),
        "total_rounds": combat_round,
        "victory": len(active_survivors) > 0 and len(active_zombies) == 0,
        "defeat": len(active_survivors) == 0 and len(active_zombies) > 0,
        "stalemate": len(active_survivors) > 0 and len(active_zombies) > 0 and combat_round >= 100
    }
    
    print("\n--- COMBAT ENDED ---")
    if outcome_summary["victory"]:
        print("VICTORY! All zombies defeated.")
    elif outcome_summary["defeat"]:
        print("DEFEAT! All active survivors incapacitated.")
    elif outcome_summary["stalemate"]:
        print("STALEMATE! Combat reached max rounds with no clear winner.")
    else:
        print("Combat ended prematurely (should not happen normally).")

    return outcome_summary


# --- Example Usage (for testing the combat engine) ---
if __name__ == "__main__":
    from game import Game # For game context
    from character_creator import create_new_survivor
    from zombies import AVAILABLE_ZOMBIES
    
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Setting up Combat Test Scenario ---")
    test_game = Game()

    # Create survivors
    survivor_fighter = Survivor(name="Brock", str_val=8, agi_val=6, int_val=4, per_val=5, chr_val=3, con_val=7, san_val=6)
    survivor_fighter.learn_skill("Melee Weaponry", 2)
    survivor_fighter.learn_skill("Endurance", 1) # Not used yet, but for future
    test_game.add_survivor(survivor_fighter)

    survivor_shooter = Survivor(name="Clara", str_val=4, agi_val=8, int_val=5, per_val=7, chr_val=4, con_val=5, san_val=7)
    survivor_shooter.learn_skill("Small Arms", 2)
    survivor_shooter.add_trait("Brave") # Not used yet, but for future
    test_game.add_survivor(survivor_shooter)

    # Create a horde of zombies (create fresh instances by extracting relevant attributes)
    zombie_horde = []
    
    # Helper to create a fresh zombie instance from the AVAILABLE_ZOMBIES blueprint
    def create_fresh_zombie_instance(zombie_type_id: str, instance_id: str):
        blueprint = AVAILABLE_ZOMBIES[zombie_type_id]
        return Zombie(
            id=instance_id,
            name=blueprint.name,
            description=blueprint.description,
            base_hp=blueprint.base_hp,
            damage=blueprint.damage,
            speed=blueprint.speed,
            defense=blueprint.defense,
            traits=list(blueprint.traits) # Copy traits list
        )

    zombie_horde.append(create_fresh_zombie_instance("shambler", "shambler_instance_1"))
    zombie_horde.append(create_fresh_zombie_instance("shambler", "shambler_instance_2"))
    zombie_horde.append(create_fresh_zombie_instance("charger", "charger_instance_1"))
    zombie_horde.append(create_fresh_zombie_instance("screamer", "screamer_instance_1"))


    # Run Combat
    combat_results = resolve_combat(
        survivors=test_game.survivors,
        zombies=zombie_horde,
        game_instance=test_game, # Pass the game instance
        environment_mods={"Fog": True}, # Test environment modifier
        node_danger=3 # Test danger level
    )

    logger.info("\n--- Final Combat Results Summary ---")
    logger.info(combat_results)
    for s in test_game.survivors:
        logger.info("%s: HP=%.2f/%.2f, Stress=%.2f/%.2f, Alive=%s", s.name, s.current_hp, s.max_hp, s.current_stress, s.max_stress, s.is_alive)
    for z in zombie_horde:
        logger.info("%s (%s): HP=%s/%s, Alive=%s", z.name, z.id, z.current_hp, z.base_hp, z.is_alive)