"""Multimodal route planning over the simplified MRT/bus network in
app.data.stations. Finds a path of services (MRT lines and/or bus routes)
connecting an origin place to a destination place, changing service at
shared stops (interchanges).
"""

from collections import deque

from app.data.stations import LINES, BUS_SERVICES


def _service_map():
    services = {}
    for code, line in LINES.items():
        services[f"MRT:{code}"] = set(line["stations"])
    for no, svc in BUS_SERVICES.items():
        services[f"BUS:{no}"] = set(svc["stops"])
    return services


def services_serving(place):
    return [key for key, stops in _service_map().items() if place in stops]


def find_route(origin, destination, avoid=None):
    """Return a list of legs [{service, from, to}] describing how to travel
    from origin to destination, or None if no route / unknown place.

    `avoid` is an optional set of service keys (e.g. {"MRT:NSL"}) to route
    around -- used to suggest alternatives when a line is disrupted.
    """
    if origin == destination:
        return None

    avoid = avoid or set()
    services = {k: v for k, v in _service_map().items() if k not in avoid}
    start_services = [s for s in services_serving(origin) if s not in avoid]
    goal_services = {s for s in services_serving(destination) if s not in avoid}
    if not start_services or not goal_services:
        return None

    direct = set(start_services) & goal_services
    if direct:
        return [{"service": sorted(direct)[0], "from": origin, "to": destination}]

    visited = set(start_services)
    queue = deque((svc, [svc]) for svc in start_services)
    while queue:
        svc, path = queue.popleft()
        for other, stops in services.items():
            if other in visited:
                continue
            if services[svc] & stops:
                if other in goal_services:
                    return _build_legs(path + [other], services, origin, destination)
                visited.add(other)
                queue.append((other, path + [other]))
    return None


def _build_legs(service_path, services, origin, destination):
    legs = []
    stop_at = origin
    for i in range(len(service_path) - 1):
        cur, nxt = service_path[i], service_path[i + 1]
        interchange = sorted(services[cur] & services[nxt])[0]
        legs.append({"service": cur, "from": stop_at, "to": interchange})
        stop_at = interchange
    legs.append({"service": service_path[-1], "from": stop_at, "to": destination})
    return legs


def leg_label(leg):
    kind, code = leg["service"].split(":", 1)
    if kind == "MRT":
        return f"{LINES[code]['name']} ({code})"
    return f"Bus {code}"
