import random # Needed for map generation
from survivor import Survivor
from utils import roll_dice, chance_check
from map_nodes import Node, AVAILABLE_NODES # New import for Node class and definitions

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
        self.game_map: dict[str, Node] = {} # New: Dictionary to store the generated map (Node ID: Node object)
        self.current_node: Node = None # Now explicitly typed as Node
        self.player_vehicle = None # Placeholder for the player's vehicle/mobile base

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
            print(f"  Connected Nodes: {', '.join(self.current_node.connected_nodes)}")
            print(f"  Hazard: {self.current_node.hazard_type if self.current_node.hazard_type else 'None'}")
        print(f"Player Vehicle: {self.player_vehicle.name if self.player_vehicle else 'None'}")
        print("--------------------------")

# --- Example Usage (for testing the Game class with map functionality) ---
if __name__ == "__main__":
    print("--- Initializing Game ---")
    my_game = Game()

    print("\n--- Generating Map ---")
    my_game.generate_map(num_nodes=3) # Generate a map with 3 nodes

    # Try to set the starting node
    if my_game.game_map:
        first_node_id = list(my_g