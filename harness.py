import random
from typing import Callable, Dict, Any, Optional


def run_combat_simulations(runs: int, survivors_factory: Callable[[], list], zombies_factory: Callable[[], list], seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Run `runs` simulated combats. survivors_factory returns a fresh list of Survivor objects per run.
    zombies_factory returns a fresh list of Zombie objects per run.
    Returns metrics: win_rate, avg_rounds, avg_survivor_deaths
    """
    from combat_engine import resolve_combat

    if seed is not None:
        random.seed(seed)

    wins = 0
    total_rounds = 0
    total_survivor_deaths = 0

    for i in range(runs):
        survivors = survivors_factory()
        zombies = zombies_factory()
        # Use a simple dummy game instance for resolve_combat
        class DummyGame:
            def add_resource(self, *args, **kwargs):
                pass

        res = resolve_combat(survivors=survivors, zombies=zombies, game_instance=DummyGame(), environment_mods={}, node_danger=1)
        if res.get("victory"):
            wins += 1
        total_rounds += res.get("total_rounds", 0)
        # survivors_remaining is survivors left; deaths = initial - remaining
        total_survivor_deaths += max(0, len(survivors) - res.get("survivors_remaining", 0))

    metrics = {
        "runs": runs,
        "win_rate": wins / runs if runs else 0.0,
        "avg_rounds": total_rounds / runs if runs else 0.0,
        "avg_survivor_deaths": total_survivor_deaths / runs if runs else 0.0,
    }
    return metrics
