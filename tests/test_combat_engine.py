import unittest

import combat_engine as ce
from survivor import Survivor
from zombies import Zombie, AVAILABLE_ZOMBIES


class CombatEngineTests(unittest.TestCase):
    def setUp(self):
        # Backup originals to restore after tests
        self._orig_calc_survivor = ce.calculate_survivor_hit_chance
        self._orig_calc_zombie = ce.calculate_zombie_hit_chance
        self._orig_chance_check = ce.chance_check

    def tearDown(self):
        ce.calculate_survivor_hit_chance = self._orig_calc_survivor
        ce.calculate_zombie_hit_chance = self._orig_calc_zombie
        ce.chance_check = self._orig_chance_check

    def _fresh_zombie(self, z_id: str, instance_id: str):
        bp = AVAILABLE_ZOMBIES[z_id]
        return Zombie(id=instance_id, name=bp.name, description=bp.description,
                      base_hp=bp.base_hp, damage=bp.damage, speed=bp.speed, defense=bp.defense,
                      traits=list(bp.traits))

    def test_survivors_win_when_they_always_hit(self):
        # Survivors always hit, zombies never hit
        ce.calculate_survivor_hit_chance = lambda a, t, env: 100
        ce.calculate_zombie_hit_chance = lambda a, t, env: 0
        ce.chance_check = lambda pct: pct == 100

        s1 = Survivor(name="Fighter", str_val=8, agi_val=6, int_val=4, per_val=5, chr_val=3, con_val=7, san_val=6)
        s1.learn_skill("Melee Weaponry", 2)
        s2 = Survivor(name="Shooter", str_val=4, agi_val=8, int_val=5, per_val=7, chr_val=4, con_val=5, san_val=7)
        s2.learn_skill("Small Arms", 2)

        zombies = [self._fresh_zombie("shambler", "z1"), self._fresh_zombie("shambler", "z2")]

        result = ce.resolve_combat(survivors=[s1, s2], zombies=zombies, game_instance=None, environment_mods={}, node_danger=1)
        self.assertTrue(result["victory"], f"Expected survivors to win but got: {result}")

    def test_zombies_win_when_survivors_never_hit(self):
        ce.calculate_survivor_hit_chance = lambda a, t, env: 0
        ce.calculate_zombie_hit_chance = lambda a, t, env: 100
        ce.chance_check = lambda pct: pct == 100

        s1 = Survivor(name="Weak", str_val=1, agi_val=1, int_val=1, per_val=1, chr_val=1, con_val=1, san_val=1)
        zombies = [self._fresh_zombie("charger", "z1"), self._fresh_zombie("charger", "z2")]

        result = ce.resolve_combat(survivors=[s1], zombies=zombies, game_instance=None, environment_mods={}, node_danger=1)
        self.assertTrue(result["defeat"] or result["zombies_remaining"] > 0, f"Expected zombies to win or remain, got: {result}")


if __name__ == '__main__':
    unittest.main()
