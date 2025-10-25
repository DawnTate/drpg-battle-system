
"""
Load configuration from config.json with safe defaults.
Import CFG from this module anywhere you need configuration values.
"""

import json, os

_DEFAULTS = {
    "treasure": {
        "chest_per_floor": 1,
        "mimic_chance": 0.30,
        "heal_rate": 0.30,
        "gamble_attr_count_min": 1,
        "gamble_attr_count_max": 3,
        "backfire_prob": 0.20,
        "mimic_boost_bias": 0.20,
    }
}

def _deep_update(dst: dict, src: dict) -> dict:
    """Recursively update dst with src; non-dict values overwrite directly."""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v
    return dst

def load_config() -> dict:
    """Load user config from config.json, fall back to defaults if missing."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, "config.json")
    cfg = json.loads(json.dumps(_DEFAULTS))  # deep copy defaults
    try:
        with open(path, "r", encoding="utf-8") as f:
            user = json.load(f)
        _deep_update(cfg, user)
    except Exception as e:
        print(f"[config] Using defaults ({e})")
    return cfg

# Public singleton
CFG = load_config()
