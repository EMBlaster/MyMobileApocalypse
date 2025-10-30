import random
from survivor import Survivor
from utils import roll_dice, chance_check
from map_nodes import Node, AVAILABLE_NODES # Import for Node class and definitions

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
            "Ammunition": 0
        }
        self.game_map: dict[str, Node] = {} # Dictionary to store the generated map (Node ID: Node object)
        self.current_node: Node = None # Current map node where the player's vehicle/base is
        self.player_vehicle = None # Placeholder for the player's vehicle/mobile base (will be a class later)

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
            # Create a copy of the node from AVAILABLE_NODES to ensure fresh instance
            original_node = AVAILABLE_NODES[node_id]
            new_node = Node(
                id=original_node.id,
                name=original_node.name,
                description=original_node.description,
                danger_level=original_node.danger_level,
                hazard_type=original_node.hazard_type,
                connected_nodes=[], # Start with empty connections, we'll build them
                potential_quests=list(original_node.potential_quests), # Copy list
                available_resources=dict(original_node.available_resources) # Copy dict
            )
            self.game_map[new_node.id] = new_node

            if previous_node_id:
                # Connect current node to previous and previous to current (two-way)
                self.game_map[previous_node_id].connected_nodes.append(new_node.id)
                new_node.connected_nodes.append(previous_node_id)
                print(f"  Connected {previous_node_id} <--> {new_node.id}")
            previous_node_id = new_node.id
        
        # Ensure the first node is connectable to a random other node if map is small and not fully connected
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


    def display_game_state(self):
        """Prints a summary of the current game state."""
        print("\n--- Current Game State ---")
        print(f"Game Day: {self.game_day}")
        print(f"Survivors: {len(self.survivors)}")
        for i, survivor in enumerate(self.survivors):
            print(f"  {i+1}. {survivor.name} (HP: {survivor.current_hp:.2f}/{survivor.max_hp:.2f}, Stress: {survivor.current_stress:.2f}/{survivor.max_stress:.2f}, Injured: {survivor.is_injured}, Stressed: {survivor.is_stressed})")
        print("Global Resources:")
        for res, qty in self.global_resources.items():
            print(f"  {res}: {qty}")
        print(f"Current Node: {self.current_node.name if self.current_node else 'None'}")
        if self.current_node:
            print(f"  Connected Nodes: {[self.game_map[node_id].name for node_id in self.current_node.connected_nodes]}")
            print(f"  Hazard: {self.current_node.hazard_type if self.current_node.hazard_type else 'None'}")
        print(f"Player Vehicle: {self.player_vehicle.name if self.player_vehicle else 'None'}")
        print("--------------------------")

# --- Example Usage (for testing the Game class with map and navigation functionality) ---
if __name__ == "__main__":
    print("--- Initializing Game ---")
    my_game = Game()

    # Add some initial resources for travel
    my_game.add_resource("Food", 100)
    my_game.add_resource("Water", 100)
    my_game.add_resource("Fuel", 50)
    my_game.add_resource("Scrap", 50)


    print("\n--- Generating Map ---")
    my_game.generate_map(num_nodes=3) # Generate a map with 3 nodes

    # Create and Add Survivors
    survivor_alice = Survivor(name="Alice", con_val=7, san_val=6)
    survivor_bob = Survivor(name="Bob", con_val=9, san_val=3)
    my_game.add_survivor(survivor_alice)
    my_game.add_survivor(survivor_bob)

    # Set the starting node (always the first one in this simple generation)
    if my_game.game_map:
        start_node_id = list(my_game.game_map.keys())[0]
        my_game.set_current_node(start_node_id)

    my_game.display_game_state()

    print("\n--- Attempting to Travel ---")
    if my_game.current_node and my_game.current_node.connected_nodes:
        next_node_id = my_game.current_node.connected_nodes[0] # Pick the first connected node
        my_game.travel_to_node(next_node_id)
    else:
        print("No connected nodes available for travel.")

    my_game.display_game_state()

    print("\n--- Attempting to Travel Again (potentially to a 3rd node) ---")
    if my_game.current_node and my_game.current_node.connected_nodes:
        next_node_id = my_game.current_node.connected_nodes[0] # Pick the first connected node
        my_game.travel_to_node(next_node_id)
    else:
        print("No connected nodes available for travel.")

    my_game.display_game_state()