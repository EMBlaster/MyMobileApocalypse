import sys
from pathlib import Path

# Ensure repo root on sys.path
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
	sys.path.insert(0, repo_root)

import character_creator
print('create_new_survivor exists?', hasattr(character_creator, 'create_new_survivor'))
print('create_pregenerated_survivor exists?', hasattr(character_creator, 'create_pregenerated_survivor'))
