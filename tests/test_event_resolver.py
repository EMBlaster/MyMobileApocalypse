import unittest

import event_resolver as er
from survivor import Survivor


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


class EventResolverTests(unittest.TestCase):
    def test_calculate_chance_skill_bonus(self):
        s_no_skill = Survivor(name="NoSkill", str_val=4, agi_val=4, int_val=4, per_val=4, chr_val=4, con_val=4, san_val=4)
        s_with_skill = Survivor(name="WithSkill", str_val=4, agi_val=4, int_val=4, per_val=4, chr_val=4, con_val=4, san_val=4)
        s_with_skill.learn_skill("Mechanics", 2)

        action = DummyAction("Fix", recommended_skills={"Mechanics": 1})

        chance_no = er.calculate_action_success_chance([s_no_skill], action, "base_job", node_danger_modifier=0)
        chance_with = er.calculate_action_success_chance([s_with_skill], action, "base_job", node_danger_modifier=0)

        self.assertGreater(chance_with, chance_no, "Skill should increase action success chance")

    def test_resolve_action_success_and_rewards(self):
        # Force deterministic success by patching roll_d100 to a low value
        original_roll = er.roll_d100
        er.roll_d100 = lambda: 1

        try:
            survivor = Survivor(name="Hero", str_val=5, agi_val=5, int_val=6, per_val=4, chr_val=3, con_val=5, san_val=4)
            survivor.learn_skill("Mechanics", 2)

            action = DummyAction("Repair", recommended_skills={"Mechanics": 1}, rewards={"Scrap": 10})
            game = MockGame()

            success, critical = er.resolve_action([survivor], action, "base_job", game, node_danger=0)

            self.assertTrue(success, "Action should be successful when roll_d100 is low")
            self.assertIn("Scrap", game.resources)
            self.assertGreaterEqual(game.resources["Scrap"], 10)
        finally:
            er.roll_d100 = original_roll

    def test_resolve_action_failure_and_consequences(self):
        # Force deterministic failure by patching roll_d100 to a high value
        original_roll = er.roll_d100
        er.roll_d100 = lambda: 100

        try:
            survivor = Survivor(name="Unlucky", str_val=4, agi_val=4, int_val=4, per_val=4, chr_val=4, con_val=4, san_val=4)
            action = DummyAction(
                "DangerJob",
                recommended_skills={"Mechanics": 3},
                rewards={"Scrap": 5},
                fail_consequences={"HP_loss_per_survivor": 10, "Stress_gain_per_survivor": 5}
            )
            game = MockGame()

            success, critical = er.resolve_action([survivor], action, "quest", game, node_danger=3)

            self.assertFalse(success, "Action should fail when roll_d100 is high")
            # Survivor should have taken damage or stress (current_hp reduced or current_stress increased)
            self.assertTrue(survivor.current_hp < survivor.max_hp or survivor.current_stress > 0)
        finally:
            er.roll_d100 = original_roll


if __name__ == '__main__':
    unittest.main()
