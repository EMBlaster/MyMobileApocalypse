from harness import run_combat_simulations
from survivor import Survivor
from zombies import Zombie, AVAILABLE_ZOMBIES


def _simple_survivors_factory():
    s1 = Survivor(name="Sim1", str_val=6, agi_val=5, int_val=4, per_val=4, chr_val=3, con_val=6, san_val=5)
    s1.learn_skill("Small Arms", 1)
    return [s1]


def _simple_zombies_factory():
    # create a single shambler instance
    bp = AVAILABLE_ZOMBIES["shambler"]
    z = Zombie(id="z1", name=bp.name, description=bp.description, base_hp=bp.base_hp, damage=bp.damage, speed=bp.speed, defense=bp.defense, traits=list(bp.traits))
    return [z]


def test_harness_runs_and_returns_metrics():
    metrics = run_combat_simulations(5, _simple_survivors_factory, _simple_zombies_factory, seed=42)
    assert "win_rate" in metrics
    assert 0.0 <= metrics["win_rate"] <= 1.0
    assert "avg_rounds" in metrics
    assert "avg_survivor_deaths" in metrics
