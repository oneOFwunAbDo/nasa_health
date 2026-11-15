"""
Writes food_nutrients_DEMO.json with FAKE, randomly generated nutrient values so the
nutrition page can be built and tested before the real data is ready.
These numbers are NOT real nutrition facts. Never ship them.

Run:  python make_demo_data.py
Then copy/rename to food_nutrients.json to try the page with it.
"""

import json
import random
from pathlib import Path

from nutrition_data import NUTRIENTS, all_food_names

# each nutrient gets its own fixed "richness" so the demo day shows a mix of low / met / over
weight = {key: random.Random("w-" + key).uniform(0.3, 1.1) for key, *_ in NUTRIENTS}

out = {"_WARNING": "DEMO DATA - randomly generated, not real nutrition facts"}
for name in all_food_names():
    rng = random.Random(name)             # same food -> same fake numbers every run
    out[name] = {}
    for key, _en, _ar, _unit, target, _kind in NUTRIENTS:
        out[name][key] = round(rng.uniform(0, 0.2 * weight[key]) * target, 2)

path = Path(__file__).with_name("food_nutrients_DEMO.json")
path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"wrote {path.name}: {len(out) - 1} foods")
