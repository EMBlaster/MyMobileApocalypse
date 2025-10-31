"""
Headless playtest runner: creates a game, a test survivor, auto-assigns base jobs,
and runs the game for a fixed number of days without interactive prompts.
"""
import random
import sys
import os
from pathlib import Path

# Ensure repository root is on sys.path so top-level imports work when running this script
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from game import Game
from io_handler import HeadlessIO
from survivor import Survivor
from base_jobs import AVAILABLE_BASE_JOBS


def main(days=5, seed=12345):
    random.seed(seed)
    g = Game(start_day=1)
    # Use headless IO to avoid interactive prompts. Pre-seed responses to choose safe/default options when decisions occur.
    # '2' will generally pick the safe/low-risk choice in decision menus used across the game.
    g.io = HeadlessIO(responses=['2'] * 200)

    # Create a test survivor
    s = Survivor(name="PlaytestHero", str_val=6, agi_val=5, int_val=5, per_val=5, chr_val=4, con_val=6, san_val=6)
    s.learn_skill("Mechanics", 1)
    s.learn_skill("Small Arms", 1)
    g.add_survivor(s)

    # Add resources so travel and jobs are possible
    g.add_resource("Food", 20)
    g.add_resource("Water", 20)
    g.add_resource("Fuel", 20)
    g.add_resource("Scrap", 20)
    g.add_resource("Ammunition", 10)
    g.add_resource("ElectronicParts", 5)

    # Generate a small map and set current node
    g.generate_map(num_nodes=3)
    if g.game_map:
        first_node_id = list(g.game_map.keys())[0]
        g.set_current_node(first_node_id)

    # Replace assign_actions_for_day with an auto-assign that picks a base job per day
    def auto_assign():
        g.assigned_actions = []
        assignable = g.get_assignable_survivors()
        for survivor in assignable:
            # Alternate jobs by day parity
            job_id = "ScrapSalvage" if (g.game_day % 2 == 1) else "CraftMedkit"
            job = AVAILABLE_BASE_JOBS.get(job_id)
            if job:
                g.assigned_actions.append({"type": "base_job", "action_obj": job, "survivors": [survivor]})
    g.assign_actions_for_day = auto_assign

    # Run for N days
    for _ in range(days):
        cont = g.run_day()
        if not cont:
            break

    # Final state
    print("\n--- FINAL GAME STATE AFTER PLAYTEST ---")
    g.display_game_state()

    # Print headless IO log (if any prompts were captured)
    print("\n--- HeadlessIO Captured Output ---")
    for line in g.io.output:
        print(line)


if __name__ == '__main__':
    main(days=5, seed=42)
