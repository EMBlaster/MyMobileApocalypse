import logging

logger = logging.getLogger(__name__)


class Node:
    """
    Represents a single location on the game map.
    """
    def __init__(self, id: str, name: str, description: str, danger_level: int,
                 hazard_type: str = None, connected_nodes: list = None,
                 potential_quests: list = None, available_resources: dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.danger_level = danger_level # e.g., 1-5, affects event difficulty
        self.hazard_type = hazard_type # e.g., "Plague Cloud", "Fire", "Fog", None
        self.connected_nodes = connected_nodes if connected_nodes is not None else [] # List of Node IDs
        self.potential_quests = potential_quests if potential_quests is not None else [] # List of Quest IDs
        # Resources that can be found or harvested at this node (resource_name: quantity)
        self.available_resources = available_resources if available_resources is not None else {}
        self.is_visited = False # To track if the node has been visited in the current run

    def __str__(self):
        return f"Node(ID: {self.id}, Name: {self.name}, Danger: {self.danger_level})"

    def __repr__(self):
        return self.id

# --- Global Dictionary of Available Map Nodes (for defining the world) ---
# This will eventually be used to construct dynamic maps, but for now serves as a blueprint.

AVAILABLE_NODES = {
    "city_outskirts_01": Node(
        id="city_outskirts_01",
        name="Abandoned Gas Station",
        description="A derelict gas station on the city's edge. Might have fuel, but also attracts looters.",
        danger_level=2,
        hazard_type=None,
        connected_nodes=["suburban_ruins_01", "highway_access_01"],
        potential_quests=["ScavengeFuel", "FindMissingTrader"],
        available_resources={"Fuel": 30, "Scrap": 20, "Water": 10}
    ),
    "suburban_ruins_01": Node(
        id="suburban_ruins_01",
        name="Collapsed Suburban Homes",
        description="Once a quiet neighborhood, now a maze of debris and lurking shadows. Good for food.",
        danger_level=3,
        hazard_type=None,
        connected_nodes=["city_outskirts_01", "downtown_perimeter_01"],
        potential_quests=["ClearOutInfestation", "RescueSurvivor"],
        available_resources={"Food": 40, "Scrap": 30, "Bandage": 5}
    ),
    "highway_access_01": Node(
        id="highway_access_01",
        name="Overgrown Highway Entrance",
        description="The main road into the city, now choked with abandoned cars. Dangerous, but a direct route.",
        danger_level=4,
        hazard_type="Fog", # Example hazard
        connected_nodes=["city_outskirts_01", "industrial_zone_01"],
        potential_quests=["ScoutNewRoute", "RetrieveSupplies"],
        available_resources={"Scrap": 60, "Fuel": 15}
    ),
    "industrial_zone_01": Node(
        id="industrial_zone_01",
        name="Decayed Factory Complex",
        description="Rusting machinery and collapsing structures. High risk, but potentially rich in parts and materials.",
        danger_level=5,
        hazard_type="Plague Cloud", # Example hazard
        connected_nodes=["highway_access_01", "downtown_center_01"],
        potential_quests=["SecureFactory", "FindRareComponents"],
        available_resources={"Scrap": 100, "ElectronicParts": 40} # Example for future items
    ),
    "downtown_perimeter_01": Node(
        id="downtown_perimeter_01",
        name="Wrecked Office Blocks",
        description="The edges of downtown. Tall buildings, fallen debris. Zombies are common here.",
        danger_level=4,
        hazard_type=None,
        connected_nodes=["suburban_ruins_01", "downtown_center_01", "hospital_district_01"],
        potential_quests=["ScavengeDocuments", "EliminateSnipers"],
        available_resources={"Scrap": 50, "Ammunition": 10}
    ),
    "downtown_center_01": Node(
        id="downtown_center_01",
        name="Collapsed City Center",
        description="The heart of the city, utterly devastated. Extremely dangerous, but holds the greatest secrets.",
        danger_level=5,
        hazard_type="Fire", # Example hazard
        connected_nodes=["industrial_zone_01", "downtown_perimeter_01"],
        potential_quests=["ReachEvacZone", "ResearchCure"],
        available_resources={"RareMetals": 20, "HighTechScrap": 15} # Example for future rare items
    ),
}


# --- Example Usage (for testing the Node class) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Available Nodes ---")
    for node_id, node in AVAILABLE_NODES.items():
        logger.info("\nID: %s", node.id)
        logger.info("Name: %s", node.name)
        logger.info("Description: %s", node.description)
        logger.info("Danger Level: %s", node.danger_level)
        logger.info("Hazard Type: %s", node.hazard_type if node.hazard_type else 'None')
        logger.info("Connected Nodes: %s", ', '.join(node.connected_nodes))
        logger.info("Potential Quests: %s", ', '.join(node.potential_quests) if node.potential_quests else 'None')
        logger.info("Available Resources: %s", node.available_resources)
        logger.info("Visited: %s", node.is_visited)

    # Example of accessing a specific node
    gas_station = AVAILABLE_NODES["city_outskirts_01"]
    logger.info("\nDetails for %s:", gas_station.name)
    logger.info("Connected to: %s", gas_station.connected_nodes)
    logger.info("Resources: %s", gas_station.available_resources)

    # Simulating visiting a node
    gas_station.is_visited = True
    logger.info("Visited status for %s: %s", gas_station.name, gas_station.is_visited)