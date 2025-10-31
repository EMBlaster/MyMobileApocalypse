from typing import Optional
from items import RECIPES, ITEMS
import math
import random


def craft_item(game, recipe_id: str, quantity: int = 1, survivor=None, rng: Optional[random.Random] = None) -> dict:
    """
    Attempt to craft `quantity` units of recipe_id.
    If `survivor` is provided, add produced item(s) to that survivor's inventory; otherwise, add to game's global resources if the recipe produces a resource.

    Returns a dict with keys:
      - success: bool
      - produced_qty: int
      - consumed: dict of resources consumed

    Behavior:
      - Mechanics skill reduces required resources (flat) and improves success chance + produced quantity.
      - Uses RNG (random.Random) if provided for deterministic tests.
    """
    rng = rng or random.Random()

    # Allow recipe_id to be the produced resource name by searching RECIPES
    recipe = RECIPES.get(recipe_id)
    if recipe is None:
        # Try to find a recipe where the produces.resource or produces.item matches recipe_id
        for r_id, r in RECIPES.items():
            produces = r.get("produces", {})
            if produces.get("resource") == recipe_id or produces.get("item") == recipe_id:
                recipe = r
                break

    if recipe is None:
        return {"success": False, "produced_qty": 0, "consumed": {}}

    base_required = recipe.get("requires", {})
    base_produced = recipe.get("produces", {})

    mech_level = 0
    if survivor is not None:
        mech_level = survivor.skills.get("Mechanics", 0)

    # Apply simple skill modifiers: reduce each required resource by mech_level (flat), min 0
    required = {}
    for k, v in base_required.items():
        req = max(0, v - mech_level) * quantity
        required[k] = req

    # Check availability
    for res, amt in required.items():
        if game.global_resources.get(res, 0) < amt:
            return {"success": False, "produced_qty": 0, "consumed": {}}

    # Consume resources
    consumed = {}
    for res, amt in required.items():
        if amt > 0:
            game.remove_resource(res, amt)
            consumed[res] = amt

    # Determine base produced quantity
    if "quantity" in base_produced:
        base_qty = base_produced.get("quantity", 1)
        produced_qty = base_qty * quantity + mech_level  # flat bonus per mechanics level
    else:
        produced_qty = 1 * quantity + mech_level

    # Success chance
    base_success = float(recipe.get("base_success_chance", 0.9))
    success_bonus = 0.03 * mech_level
    success_chance = min(0.99, base_success + success_bonus)
    roll = rng.random()
    is_success = roll <= success_chance

    # Critical success chance depends on mechanics (small)
    crit_chance = min(0.5, 0.05 + 0.02 * mech_level)
    is_critical = is_success and (rng.random() <= crit_chance)

    if not is_success:
        # Failure: resources already consumed, nothing produced
        return {"success": False, "produced_qty": 0, "consumed": consumed}

    # On success, apply critical multiplier
    if is_critical:
        produced_qty = int(produced_qty * 2)

    # Apply produced
    if "item" in base_produced:
        item_id = base_produced["item"]
        if survivor is not None:
            survivor.add_item_to_inventory(item_id, produced_qty)
        else:
            game.global_resources[item_id] = game.global_resources.get(item_id, 0) + produced_qty
    elif "resource" in base_produced:
        res_name = base_produced["resource"]
        game.add_resource(res_name, produced_qty)

    return {"success": True, "produced_qty": produced_qty, "consumed": consumed}
