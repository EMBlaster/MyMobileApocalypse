## MyMobileApocalypse — Copilot instructions

This file gives focused, actionable guidance for an AI coding agent to be productive in this repository.

Key concepts (big picture)
- The central game loop is in `game.py::Game` (see `run_day`, `assign_actions_for_day`, `display_game_state`). Most changes that alter gameplay flow attach here.
- Decision logic is encapsulated in `decision_engine.py` (class `Choice`, `make_decision`). `make_decision` computes chances and returns an outcome plus an effects dict; callers (e.g., `game.py`) are responsible for applying effects to the `Game` and `Survivor` objects.
- Combat is handled in `combat_engine.py::resolve_combat` which simulates rounds and returns a summary dict (victory/defeat/stalemate, survivors/zombies remaining). Callers should apply rewards/penalties after examining that summary.
- Non-combat actions use `event_resolver.py::resolve_action` — this is the integration point for quest/job resolution and should be updated when adding new action types.
- Data blueprints and registries live in small modules: `zombies.py`, `quests.py`, `base_jobs.py`, `map_nodes.py`, `skills.py`, `traits.py`. Use their AVAILABLE_* dicts to create instances.

Project-specific conventions & patterns
- Survivors are modeled by `Survivor` (`survivor.py`) with:
  - `attributes` dict keys: STR, AGI, INT, PER, CHR, CON, SAN
  - `skills` dict (name -> level), `traits` list, `inventory` dict
  - Methods that mutate state: `take_damage`, `gain_stress`, `heal`, `learn_skill`, etc. Prefer calling these methods rather than directly mutating fields.
- Effects objects are plain dicts (e.g. `effects_on_success`, `effects_on_failure`). Engines generally return or print effects; the Game or caller applies them.
- Side-effect style: many modules print internal traces for debugging and run small example code under `if __name__ == '__main__'` — use those entry points for quick local tests.

Integration points to check when changing behavior
- `game.py` — main entrypoint and orchestrator: adding new action types, resource types, or daily events should be wired here.
- `decision_engine.py` ↔ `event_resolver.py` — decision engine returns effects; event_resolver / game apply them. Keep the contract: (outcome_string, effects_dict).
- `combat_engine.py` ↔ `game.py` — combat returns summary dict; `game.py` is currently responsible for rewarding survivors and applying stress/hp effects.

Developer workflows
- Run the game locally (interactive CLI): run `python game.py` from the repository root (Windows PowerShell). Many modules include small example usage blocks to exercise logic.
- Debugging: modules use prints liberally. To reproduce bugs, run the module's `__main__` block (e.g., `python combat_engine.py`) or run `python game.py` to exercise full flow.
- No automated tests found in repo; add small unit tests under a `tests/` folder if you introduce behavior-critical logic.

Small examples & do/don'ts
- Example: to create a temporary zombie instance for a quest, copy a blueprint from `AVAILABLE_ZOMBIES` and set a unique `id` (see `game.py` ClearInfestation example).
- Example: when adding a new quest type, update `quests.py` for blueprint + wire resolution in `event_resolver.resolve_action` and any special combat handling in `game.py` if needed.
- Do call `Survivor` methods (e.g., `take_damage`, `gain_stress`) instead of directly changing `current_hp`/`current_stress` to preserve side effects and prints.
- Don't change the return contract of `make_decision` (currently returns (outcome, effects_dict)) or `resolve_combat` (returns summary dict) — callers expect those shapes.

Files to inspect first for feature work
- `game.py` (orchestration)
- `survivor.py` (data model & methods)
- `decision_engine.py`, `combat_engine.py`, `event_resolver.py` (logic cores)
- `zombies.py`, `quests.py`, `base_jobs.py`, `map_nodes.py` (data registries/blueprints)

If anything here is unclear or you'd like more examples (unit tests or small scripts that exercise specific systems), tell me which subsystem to expand and I will add targeted examples or tests.
