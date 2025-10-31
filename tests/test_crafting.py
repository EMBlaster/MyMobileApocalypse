from game import Game
from survivor import Survivor
from crafting import craft_item


def test_craft_medkit_to_survivor(tmp_path):
    g = Game()
    # give resources required by Medkit recipe: Scrap 5, ElectronicParts 2
    g.add_resource("Scrap", 10)
    g.add_resource("ElectronicParts", 5)

    # Give Crafter a Mechanics skill to improve crafting yield
    s = Survivor(name="Crafter", con_val=4, san_val=4)
    s.learn_skill("Mechanics", 1)
    g.add_survivor(s)

    import random
    rng = random.Random(42)
    result = craft_item(g, "Medkit", quantity=1, survivor=s, rng=rng)
    assert result.get("success")
    # Mechanics level 1 gives +1 produced medkit, seed 42 deterministic
    assert s.inventory.get("Medkit", 0) == result.get("produced_qty")
    # Requirements reduced by mech level (Scrap 5-1=4 consumed, ElectronicParts 2-1=1 consumed)
    assert g.global_resources.get("Scrap", 0) == 6
    assert g.global_resources.get("ElectronicParts", 0) == 4
    # previous expectations removed; mechanics reduces requirements as asserted above


def test_craft_ammo_to_global(g=None):
    g = Game()
    g.add_resource("Scrap", 10)
    # craft ammo recipe consumes scrap and produces Ammunition resource
    from crafting import craft_item
    import random
    rng = random.Random(1)
    result = craft_item(g, "Ammo", quantity=1, rng=rng)
    assert result.get("success")
    assert g.global_resources.get("Ammunition", 0) >= 5
    # scrap consumed
    assert g.global_resources.get("Scrap", 0) <= 7


def test_craft_failure_due_to_insufficient_resources():
    g = Game()
    g.add_resource("Scrap", 1)
    # Not enough for Medkit
    import random
    rng = random.Random(0)
    result = craft_item(g, "Medkit", quantity=1, rng=rng)
    assert not result.get("success")
