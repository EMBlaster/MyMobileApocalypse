"""
Multi-survivor headless playtest runner.
- Monkeypatches `decision_engine.make_decision` with an automatic policy that picks the highest-calculated chance.
- Sets up 3 survivors and assigns a combat quest (ClearInfestation) to exercise the combat engine.
- Runs a few follow-up days with base jobs.
"""
import sys
from pathlib import Path
import random

# Ensure repo root on path
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from game import Game
from io_handler import HeadlessIO
from survivor import Survivor
from quests import AVAILABLE_QUESTS
import decision_engine as de
from utils import roll_d100
from event_resolver import CRITICAL_SUCCESS_THRESHOLD, CRITICAL_FAILURE_THRESHOLD

# Monkeypatch make_decision to be automated
_original_make_decision = de.make_decision

def auto_make_decision(prompt, choices, game_instance, affected_survivors=None, node_danger=0, io_handler=None):
    """Automatic decision policy:
    - Filters choices by simple prerequisites (skills/attributes) similarly to original.
    - Uses calculate_choice_specific_chance to compute final chance for each available choice.
    - Picks the choice with the highest calculated chance (ties broken by first seen).
    - Rolls deterministically using a seeded RNG in game_instance (if present) or Python's random.
    - Returns (outcome_type, effects_dict) same contract as original.
    """
    if affected_survivors is None:
        affected_survivors = []

    # Build available choices list with calculated chance
    available = []
    for choice in choices:
        # Check basic prerequisites similar to decision_engine.make_decision
        can_choose = True
        if getattr(choice, 'prerequisites', None):
            # Skill prereqs
            if 'skill' in choice.prerequisites:
                has_required_skill = False
                for s in affected_survivors:
                    for sk, lvl in choice.prerequisites['skill'].items():
                        if s.skills.get(sk, 0) >= lvl:
                            has_required_skill = True
                            break
                    if has_required_skill:
                        break
                if not has_required_skill:
                    can_choose = False
            # Attribute prereqs
            if 'attribute' in choice.prerequisites:
                has_required_attr = False
                for s in affected_survivors:
                    for attr, val in choice.prerequisites['attribute'].items():
                        if s.attributes.get(attr, 0) >= val:
                            has_required_attr = True
                            break
                    if has_required_attr:
                        break
                if not has_required_attr:
                    can_choose = False
        if not can_choose:
            continue

        # Calculate final chance using existing helper
        try:
            final_chance = de.calculate_choice_specific_chance(choice, affected_survivors, game_instance)
        except Exception:
            final_chance = getattr(choice, 'base_success_chance', 50)
        available.append((choice, final_chance))

    if not available:
        # No viable choice; emulate failure
        return "failure", {"info": "No viable choices (auto policy)."}

    # Pick highest chance
    available.sort(key=lambda x: x[1], reverse=True)
    chosen, chance = available[0]

    # Determine roll source: try to use game_instance RNG if available, else use random module
    rng = getattr(game_instance, 'rng', None)
    if rng is None:
        rng = random

    roll = rng.randint(1, 100) if hasattr(rng, 'randint') else roll_d100()

    is_success = roll <= chance
    is_critical_success = is_success and roll >= CRITICAL_SUCCESS_THRESHOLD
    is_critical_failure = not is_success and roll <= CRITICAL_FAILURE_THRESHOLD

    if is_critical_success:
        outcome = 'critical_success'
        effects = chosen.effects_on_success
    elif is_success:
        outcome = 'success'
        effects = chosen.effects_on_success
    elif is_critical_failure:
        outcome = 'critical_failure'
        effects = chosen.effects_on_failure
    else:
        outcome = 'failure'
        effects = chosen.effects_on_failure

    # Optionally log via game_instance.io
    io = io_handler or (getattr(game_instance, 'io', None) if game_instance else None)
    if io:
        io.print(f"Auto-choice: '{chosen.text}' (Chance: {chance:.0f}%), Roll: {roll} -> {outcome}")

    return outcome, effects

# Patch it in
de.make_decision = auto_make_decision
# Also update the reference in the already-imported game module (it imported make_decision at module load time)
import game as _game_module
_game_module.make_decision = de.make_decision


def main(seed=2025):
    random.seed(seed)
    g = Game(start_day=1)
    # attach RNG for deterministic decisions
    g.rng = random.Random(seed)
    # use HeadlessIO and supply default responses (not used by auto policy but useful for other IO capture)
    g.io = HeadlessIO(responses=['1'] * 50)

    # Create survivors
    leader = Survivor(name='Leader', str_val=6, agi_val=6, int_val=5, per_val=5, chr_val=5, con_val=6, san_val=6)
    leader.learn_skill('Small Arms', 2)
    leader.learn_skill('Mechanics', 1)

    ally1 = Survivor(name='Maya', str_val=5, agi_val=6, int_val=4, per_val=6, chr_val=4, con_val=5, san_val=5)
    ally1.learn_skill('Small Arms', 1)

    ally2 = Survivor(name='Rex', str_val=7, agi_val=4, int_val=3, per_val=4, chr_val=3, con_val=7, san_val=4)
    ally2.learn_skill('Melee Weaponry', 1)

    g.add_survivor(leader)
    g.add_survivor(ally1)
    g.add_survivor(ally2)

    # Resources
    g.add_resource('Food', 30)
    g.add_resource('Water', 30)
    g.add_resource('Fuel', 30)
    g.add_resource('Scrap', 30)
    g.add_resource('Ammunition', 30)
    g.add_resource('ElectronicParts', 10)

    # Map
    g.generate_map(num_nodes=3)
    if g.game_map:
        g.set_current_node(list(g.game_map.keys())[0])

    # Monkeypatch assign_actions_for_day to set ClearInfestation on day1 with two survivors
    def assign_for_multi():
        g.assigned_actions = []
        # On day 1, assign ClearInfestation using Leader + Ally1
        if g.game_day == 1:
            quest = AVAILABLE_QUESTS.get('ClearInfestation')
            if quest:
                g.assigned_actions.append({'type': 'quest', 'action_obj': quest, 'survivors': [leader, ally1]})
        else:
            # For subsequent days, assign simple base jobs (ScrapSalvage) for all survivors
            from base_jobs import AVAILABLE_BASE_JOBS
            job = AVAILABLE_BASE_JOBS.get('ScrapSalvage')
            for s in g.get_assignable_survivors():
                g.assigned_actions.append({'type': 'base_job', 'action_obj': job, 'survivors': [s]})

    g.assign_actions_for_day = assign_for_multi

    # Run day 1 (quest + potential combat), then run 3 more days
    days = 4
    for _ in range(days):
        cont = g.run_day()
        if not cont:
            break

    # Print final state and IO log
    print('\n--- MULTI PLAYTEST FINAL STATE ---')
    g.display_game_state()

    print('\n--- HeadlessIO Log ---')
    for line in g.io.output:
        print(line)

    # Restore original decision function (cleanup)
    de.make_decision = _original_make_decision


if __name__ == '__main__':
    main(seed=42)
