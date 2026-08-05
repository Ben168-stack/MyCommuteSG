"""Core decision-support logic: turns a planned route plus the current
world state (disruptions, weather, planned works, live-ish arrivals) into
a ranked list of proactive recommendations for the commuter.
"""

from datetime import datetime, timedelta

from app.data import world_state
from app.data.stations import region_for
from app.services import arrival_service, route_service

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


def _mrt_legs(route):
    return [leg for leg in route if leg["service"].startswith("MRT:")]


def _regions_on_route(route):
    regions = set()
    for leg in route:
        regions.add(region_for(leg["from"]))
        regions.add(region_for(leg["to"]))
    return regions


def _disruption_recommendations(route):
    recs = []
    for leg in _mrt_legs(route):
        code = leg["service"].split(":", 1)[1]
        disruption = world_state.get_disruption(code)
        if not disruption:
            continue
        severity = "critical" if disruption["severity"] == "disruption" else "warning"
        alt_route = route_service.find_route(route[0]["from"], route[-1]["to"], avoid={leg["service"]})
        if alt_route:
            alt_desc = " then ".join(route_service.leg_label(l) for l in alt_route)
            action = f"Suggested alternative: {alt_desc}."
        else:
            action = disruption.get("alt_advice") or "Consider a taxi/ride-hail or delaying non-essential trips."

        recs.append({
            "severity": severity,
            "category": "disruption",
            "title": f"{route_service.leg_label(leg)} {disruption['severity']}",
            "message": disruption["message"],
            "action": action,
        })
    return recs


def _weather_recommendations(route):
    recs = []
    regions = _regions_on_route(route)
    seen_conditions = set()
    for region in regions:
        condition = world_state.get_weather(region)
        if condition == "clear" or condition in seen_conditions:
            continue
        seen_conditions.add(condition)
        if condition == "heavy_rain":
            recs.append({
                "severity": "warning",
                "category": "weather",
                "title": f"Heavy rain over {region} Singapore",
                "message": "Heavy rain may slow buses and surface transfers, and surge ride-hail pricing.",
                "action": "Bring an umbrella, favour sheltered MRT-to-mall transfers, and budget extra transfer time.",
            })
        elif condition == "light_rain":
            recs.append({
                "severity": "info",
                "category": "weather",
                "title": f"Light rain over {region} Singapore",
                "message": "Light rain in the area of your route.",
                "action": "Bring an umbrella for the walking segments of your trip.",
            })
    return recs


def _crowd_recommendations(route):
    if not route:
        return []
    first_leg = route[0]
    arrivals = arrival_service.get_arrivals(first_leg["service"])
    if not arrivals:
        return []

    label = route_service.leg_label(first_leg)
    next_train = arrivals[0]
    recs = []

    if next_train["crowd"] == "high" and len(arrivals) > 1:
        for later in arrivals[1:]:
            if later["crowd"] in ("low", "moderate"):
                recs.append({
                    "severity": "info",
                    "category": "crowd",
                    "title": f"{label} is crowded right now",
                    "message": f"The next {label} arrives in {next_train['eta_min']} min and looks crowded.",
                    "action": f"Consider waiting {later['eta_min']} min for a less crowded ride instead.",
                })
                break
        else:
            recs.append({
                "severity": "info",
                "category": "crowd",
                "title": f"{label} is crowded right now",
                "message": f"The next {label} arrives in {next_train['eta_min']} min and looks crowded, "
                            "and later services look similarly busy.",
                "action": "Leave a little earlier than usual to have a buffer.",
            })
    else:
        recs.append({
            "severity": "info",
            "category": "crowd",
            "title": f"{label} looks good to go",
            "message": f"The next {label} arrives in {next_train['eta_min']} min with {next_train['crowd']} crowding.",
            "action": "Leave now to catch it comfortably.",
        })
    return recs


def _planned_works_recommendations(route):
    recs = []
    line_codes = {leg["service"].split(":", 1)[1] for leg in _mrt_legs(route)}
    regions = _regions_on_route(route)
    now = datetime.now()
    horizon = now + timedelta(days=3)

    for work in world_state.planned_works():
        in_scope = (
            (work["scope_type"] == "line" and work["scope"] in line_codes) or
            (work["scope_type"] == "road" and work["scope"] in regions)
        )
        if not in_scope:
            continue
        if not (now <= work["start"] <= horizon):
            continue

        when = work["start"].strftime("%a %d %b, %I:%M%p")
        recs.append({
            "severity": "info",
            "category": "planned_works",
            "title": work["title"],
            "message": f"{work['description']} Starts {when}.",
            "action": work["advisory"],
        })
    return recs


def leave_by_recommendation(route):
    if not route:
        return None
    arrivals = arrival_service.get_arrivals(route[0]["service"])
    if not arrivals:
        return None
    eta = arrivals[0]["eta_min"]
    leave_by = (datetime.now() + timedelta(minutes=max(eta - 2, 0))).strftime("%I:%M %p")
    return {
        "severity": "info",
        "category": "summary",
        "title": "Recommended departure",
        "message": f"Leave by {leave_by} to catch the next {route_service.leg_label(route[0])}.",
        "action": "",
    }


def build_recommendations(route):
    """Return (recommendations, summary) for a planned route, sorted with
    the most urgent/actionable items first."""
    if not route:
        return [], None

    recs = []
    summary = leave_by_recommendation(route)
    recs.extend(_disruption_recommendations(route))
    recs.extend(_weather_recommendations(route))
    recs.extend(_crowd_recommendations(route))
    recs.extend(_planned_works_recommendations(route))

    recs.sort(key=lambda r: SEVERITY_ORDER.get(r["severity"], 3))
    return recs, summary
