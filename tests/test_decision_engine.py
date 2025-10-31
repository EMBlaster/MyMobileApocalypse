import unittest
import builtins

import decision_engine as de
from survivor import Survivor


class DecisionEngineTests(unittest.TestCase):
    def setUp(self):
        self._orig_roll = de.roll_d100
        self._orig_input = builtins.input

    def tearDown(self):
        de.roll_d100 = self._orig_roll
        builtins.input = self._orig_input

    def test_calculate_choice_specific_chance_skill_and_attribute(self):
        s = Survivor(name="Smart", str_val=3, agi_val=3, int_val=7, per_val=3, chr_val=3, con_val=3, san_val=3)
        s.learn_skill("Mechanics", 2)
        choice = de.Choice(text="Test", description="", base_success_chance=50, prerequisites={"skill": {"Mechanics": 1}, "attribute": {"INT": 6}})
        chance = de.calculate_choice_specific_chance(choice, [s], None)
        self.assertGreater(chance, 50)

    def test_make_decision_success_path(self):
        # Force success by making roll_d100 low and calculator return high chance
        de.calculate_choice_specific_chance = lambda c, s, g: 100
        de.roll_d100 = lambda: 1
        builtins.input = lambda prompt='': '1'

        survivor = Survivor(name="Decider", str_val=4, agi_val=4, int_val=5, per_val=4, chr_val=4, con_val=4, san_val=4)
        choices = [de.Choice(text="Do it", description="", base_success_chance=50, effects_on_success={"info": "ok"})]
        outcome, effects = de.make_decision("Choose:", choices, game_instance=None, affected_survivors=[survivor], node_danger=1)
        self.assertIn(outcome, ("success", "critical_success"))
        self.assertEqual(effects, choices[0].effects_on_success)

    def test_make_decision_failure_path(self):
        de.calculate_choice_specific_chance = lambda c, s, g: 0
        de.roll_d100 = lambda: 100
        builtins.input = lambda prompt='': '1'

        survivor = Survivor(name="Decider2", str_val=4, agi_val=4, int_val=5, per_val=4, chr_val=4, con_val=4, san_val=4)
        choices = [de.Choice(text="Don't", description="", base_success_chance=50, effects_on_failure={"info": "bad"})]
        outcome, effects = de.make_decision("Choose:", choices, game_instance=None, affected_survivors=[survivor], node_danger=1)
        self.assertIn(outcome, ("failure", "critical_failure"))
        self.assertEqual(effects, choices[0].effects_on_failure)


if __name__ == '__main__':
    unittest.main()
