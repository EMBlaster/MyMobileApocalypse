import json
from pathlib import Path

from game import Game
from survivor import Survivor


def test_save_load_roundtrip(tmp_path: Path):
    save_path = tmp_path / "roundtrip_save.json"

    g = Game(start_day=3)
    # create a survivor with a known skill
    s = Survivor(name="Testy", con_val=5, san_val=4, int_val=3)
    s.learn_skill("Mechanics", 1)
    g.add_survivor(s)

    # add some resources and set a known day
    g.add_resource("Food", 42)
    g.global_resources["Water"] = 7
    g.game_day = 7

    # save and load
    g.save_to_file(save_path)
    loaded = Game.load_from_file(save_path)

    assert loaded.game_day == g.game_day
    assert loaded.global_resources.get("Food") == 42
    assert loaded.global_resources.get("Water") == 7
    assert len(loaded.survivors) == 1
    ls = loaded.survivors[0]
    assert ls.name == "Testy"
    assert ls.skills.get("Mechanics") == 1
