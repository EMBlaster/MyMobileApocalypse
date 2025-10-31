import unittest
import random
from game import Game


def is_connected(game: Game) -> bool:
    # simple BFS from any node to ensure all nodes reachable
    if not game.game_map:
        return True
    nodes = list(game.game_map.keys())
    start = nodes[0]
    visited = set()
    stack = [start]
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        for nbr in game.game_map[node_id].connected_nodes:
            if nbr not in visited:
                stack.append(nbr)
    return len(visited) == len(nodes)


class MapGenerationTests(unittest.TestCase):
    def test_generate_map_is_connected_multiple_seeds(self):
        # Run generation across several seeds to catch intermittent random behavior
        for seed in range(5):
            random.seed(seed)
            g = Game()
            g.generate_map(num_nodes=4)
            self.assertTrue(is_connected(g), f"Generated map not connected for seed {seed}: {list(g.game_map.keys())}")


if __name__ == '__main__':
    unittest.main()
