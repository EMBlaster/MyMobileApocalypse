import sys
from pathlib import Path

# Ensure repo root on sys.path when running from scripts/
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from io_handler import HeadlessIO
from decision_engine import Choice, make_decision

# Build the visitor choices used in game
visitor_choices = [
    Choice(
        text="Welcome Visitor",
        description="Let them join, risking resources but gaining potential manpower.",
        base_success_chance=70,
        effects_on_success={"recruit_survivor": True, "resource_loss": {"Food": 10, "Water": 10}},
        effects_on_failure={"stress_gain_per_survivor": 5, "info": "Visitor was hostile or sick."},
        known_consequences_text="Risk resources, may gain a survivor."
    ),
    Choice(
        text="Turn Away Visitor",
        description="Conserve resources, but miss a potential opportunity.",
        base_success_chance=99,
        effects_on_success={"info": "Visitor left peacefully."},
        effects_on_failure={"stress_gain_per_survivor": 5, "info": "Visitor reacted negatively."},
        known_consequences_text="Safe, but no new survivor."
    ),
]

# Use HeadlessIO with response '1' to pick the first option (Welcome Visitor)
io = HeadlessIO(responses=["1"]) 
outcome, effects = make_decision(
    prompt="A lone survivor approaches your mobile base. What do you do?",
    choices=visitor_choices,
    game_instance=None,
    affected_survivors=[],
    node_danger=1,
    io_handler=io
)
print('Outcome:', outcome)
print('Effects:', effects)
print('\nCaptured output:')
for line in io.output:
    print(line)
