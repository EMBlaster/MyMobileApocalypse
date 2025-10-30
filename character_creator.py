from survivor import Survivor
from traits import AVAILABLE_TRAITS, Trait
from skills import AVAILABLE_SKILLS, Skill
import os # For clearing the console (optional)

# --- Constants for Character Creation ---
STARTING_POINTS_POOL = 50
ATTRIBUTE_COST_THRESHOLD = 7 # Attributes up to this value cost 1 point
ATTRIBUTE_COST_HIGH = 2    # Attributes above this threshold cost this many points per level
SKILL_COST_LEVEL_1 = 4     # Cost to learn Level 1 of a skill

def clear_screen():
    """Clears the terminal screen."""
    # Check if we are in an environment where os.system works (like a terminal/cmd/bash)
    # If not, it might not clear, but won't cause an error.
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

def get_attribute_cost(current_value: int) -> int:
    """Calculates the point cost to increase an attribute by 1."""
    if current_value < ATTRIBUTE_COST_THRESHOLD:
        return 1
    elif current_value < 10: # Cap at 10, no cost to increase beyond
        return ATTRIBUTE_COST_HIGH
    return 0 # Already at max

def display_current_character_state(points: int, attributes: dict, selected_traits: list[Trait], selected_skills: dict):
    """Displays the current character's attributes, traits, and skills."""
    print("=" * 40)
    print(f"{'POINTS REMAINING:':<20} {points}")
    print("=" * 40)

    print("\n--- ATTRIBUTES ---")
    for attr, val in attributes.items():
        cost_to_increase = get_attribute_cost(val) if val < 10 else "Max"
        # Display cost to decrease, if not at min (attribute cost to return is cost for the *previous* level)
        cost_to_decrease = get_attribute_cost(val - 1) if val > 1 else "Min"
        print(f"{attr}: {val:<2} (Cost to +1: {cost_to_increase}, Points returned if -1: {cost_to_decrease})")
    
    print("\n--- TRAITS ---")
    if not selected_traits:
        print("  None selected.")
    else:
        for trait in selected_traits:
            print(f"  - {trait.name} (Cost: {trait.point_cost})")

    print("\n--- SKILLS (Level 1) ---")
    if not selected_skills:
        print("  None learned.")
    else:
        for skill_name, level in selected_skills.items():
            print(f"  - {skill_name} (Level {level})")
    print("=" * 40)

def create_pregenerated_survivor() -> Survivor:
    """
    Creates and returns a pre-generated Survivor with a balanced spread of attributes, traits, and skills.
    This represents a "well-rounded" survivor suitable for general gameplay.
    """
    # Create base survivor with balanced attributes (good middle-ground values)
    pregenerated = Survivor(
        name="Alex Chen",
        str_val=5,
        agi_val=6,
        int_val=5,
        per_val=6,
        chr_val=4,
        con_val=5,
        san_val=5
    )
    
    # Add balanced traits
    # Adjust these based on your available traits and what works well together
    pregenerated.add_trait("Brave")
    pregenerated.add_trait("Strong")
    
    # Learn foundational skills
    pregenerated.learn_skill("Small Arms", 1)
    pregenerated.learn_skill("First Aid", 1)
    pregenerated.learn_skill("Scouting", 1)
    
    return pregenerated


