from survivor import Survivor
from traits import AVAILABLE_TRAITS, Trait
from skills import AVAILABLE_SKILLS, Skill
import math # For math.ceil if needed for point costs/etc.

# --- Constants for Character Creation ---
STARTING_POINTS_POOL = 50
ATTRIBUTE_COST_THRESHOLD = 7 # Attributes up to this value cost 1 point
ATTRIBUTE_COST_HIGH = 2    # Attributes above this threshold cost this many points per level
SKILL_COST_LEVEL_1 = 4     # Cost to learn Level 1 of a skill

def create_new_survivor() -> Survivor:
    """
    Guides the player through the character creation process to build a new Survivor.
    """
    print("\n--- NEW SURVIVOR CREATION ---")
    name = input("Enter survivor's name: ").strip()
    if not name:
        name = "Unnamed Survivor"

    points_pool = STARTING_POINTS_POOL
    current_attributes = {attr: 1 for attr in ["STR", "AGI", "INT", "PER", "CHR", "CON", "SAN"]}
    selected_traits: list[Trait] = []
    selected_skills: dict[str, int] = {} # Skill name: level

    print(f"\nYou have {points_pool} points to spend on Attributes, Traits, and Skills.")

    # --- 1. Attribute Distribution ---
    while True:
        print("\n--- ATTRIBUTE DISTRIBUTION ---")
        print(f"Points remaining: {points_pool}")
        for attr, val in current_attributes.items():
            print(f"  {attr}: {val}")

        print("\nEnter attribute to increase (e.g., STR) or 'done' to continue.")
        choice = input("> ").strip().upper()

        if choice == 'DONE':
            break
        elif choice in current_attributes:
            current_value = current_attributes[choice]
            cost = 0
            if current_value < ATTRIBUTE_COST_THRESHOLD:
                cost = 1
            else:
                cost = ATTRIBUTE_COST_HIGH

            if points_pool >= cost:
                if current_value < 10: # Cap attributes at 10
                    current_attributes[choice] += 1
                    points_pool -= cost
                    print(f"Increased {choice} to {current_attributes[choice]}. Spent {cost} points.")
                else:
                    print(f"{choice} is already at max (10).")
            else:
                print(f"Not enough points to increase {choice}. Requires {cost} points.")
        else:
            print("Invalid attribute. Please choose from STR, AGI, INT, PER, CHR, CON, SAN or type 'done'.")

    # --- 2. Trait Selection ---
    while True:
        print("\n--- TRAIT SELECTION ---")
        print(f"Points remaining: {points_pool}")
        print("\nCurrently selected traits:")
        if not selected_traits:
            print("  None")
        for trait in selected_traits:
            print(f"  - {trait.name} (Cost: {trait.point_cost})")

        print("\nAvailable traits:")
        available_for_selection = {}
        trait_index = 1
        for trait_name, trait_obj in AVAILABLE_TRAITS.items():
            # Check for conflicts with already selected traits
            conflicts_exist = False
            for selected_t in selected_traits:
                if trait_name in selected_t.conflicts or selected_t.name in trait_obj.conflicts:
                    conflicts_exist = True
                    break
            if conflicts_exist:
                continue

            available_for_selection[str(trait_index)] = trait_obj
            print(f"  {trait_index}. {trait_name} (Cost: {trait_obj.point_cost}) - {trait_obj.description}")
            trait_index += 1

        print("\nEnter number of trait to add/remove, or 'done' to continue.")
        choice = input("> ").strip()

        if choice.lower() == 'done':
            break
        elif choice.isdigit() and choice in available_for_selection:
            trait_to_select = available_for_selection[choice]

            if trait_to_select in selected_traits: # If already selected, allow removal
                selected_traits.remove(trait_to_select)
                points_pool += trait_to_select.point_cost # Return points
                print(f"Removed trait '{trait_to_select.name}'. Points returned: {trait_to_select.point_cost}")
            else: # Add trait
                if points_pool >= trait_to_select.point_cost:
                    selected_traits.append(trait_to_select)
                    points_pool -= trait_to_select.point_cost
                    print(f"Added trait '{trait_to_select.name}'. Points spent: {trait_to_select.point_cost}")
                else:
                    print(f"Not enough points to add trait '{trait_to_select.name}'. Requires {trait_to_select.point_cost} points.")
        else:
            print("Invalid selection. Please enter a valid number or 'done'.")

    # --- 3. Skill Selection ---
    while True:
        print("\n--- SKILL SELECTION ---")
        print(f"Points remaining: {points_pool}")
        print("\nCurrently learned skills:")
        if not selected_skills:
            print("  None")
        for skill_name, level in selected_skills.items():
            print(f"  - {skill_name} (Level {level})")

        print("\nAvailable skills to learn (Level 1):")
        available_for_selection = {}
        skill_index = 1
        for skill_name, skill_obj in AVAILABLE_SKILLS.items():
            if skill_name in selected_skills: # Don't show already learned skills (for now, assume level 1 only)
                continue

            # Check prerequisites
            prereqs_met = True
            for attr, req_val in skill_obj.attribute_prerequisites.items():
                if current_attributes.get(attr, 0) < req_val:
                    prereqs_met = False
                    break

            if not prereqs_met:
                print(f"  (Prereqs not met) {skill_index}. {skill_name} (Cost: {skill_obj.cost_to_learn}) - Requires: {skill_obj.attribute_prerequisites}")
                skill_index += 1
                continue

            available_for_selection[str(skill_index)] = skill_obj
            print(f"  {skill_index}. {skill_name} (Cost: {skill_obj.cost_to_learn}) - {skill_obj.description}")
            skill_index += 1

        print("\nEnter number of skill to learn (Level 1), or 'done' to continue.")
        choice = input("> ").strip()

        if choice.lower() == 'done':
            break
        elif choice.isdigit() and choice in available_for_selection:
            skill_to_learn = available_for_selection[choice]

            if points_pool >= SKILL_COST_LEVEL_1:
                selected_skills[skill_to_learn.name] = 1 # Learn at Level 1
                points_pool -= SKILL_COST_LEVEL_1
                print(f"Learned skill '{skill_to_learn.name}' at Level 1. Points spent: {SKILL_COST_LEVEL_1}")
            else:
                print(f"Not enough points to learn skill '{skill_to_learn.name}'. Requires {SKILL_COST_LEVEL_1} points.")
        else:
            print("Invalid selection. Please enter a valid number or 'done'.")


    # --- Final Survivor Creation ---
    print("\n--- FINALIZING SURVIVOR ---")
    final_survivor = Survivor(
        name=name,
        str_val=current_attributes["STR"],
        agi_val=current_attributes["AGI"],
        int_val=current_attributes["INT"],
        per_val=current_attributes["PER"],
        chr_val=current_attributes["CHR"],
        con_val=current_attributes["CON"],
        san_val=current_attributes["SAN"]
    )

    for trait in selected_traits:
        final_survivor.add_trait(trait.name) # Add trait name to survivor

    for skill_name, level in selected_skills.items():
        final_survivor.learn_skill(skill_name, level) # Add skill to survivor

    print(f"\nSurvivor '{final_survivor.name}' has been created!")
    print(f"Final Attributes: {final_survivor.attributes}")
    print(f"Final Traits: {final_survivor.traits}")
    print(f"Final Skills: {final_survivor.skills}")
    print(f"Remaining points: {points_pool}")

    return final_survivor

# --- Example Usage (for testing the character creator) ---
if __name__ == "__main__":
    test_survivor = create_new_survivor()
    print("\n--- Test Survivor Details ---")
    print(f"Name: {test_survivor.name}")
    print(f"HP: {test_survivor.current_hp}/{test_survivor.max_hp}")
    print(f"Stress: {test_survivor.current_stress}/{test_survivor.max_stress}")
    print(f"Is Alive: {test_survivor.is_alive}")
    print(f"Attributes: {test_survivor.attributes}")
    print(f"Skills: {test_survivor.skills}")
    print(f"Traits: {test_survivor.traits}")