"""In-memory, mutable "world state": the mock stand-in for live LTA feeds
(service alerts, weather nowcast, planned works). A single process-wide
instance is mutated either by the background-feeling mock scheduler or by
the demo "Simulate Event" control panel, and read by the recommendation
engine on every request.
"""

import threading
import uuid
from datetime import datetime, timedelta

from app.data.stations import LINES, REGIONS

_lock = threading.Lock()

_state = {
    "disruptions": {},   # line_code -> {severity, message, alt_advice, since}
    "weather": {region: "clear" for region in REGIONS},
    "planned_works": [],  # list of dicts, see _seed_planned_works
}


def _seed():
    now = datetime.now()
    _state["planned_works"] = [
        {
            "id": str(uuid.uuid4())[:8],
            "scope_type": "line",
            "scope": "DTL",
            "title": "Late-night signalling upgrade",
            "description": "DTL trains will end service 1 hour early and run at "
                            "wider intervals for signalling upgrading works.",
            "start": now + timedelta(days=2, hours=-now.hour, minutes=-now.minute),
            "end": now + timedelta(days=2, hours=-now.hour + 4, minutes=-now.minute),
            "advisory": "Plan to leave earlier, or use EWL/NSL as an alternative on that night.",
        },
        {
            "id": str(uuid.uuid4())[:8],
            "scope_type": "road",
            "scope": "Central",
            "title": "Weekend road closure near City Hall",
            "description": "Road closures around City Hall for a community run on "
                            "Sunday morning will affect bus routings and nearby traffic.",
            "start": now + timedelta(days=(6 - now.weekday()) % 7 or 7, hours=-now.hour, minutes=-now.minute),
            "end": now + timedelta(days=(6 - now.weekday()) % 7 or 7, hours=-now.hour + 5, minutes=-now.minute),
            "advisory": "Avoid driving through Central on Sunday morning; MRT is unaffected.",
        },
    ]
    _state["weather"]["East"] = "light_rain"


_seed()


def snapshot():
    with _lock:
        return {
            "disruptions": dict(_state["disruptions"]),
            "weather": dict(_state["weather"]),
            "planned_works": [dict(w) for w in _state["planned_works"]],
        }


def get_disruption(line_code):
    with _lock:
        return _state["disruptions"].get(line_code)


def all_disruptions():
    with _lock:
        return dict(_state["disruptions"])


def set_disruption(line_code, severity, message, alt_advice=""):
    with _lock:
        _state["disruptions"][line_code] = {
            "severity": severity,  # "delay" | "disruption"
            "message": message,
            "alt_advice": alt_advice,
            "since": datetime.now().isoformat(timespec="minutes"),
        }


def clear_disruption(line_code):
    with _lock:
        _state["disruptions"].pop(line_code, None)


def clear_all_disruptions():
    with _lock:
        _state["disruptions"].clear()


def get_weather(region):
    with _lock:
        return _state["weather"].get(region, "clear")


def all_weather():
    with _lock:
        return dict(_state["weather"])


def set_weather(region, condition):
    with _lock:
        _state["weather"][region] = condition


def reset_weather():
    with _lock:
        for region in REGIONS:
            _state["weather"][region] = "clear"


def planned_works():
    with _lock:
        return [dict(w) for w in _state["planned_works"]]


def add_planned_work(work):
    with _lock:
        work["id"] = str(uuid.uuid4())[:8]
        _state["planned_works"].append(work)
        return work["id"]


def reset_all():
    with _lock:
        _state["disruptions"].clear()
        for region in REGIONS:
            _state["weather"][region] = "clear"
    _seed()


def line_name(code):
    return LINES.get(code, {}).get("name", code)