def character_creation_menu() -> Survivor:
    """
    Main interactive menu for character creation.
    Allows player to choose between custom creation or pre-generated character.
    """
    clear_screen()
    print("\n--- NEW SURVIVOR CREATION ---")
    print("1. Create Custom Character")
    print("2. Use Pre-Generated Character")
    
    initial_choice = input("> ").strip()
    
    if initial_choice == '2':
        pregenerated = create_pregenerated_survivor()
        print(f"\nLoading pre-generated survivor: {pregenerated.name}")
        print(f"Attributes: {pregenerated.attributes}")
        print(f"Traits: {pregenerated.traits}")
        print(f"Skills: {pregenerated.skills}")
        input("Press Enter to continue...")
        return pregenerated
    
    # Custom character creation (original flow)
    clear_screen()
    print("\n--- NEW SURVIVOR CREATION ---")
    name = input("Enter survivor's name: ").strip()
    if not name:
        name = "Unnamed Survivor"

    points_pool = STARTING_POINTS_POOL
    current_attributes = {attr: 1 for attr in ["STR", "AGI", "INT", "PER", "CHR", "CON", "SAN"]}
    selected_traits: list[Trait] = []
    selected_skills: dict[str, int] = {}

    while True:
        clear_screen()
        print(f"\n--- Creating {name} ---")
        display_current_character_state(points_pool, current_attributes, selected_traits, selected_skills)
        
        print("\nChoose an option:")
        print("1. Edit Attributes")
        print("2. Edit Traits")
        print("3. Edit Skills")
        print("4. Finalize Character")
        print("5. (Cheat: Add 100 Points - for testing)")
        
        choice = input("> ").strip()


        if choice == '1': # Edit Attributes
            while True:
                clear_screen() # Clear at the start of each attribute sub-menu loop iteration
                print("\n--- EDIT ATTRIBUTES ---")
                display_current_character_state(points_pool, current_attributes, selected_traits, selected_skills)
                print("\nEnter attribute to change (e.g., STR +1, CON -1) or 'back' to return.")
                print("Attributes are 1-10. Cost to +1: 1pt (1-7), 2pt (8-10).")
                
                attr_input = input("> ").strip().upper()
                if attr_input == 'BACK':
                    break
                
                parts = attr_input.split()
                if len(parts) == 2 and parts[0] in current_attributes and (parts[1] == '+1' or parts[1] == '-1'):
                    attr_name = parts[0]
                    change_type = parts[1]
                    current_val = current_attributes[attr_name]

                    if change_type == '+1':
                        cost = get_attribute_cost(current_val)
                        if current_val < 10:
                            if points_pool >= cost:
                                current_attributes[attr_name] += 1
                                points_pool -= cost
                                print(f"Increased {attr_name} to {current_attributes[attr_name]}. Spent {cost} points.")
                            else:
                                print(f"Not enough points. Requires {cost}.")
                        else:
                            print(f"{attr_name} is already at max (10).")
                    elif change_type == '-1':
                        if current_val > 1:
                            cost_returned = get_attribute_cost(current_val - 1) # Cost to get to current, so return that
                            current_attributes[attr_name] -= 1
                            points_pool += cost_returned
                            print(f"Decreased {attr_name} to {current_attributes[attr_name]}. Points returned: {cost_returned}.")
                        else:
                            print(f"{attr_name} is already at min (1).")
                else:
                    print("Invalid input. Use format 'ATTR +1' or 'ATTR -1'.")
                input("Press Enter to continue...") # Pause for user to read message

        elif choice == '2': # Edit Traits
            while True:
                clear_screen() # Clear at the start of each trait sub-menu loop iteration
                print("\n--- EDIT TRAITS ---")
                display_current_character_state(points_pool, current_attributes, selected_traits, selected_skills)
                
                print("\nAvailable Traits (Select by number to toggle):")
                display_trait_options = []
                for i, (trait_name, trait_obj) in enumerate(AVAILABLE_TRAITS.items()):
                    is_selected = trait_obj in selected_traits
                    status = "[SELECTED]" if is_selected else ""

                    conflicts_exist = False
                    if not is_selected: # Only check conflicts if trying to ADD
                        for selected_t in selected_traits:
                            if trait_name in selected_t.conflicts or selected_t.name in trait_obj.conflicts:
                                conflicts_exist = True
                                break
                    
                    if conflicts_exist:
                        status += " [CONFLICT]"
                    
                    display_trait_options.append((trait_obj, status, conflicts_exist))
                    print(f"{i+1}. {trait_name} (Cost: {trait_obj.point_cost}) - {trait_obj.description} {status}")
                
                print("\nEnter trait number to toggle, or 'back' to return.")
                trait_choice = input("> ").strip()

                if trait_choice.lower() == 'back':
                    break
                elif trait_choice.isdigit() and 1 <= int(trait_choice) <= len(AVAILABLE_TRAITS):
                    selected_idx = int(trait_choice) - 1
                    trait_obj_to_toggle, status_text, conflicts_exist = display_trait_options[selected_idx]

                    if trait_obj_to_toggle in selected_traits: # Remove trait
                        selected_traits.remove(trait_obj_to_toggle)
                        points_pool += trait_obj_to_toggle.point_cost
                        print(f"Removed '{trait_obj_to_toggle.name}'. Points returned: {trait_obj_to_toggle.point_cost}")
                    else: # Add trait
                        if conflicts_exist:
                            print(f"Cannot add '{trait_obj_to_toggle.name}'. It conflicts with an already selected trait.")
                        elif points_pool >= trait_obj_to_toggle.point_cost:
                            selected_traits.append(trait_obj_to_toggle)
                            points_pool -= trait_obj_to_toggle.point_cost
                            print(f"Added '{trait_obj_to_toggle.name}'. Points spent: {trait_obj_to_toggle.point_cost}")
                        else:
                            print(f"Not enough points to add '{trait_obj_to_toggle.name}'. Requires {trait_obj_to_toggle.point_cost} points.")
                else:
                    print("Invalid selection.")
                input("Press Enter to continue...") # Pause for user to read message

        elif choice == '3': # Edit Skills
            while True:
                clear_screen() # Clear at the start of each skill sub-menu loop iteration
                print("\n--- EDIT SKILLS (Level 1) ---")
                display_current_character_state(points_pool, current_attributes, selected_traits, selected_skills)
                
                print("\nAvailable Skills (Select by number to toggle):")
                display_skill_options = []
                for i, (skill_name, skill_obj) in enumerate(AVAILABLE_SKILLS.items()):
                    is_learned = skill_name in selected_skills
                    status = "[LEARNED]" if is_learned else ""

                    # Check prerequisites
                    prereqs_met = True
                    prereq_string = ""
                    for attr, req_val in skill_obj.attribute_prerequisites.items():
                        prereq_string += f"{attr} {req_val}, "
                        if current_attributes.get(attr, 0) < req_val:
                            prereqs_met = False
                    prereq_string = prereq_string.rstrip(', ')

                    if not prereqs_met:
                        status += " [PREREQS NOT MET]"
                    
                    display_skill_options.append((skill_obj, status, prereqs_met))
                    print(f"{i+1}. {skill_name} (Cost: {SKILL_COST_LEVEL_1}) - {skill_obj.description} (Req: {prereq_string}) {status}")
                
                print("\nEnter skill number to toggle, or 'back' to return.")
                skill_choice = input("> ").strip()

                if skill_choice.lower() == 'back':
                    break
                elif skill_choice.isdigit() and 1 <= int(skill_choice) <= len(AVAILABLE_SKILLS):
                    selected_idx = int(skill_choice) - 1
                    skill_obj_to_toggle, status_text, prereqs_met = display_skill_options[selected_idx]

                    if skill_obj_to_toggle.name in selected_skills: # Unlearn skill
                        del selected_skills[skill_obj_to_toggle.name]
                        points_pool += SKILL_COST_LEVEL_1
                        print(f"Unlearned '{skill_obj_to_toggle.name}'. Points returned: {SKILL_COST_LEVEL_1}")
                    else: # Learn skill
                        if not prereqs_met:
                            print(f"Cannot learn '{skill_obj_to_toggle.name}'. Prerequisites not met.")
                        elif points_pool >= SKILL_COST_LEVEL_1:
                            selected_skills[skill_obj_to_toggle.name] = 1 # Learn at Level 1
                            points_pool -= SKILL_COST_LEVEL_1
                            print(f"Learned '{skill_obj_to_toggle.name}' at Level 1. Points spent: {SKILL_COST_LEVEL_1}")
                        else:
                            print(f"Not enough points to learn '{skill_obj_to_toggle.name}'. Requires {SKILL_COST_LEVEL_1} points.")
                else:
                    print("Invalid selection.")
                input("Press Enter to continue...") # Pause for user to read message

        elif choice == '4': # Finalize Character
            print("\n--- FINALIZING CHARACTER ---")
            break
        elif choice == '5':
            points_pool += 100
            print("100 points added for testing purposes!")
            input("Press Enter to continue...")
        else:
            print("Invalid option.")
            input("Press Enter to continue...")

    # --- Construct Final Survivor Object ---
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

    for trait_obj in selected_traits:
        final_survivor.add_trait(trait_obj.name)

    for skill_name, level in selected_skills.items():
        final_survivor.learn_skill(skill_name, level)

    print(f"\nSurvivor '{final_survivor.name}' has been created!")
    print(f"Final Attributes: {final_survivor.attributes}")
    print(f"Final Traits: {[t.name for t in selected_traits]}")
    print(f"Final Skills: {final_survivor.skills}")
    print(f"Remaining points: {points_pool}")

    return final_survivor


# --- Example Usage (for testing the character creator) ---
if __name__ == "__main__":
    test_survivor = character_creation_menu()
    print("\n--- Test Survivor Details ---")
    print(f"Name: {test_survivor.name}")
    print(f"HP: {test_survivor.current_hp}/{test_survivor.max_hp}")
    print(f"Stress: {test_survivor.current_stress}/{test_survivor.max_stress}")
    print(f"Is Alive: {test_survivor.is_alive}")
    print(f"Attributes: {test_survivor.attributes}")
    print(f"Skills: {test_survivor.skills}")
    print(f"Traits: {test_survivor.traits}")