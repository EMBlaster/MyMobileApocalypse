import random
from survivor import Survivor
from utils import roll_dice, chance_check
from map_nodes import Node, AVAILABLE_NODES
from character_creator import create_new_survivor
from quests import Quest, AVAILABLE_QUESTS # NEW IMPORT
from base_jobs import BaseJob, AVAILABLE_BASE_JOBS # NEW IMPORT

# --- Constants for Travel Costs (can be adjusted later) ---
TRAVEL_FUEL_COST = 5
TRAVEL_FOOD_COST_PER_SURVIVOR = 1
TRAVEL_WATER_COST_PER_SURVIVOR = 1
TRAVEL_VEHICLE_BREAKDOWN_CHANCE = 15 # % chance to check for breakdown (e.g., 15% means 15/100 roll)

class Game:
    def __init__(self, start_day=1):
        self.game_day = start_day
        self.survivors: list[Survivor] = []
        self.global_resources: dict[str, int] = {
            "Food": 0,
            "Water": 0,
            "Fuel": 0,
            "Scrap": 0,
            "Ammunition": 0,
            "ElectronicParts": 0, # Added for consistency with quest/job rewards
        }
        self.game_map: dict[str, Node] = {}
        self.current_node: Node = None
        self.player_vehicle = None # Placeholder for the player's vehicle/mobile base (will be a class later)
        self.assigned_actions: list[dict] = [] # NEW: To track assignments for the current day

        print(f"Game initialized. Day: {self.game_day}")

    def add_survivor(self, survivor: Survivor):
        """Adds a Survivor object to the game's active survivor list."""
        if isinstance(survivor, Survivor):
            self.survivors.append(survivor)
            print(f"Added survivor: {survivor.name}")
        else:
            print("Error: Only Survivor objects can be added.")

    def add_resource(self, resource_name: str, quantity: int):
        """Adds a quantity of a resource to the global inventory."""
        if resource_name in self.global_resources:
            self.global_resources[resource_name] += quantity
            print(f"Added {quantity} {resource_name}. Total: {self.global_resources[resource_name]}")
        else:
            self.global_resources[resource_name] = quantity
            print(f"Added new resource {resource_name}: {quantity}")

    def remove_resource(self, resource_name: str, quantity: int) -> bool:
        """Removes a quantity of a resource from the global inventory, if available."""
        if resource_name in self.global_resources and self.global_resources[resource_name] >= quantity:
            self.global_resources[resource_name] -= quantity
            print(f"Removed {quantity} {resource_name}. Total: {self.global_resources[resource_name]}")
            return True
        else:
            print(f"Not enough {resource_name} to remove {quantity}. Current: {self.global_resources.get(resource_name, 0)}")
            return False

    def generate_map(self, num_nodes: int = 5):
        """
        Generates a basic, connected map for the current run.
        For simplicity, it picks random nodes and attempts to connect them in a chain-like fashion.
        """
        print(f"\n--- Generating a map with {num_nodes} nodes ---")
        self.game_map = {}
        
        # Ensure we have enough unique nodes to pick from
        if num_nodes > len(AVAILABLE_NODES):
            print(f"Warning: Requested {num_nodes} nodes, but only {len(AVAILABLE_NODES)} available. Using all available nodes.")
            selected_node_ids = list(AVAILABLE_NODES.keys())
        else:
            selected_node_ids = random.sample(list(AVAILABLE_NODES.keys()), num_nodes)
        
        previous_node_id = None
        for node_id in selected_node_ids:
            original_node = AVAILABLE_NODES[node_id]
            new_node = Node(
                id=original_node.id,
                name=original_node.name,
                description=original_node.description,
                danger_level=original_node.danger_level,
                hazard_type=original_node.hazard_type,
                connected_nodes=[],
                potential_quests=list(original_node.potential_quests),
                available_resources=dict(original_node.available_resources)
            )
            self.game_map[new_node.id] = new_node

            if previous_node_id:
                self.game_map[previous_node_id].connected_nodes.append(new_node.id)
                new_node.connected_nodes.append(previous_node_id)
                print(f"  Connected {previous_node_id} <--> {new_node.id}")
            previous_node_id = new_node.id
        
        if len(self.game_map) > 1 and not self.game_map[selected_node_ids[0]].connected_nodes:
            second_node_id = selected_node_ids[1]
            self.game_map[selected_node_ids[0]].connected_nodes.append(second_node_id)
            self.game_map[second_node_ids].connected_nodes.append(selected_node_ids[0])
            print(f"  Ensured connection between first two nodes: {selected_node_ids[0]} <--> {second_node_id}")

        print("Map generation complete.")
        if self.game_map:
            print(f"Generated Map Nodes: {[node.id for node in self.game_map.values()]}")
            
    def set_current_node(self, node_id: str):
        """Sets the player's current location on the map."""
        if node_id in self.game_map:
            self.current_node = self.game_map[node_id]
            self.current_node.is_visited = True
            print(f"Player is now at: {self.current_node.name} (ID: {self.current_node.id})")
        else:
            print(f"Error: Node '{node_id}' not found in the current map.")

    def travel_to_node(self, target_node_id: str) -> bool:
        """
        Handles the logic for traveling from the current node to a target node.
        Consumes resources and has a chance for travel events.
        """
        if not self.current_node:
            print("Error: Cannot travel, current node is not set.")
            return False

        if target_node_id not in self.current_node.connected_nodes:
            print(f"Error: Node '{target_node_id}' is not directly connected to {self.current_node.name}.")
            return False

        target_node = self.game_map.get(target_node_id)
        if not target_node:
            print(f"Error: Target node '{target_node_id}' not found in the map.")
            return False

        # --- Calculate Resource Costs ---
        fuel_needed = TRAVEL_FUEL_COST
        food_needed = TRAVEL_FOOD_COST_PER_SURVIVOR * len(self.survivors)
        water_needed = TRAVEL_WATER_COST_PER_SURVIVOR * len(self.survivors)

        # --- Check if resources are available ---
        can_afford = True
        if self.global_resources["Fuel"] < fuel_needed:
            print(f"Not enough Fuel to travel. Need {fuel_needed}, have {self.global_resources['Fuel']}.")
            can_afford = False
        if self.global_resources["Food"] < food_needed:
            print(f"Not enough Food to travel. Need {food_needed}, have {self.global_resources['Food']}.")
            can_afford = False
        if self.global_resources["Water"] < water_needed:
            print(f"Not enough Water to travel. Need {water_needed}, have {self.global_resources['Water']}.")
            can_afford = False
        
        if not can_afford:
            print("Travel aborted due to insufficient resources.")
            return False

        print(f"\n--- Traveling from {self.current_node.name} to {target_node.name} ---")
        print(f"Consuming: {fuel_needed} Fuel, {food_needed} Food, {water_needed} Water.")

        # --- Consume Resources ---
        self.remove_resource("Fuel", fuel_needed)
        self.remove_resource("Food", food_needed)
        self.remove_resource("Water", water_needed)

        # --- Travel Events (Placeholder) ---
        if chance_check(TRAVEL_VEHICLE_BREAKDOWN_CHANCE):
            print("Oh no! Vehicle breakdown during travel! (This will trigger an event later)")
            # This is where a more complex event would be triggered (e.g., skill check to repair, loss of resources, delay)
            # For now, it just prints a message.

        # --- Update Current Node ---
        self.set_current_node(target_node_id)
        print(f"Successfully arrived at {self.current_node.name}.")
        return True

    def get_assignable_survivors(self) -> list[Survivor]:
        """Returns a list of survivors not yet assigned an action for the day."""
        assigned_survivor_ids = [action['survivor'].name for action in self.assigned_actions if 'survivor' in action]
        return [s for s in self.survivors if s.name not in assigned_survivor_ids and s.is_alive]

    def get_available_quests_for_node(self) -> dict[str, Quest]:
        """Returns quests relevant to the current node."""
        if not self.current_node:
            return {}
        
        available_quests = {}
        for q_id in self.current_node.potential_quests:
            if q_id in AVAILABLE_QUESTS:
                available_quests[q_id] = AVAILABLE_QUESTS[q_id]
        return available_quests

    def get_available_base_jobs(self) -> dict[str, BaseJob]:
        """Returns all currently available base jobs."""
        # For now, all base jobs are always available. Can be filtered later by base upgrades.
        return AVAILABLE_BASE_JOBS

    def assign_actions_for_day(self):
        """
        Allows the player to assign survivors to quests or base jobs.
        """
        self.assigned_actions = [] # Reset assignments for the new day
        assignable_survivors = self.get_assignable_survivors()
        
        print("\n--- Assign Actions for Today ---")
        while assignable_survivors:
            self.display_game_state() # Show current state, especially available survivors
            print(f"\nSurvivors to assign: {[s.name for s in assignable_survivors]}")
            
            print("\nChoose an action type (or 'done' to finish assignments):")
            print("1. Assign to Quest")
            print("2. Assign to Base Job")
            print("3. Travel to New Node") # Travel is also a daily action
            action_type_choice = input("> ").strip().lower()

            if action_type_choice == 'done':
                break
            
            if action_type_choice == '1': # Assign to Quest
                available_quests = self.get_available_quests_for_node()
                if not available_quests:
                    print("No quests available at this node.")
                    continue
                
                print("\nAvailable Quests:")
                quest_options = list(available_quests.values())
                for i, quest in enumerate(quest_options):
                    print(f"  {i+1}. {quest.name} (Danger: {quest.danger_rating}, Rec. Survivors: {quest.required_survivors}, Rec. Skills: {quest.recommended_skills})")
                
                quest_choice_idx = input("Enter quest number to assign: ").strip()
                if quest_choice_idx.isdigit() and 1 <= int(quest_choice_idx) <= len(quest_options):
                    chosen_quest = quest_options[int(quest_choice_idx) - 1]
                    
                    if chosen_quest.required_survivors > len(assignable_survivors):
                        print(f"Not enough unassigned survivors for this quest (requires {chosen_quest.required_survivors}).")
                        continue

                    print(f"Assigning survivors to: {chosen_quest.name}")
                    assigned_to_quest = []
                    for _ in range(chosen_quest.required_survivors):
                        print(f"Select survivor #{len(assigned_to_quest) + 1} for '{chosen_quest.name}':")
                        for i, s in enumerate(assignable_survivors):
                            print(f"  {i+1}. {s.name} (HP: {s.current_hp:.1f}, Stress: {s.current_stress:.1f})")
                        
                        survivor_choice_idx = input("> ").strip()
                        if survivor_choice_idx.isdigit() and 1 <= int(survivor_choice_idx) <= len(assignable_survivors):
                            selected_survivor = assignable_survivors.pop(int(survivor_choice_idx) - 1)
                            assigned_to_quest.append(selected_survivor)
                            print(f"{selected_survivor.name} assigned to {chosen_quest.name}.")
                        else:
                            print("Invalid survivor selection. Please try again.")
                            # Re-add survivors if selection fails
                            assignable_survivors.extend(assigned_to_quest)
                            assigned_to_quest = []
                            break
                    
                    if assigned_to_quest:
                        self.assigned_actions.append({"type": "quest", "action_obj": chosen_quest, "survivors": assigned_to_quest})
                        
                else:
                    print("Invalid quest selection.")

            elif action_type_choice == '2': # Assign to Base Job
                available_jobs = self.get_available_base_jobs()
                if not available_jobs:
                    print("No base jobs available.")
                    continue
                
                print("\nAvailable Base Jobs:")
                job_options = list(available_jobs.values())
                for i, job in enumerate(job_options):
                    print(f"  {i+1}. {job.name} (Risk: {job.risk_level}, Rec. Skills: {job.recommended_skills})")
                
                job_choice_idx = input("Enter job number to assign: ").strip()
                if job_choice_idx.isdigit() and 1 <= int(job_choice_idx) <= len(job_options):
                    chosen_job = job_options[int(job_choice_idx) - 1]
                    
                    print(f"Select survivor for '{chosen_job.name}':")
                    for i, s in enumerate(assignable_survivors):
                        print(f"  {i+1}. {s.name} (HP: {s.current_hp:.1f}, Stress: {s.current_stress:.1f})")
                    
                    survivor_choice_idx = input("> ").strip()
                    if survivor_choice_idx.isdigit() and 1 <= int(survivor_choice_idx) <= len(assignable_survivors):
                        selected_survivor = assignable_survivors.pop(int(survivor_choice_idx) - 1)
                        self.assigned_actions.append({"type": "base_job", "action_obj": chosen_job, "survivors": [selected_survivor]})
                        print(f"{selected_survivor.name} assigned to {chosen_job.name}.")
                    else:
                        print("Invalid survivor selection. Please try again.")
                else:
                    print("Invalid job selection.")
            
            elif action_type_choice == '3': # Travel to New Node
                if not self.current_node:
                    print("Cannot travel, current node is not set.")
                    continue
                
                print("\nConnected Nodes for Travel:")
                connected_nodes_list = list(self.current_node.connected_nodes)
                if not connected_nodes_list:
                    print("No connected nodes to travel to.")
                    continue
                
                for i, node_id in enumerate(connected_nodes_list):
                    node_obj = self.game_map.get(node_id)
                    if node_obj:
                        print(f"  {i+1}. {node_obj.name} (Danger: {node_obj.danger_level}, Hazard: {node_obj.hazard_type if node_obj.hazard_type else 'None'})")
                
                travel_choice_idx = input("Enter node number to travel to: ").strip()
                if travel_choice_idx.isdigit() and 1 <= int(travel_choice_idx) <= len(connected_nodes_list):
                    target_node_id = connected_nodes_list[int(travel_choice_idx) - 1]
                    # Travel is handled immediately, not as an "assigned action" for the day
                    if self.travel_to_node(target_node_id):
                        # If travel is successful, all remaining unassigned survivors are effectively "done" for the day
                        # and no further assignments are needed.
                        assignable_survivors = [] 
                        print("Travel successful. Remaining survivors are at the new node.")
                    else:
                        print("Travel failed. You can re-assign actions for remaining survivors.")
                else:
                    print("Invalid node selection.")
            else:
                print("Invalid action type choice.")
        
        if not self.assigned_actions and self.survivors and self.get_assignable_survivors():
            print("\nNo actions assigned for the day. Survivors will rest by default.")
            # Optionally, automatically assign remaining to "Rest" job
            for survivor in self.get_assignable_survivors():
                self.assigned_actions.append({"type": "base_job", "action_obj": AVAILABLE_BASE_JOBS["RestAndRecover"], "survivors": [survivor]})


    def run_day(self):
        """
        Advances the game by one day, handling daily routines and player actions.
        """
        print(f"\n======== DAY {self.game_day} ========")
        self.game_day += 1

        # --- 1. Daily Resource Consumption (for all survivors) ---
        print("\n--- Daily Consumption ---")
        food_needed_today = len(self.survivors) * TRAVEL_FOOD_COST_PER_SURVIVOR
        water_needed_today = len(self.survivors) * TRAVEL_WATER_COST_PER_SURVIVOR

        if self.remove_resource("Food", food_needed_today):
            print(f"Consumed {food_needed_today} Food.")
        else:
            print(f"WARNING: Not enough Food for {len(self.survivors)} survivors. Consequences (e.g., stress, health loss) will apply!")
            # TODO: Implement consequences for food shortage (e.g., gain stress, take HP damage)

        if self.remove_resource("Water", water_needed_today):
            print(f"Consumed {water_needed_today} Water.")
        else:
            print(f"WARNING: Not enough Water for {len(self.survivors)} survivors. Consequences (e.g., stress, health loss) will apply!")
            # TODO: Implement consequences for water shortage

        # --- NEW: Player assigns actions ---
        self.assign_actions_for_day()

        # --- 3. Resolve Actions (Placeholder for later phases) ---
        print("\n--- Action Resolution ---")
        for action in self.assigned_actions:
            print(f"Resolving {action['type']} for {', '.join([s.name for s in action['survivors']])} on {action['action_obj'].name}")
            # TODO: Call specific resolution methods based on action['type']
        
        # Reset assigned actions for next day
        self.assigned_actions = []


        # --- 4. Base Events (Placeholder for later phases) ---
        print("\n--- Base Events ---")
        if chance_check(20): # 20% chance for a random base event
            print("A random base event occurred! (e.g., zombie attack, new survivor, minor malfunction)")
            # TODO: Implement logic for triggering specific base events.
        else:
            print("The base remained quiet today.")

        # --- 5. Update Survivor States (Placeholder for later phases) ---
        print("\n--- Survivor Status Update ---")
        for survivor in self.survivors:
            # TODO: Apply stress/HP changes based on the day's events, resolve injury/stressed flags
            if survivor.is_alive: # Only update if alive
                if survivor.current_stress > survivor.max_stress * 0.75 and not survivor.is_stressed:
                    survivor.is_stressed = True
                    print(f"{survivor.name} became stressed due to daily events.")
                if survivor.current_hp < survivor.max_hp * 0.5 and not survivor.is_injured:
                    survivor.is_injured = True
                    print(f"{survivor.name} became injured due to daily events.")
            
        print(f"Day {self.game_day-1} ends.")


    def display_game_state(self):
        """Prints a summary of the current game state."""
        print("\n--- Current Game State ---")
        print(f"Game Day: {self.game_day}")
        print(f"Survivors: {len(self.survivors)}")
        for i, survivor in enumerate(self.survivors):
            status = "Alive" if survivor.is_alive else "Deceased"
            status += ", Injured" if survivor.is_injured else ""
            status += ", Stressed" if survivor.is_stressed else ""
            print(f"  {i+1}. {survivor.name} (HP: {survivor.current_hp:.2f}/{survivor.max_hp:.2f}, Stress: {survivor.current_stress:.2f}/{survivor.max_stress:.2f}) [{status}]")
            if survivor.skills:
                print(f"    Skills: {', '.join([f'{k} L{v}' for k, v in survivor.skills.items()])}")
            if survivor.traits:
                print(f"    Traits: {', '.join(survivor.traits)}")
            if survivor.inventory:
                print(f"    Inventory: {', '.join([f'{k}: {v}' for k, v in survivor.inventory.items()])}")
        
        print("Global Resources:")
        for res, qty in self.global_resources.items():
            print(f"  {res}: {qty}")
        print(f"Current Node: {self.current_node.name if self.current_node else 'None'}")
        if self.current_node:
            connected_node_names = [self.game_map[node_id].name for node_id in self.current_node.connected_nodes if node_id in self.game_map]
            print(f"  Connected Nodes: {', '.join(connected_node_names)}")
            print(f"  Hazard: {self.current_node.hazard_type if self.current_node.hazard_type else 'None'}")
            if self.current_node.available_resources:
                print(f"  Node Resources: {self.current_node.available_resources}")
        print(f"Player Vehicle: {self.player_vehicle.name if self.player_vehicle else 'None'}")
        print("--------------------------")

# --- Example Us