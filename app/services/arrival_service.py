"""Mock real-time arrival predictions and crowd levels.

Values are deterministic within a 20-second window (derived from a hash of
the service code and a coarse timestamp) so repeated polls feel "live"
without needing a background thread, and shift automatically with peak /
off-peak hours the same way LTA's actual crowd predictions do.
"""

import random
from datetime import datetime

from app.data import world_state

CROWD_LEVELS = ["low", "moderate", "high"]

PEAK_WINDOWS = [(7, 9), (18, 20)]


def _is_peak(hour):
    return any(start <= hour < end for start, end in PEAK_WINDOWS)


def _rng_for(key):
    bucket = int(datetime.now().timestamp() // 20)
    return random.Random(f"{key}:{bucket}")


def _base_crowd_weights(hour):
    if _is_peak(hour):
        return [1, 3, 6]  # low, moderate, high
    if 22 <= hour or hour < 6:
        return [7, 2, 1]
    return [3, 5, 2]


def get_mrt_arrivals(line_code):
    disruption = world_state.get_disruption(line_code)
    rng = _rng_for(f"MRT:{line_code}")
    hour = datetime.now().hour
    weights = _base_crowd_weights(hour)

    base_gap = 8 if (disruption and disruption["severity"] == "disruption") else \
        4 if (disruption and disruption["severity"] == "delay") else 2

    arrivals = []
    eta = rng.randint(1, 3) + base_gap
    for _ in range(3):
        crowd = rng.choices(CROWD_LEVELS, weights=weights, k=1)[0]
        if disruption:
            # disruptions push more commuters onto each remaining train
            crowd = CROWD_LEVELS[min(len(CROWD_LEVELS) - 1, CROWD_LEVELS.index(crowd) + 1)]
        arrivals.append({"eta_min": eta, "crowd": crowd})
        eta += rng.randint(2, 5) + base_gap
    return arrivals


def get_bus_arrivals(service_no):
    rng = _rng_for(f"BUS:{service_no}")
    hour = datetime.now().hour
    weights = _base_crowd_weights(hour)

    arrivals = []
    eta = rng.randint(2, 6)
    for _ in range(2):
        crowd = rng.choices(CROWD_LEVELS, weights=weights, k=1)[0]
        arrivals.append({"eta_min": eta, "crowd": crowd})
        eta += rng.randint(6, 14)
    return arrivals


def get_arrivals(service_key):
    kind, code = service_key.split(":", 1)
    if kind == "MRT":
        return get_mrt_arrivals(code)
    return get_bus_arrivals(code)
