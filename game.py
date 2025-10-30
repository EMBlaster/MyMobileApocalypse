from survivor import Survivor # We'll need to import our Survivor class
from utils import roll_dice, chance_check # We'll likely use these soon, good to include

class Game:
    def __init__(self, start_day=1):
        self.game_day = start_day
        self.survivors: list[Survivor] = [] # List to hold Survivor objects
        self.global_resources: dict[str, int] = {
            "Food": 0,
            "Water": 0,
            "Fuel": 0,
            "Scrap": 0,
            "Ammunition": 0
        } # Dictionary for global resources (resource_name: quantity)
        self.current_node = None # Placeholder for the current map node
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

    def display_game_state(self):
        """Prints a summary of the current game state."""
        print("\n--- Current Game State ---")
        print(f"Game Day: {self.game_day}")
        print(f"Survivors: {len(self.survivors)}")
        for i, survivor in enumerate(self.survivors):
            print(f"  {i+1}. {survivor.name} (HP: {survivor.current_hp:.2f}/{survivor.max_hp:.2f}, Stress: {survivor.current_stress:.2f}/{survivor.max_stress:.2f})")
        print("Global Resources:")
        for res, qty in self.global_resources.items():
            print(f"  {res}: {qty}")
        print(f"Current Node: {self.current_node.name if self.current_node else 'None'}")
        print(f"Player Vehicle: {self.player_vehicle.name if self.player_vehicle else 'None'}")
        print("--------------------------")

# --- Example Usage (for testing the Game class) ---
if __name__ == "__main__":
    print("--- Initializing Game ---")
    my_game = Game()

    print("\n--- Creating and Adding Survivors ---")
    survivor_alice = Survivor(name="Alice", con_val=7, san_val=6)
    survivor_bob = Survivor(name="Bob", con_val=9, san_val=3)

    my_game.add_survivor(survivor_alice)
    my_game.add_survivor(survivor_bob)

    print("\n--- Adding and Removing Resources ---")
    my_game.add_resource("Food", 100)
    my_game.add_resource("Water", 75)
    my_game.add_resource("Scrap", 50)
    my_game.add_resource("Fuel", 20)
    my_game.remove_resource("Food", 30)
    my_game.remove_resource("Ammunition", 5) # Should fail as not enough

    # Display the current state
    my_game.display_game_state()

    print("\n--- Advancing a Day (placeholder for actual day logic) ---")
    my_game.game_day += 1
    my_game.display_game_state()

    # Demonstrating simple utility usage
    print("\n--- Testing utilities from Game context ---")
    print(f"A D6 roll (via utils): {roll_dice(6)}")
    if chance_check(80):
        print("80% chance succeeded!")
    else:
        print("80% chance failed.")
