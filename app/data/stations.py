"""Static reference data: a simplified model of Singapore's rail lines,
bus services and regions. Trimmed to a demo-sized subset of real station
and place names -- enough to exercise routing/interchange logic without
encoding the full rail network.
"""

LINES = {
    "NSL": {
        "name": "North South Line",
        "color": "#D42E12",
        "stations": [
            "Jurong East", "Bukit Batok", "Bishan", "Toa Payoh",
            "Novena", "Orchard", "City Hall", "Raffles Place", "Marina Bay",
        ],
    },
    "EWL": {
        "name": "East West Line",
        "color": "#009645",
        "stations": [
            "Boon Lay", "Jurong East", "Buona Vista", "Outram Park",
            "Raffles Place", "City Hall", "Paya Lebar", "Tampines", "Pasir Ris",
        ],
    },
    "NEL": {
        "name": "North East Line",
        "color": "#9900AA",
        "stations": [
            "Punggol", "Hougang", "Serangoon", "Little India",
            "Dhoby Ghaut", "Clarke Quay", "Outram Park", "HarbourFront",
        ],
    },
    "CCL": {
        "name": "Circle Line",
        "color": "#FA9E0D",
        "stations": [
            "HarbourFront", "Buona Vista", "Botanic Gardens", "Serangoon",
            "Bishan", "Paya Lebar", "Dhoby Ghaut",
        ],
    },
    "DTL": {
        "name": "Downtown Line",
        "color": "#005EC4",
        "stations": [
            "Bukit Panjang", "Botanic Gardens", "Newton", "Little India",
            "Bugis", "Chinatown", "Tampines", "Expo",
        ],
    },
    "TEL": {
        "name": "Thomson-East Coast Line",
        "color": "#9D5B25",
        "stations": [
            "Woodlands", "Caldecott", "Orchard", "Outram Park", "Marina Bay",
        ],
    },
}

BUS_SERVICES = {
    "67": {"stops": ["Jurong East", "Clementi", "Buona Vista", "Orchard", "City Hall"]},
    "174": {"stops": ["Woodlands", "Bukit Panjang", "Bukit Batok", "Jurong East"]},
    "851": {"stops": ["Punggol", "Hougang", "Serangoon", "Bishan"]},
    "961": {"stops": ["Pasir Ris", "Tampines", "Paya Lebar", "Novena"]},
    "196": {"stops": ["Tanjong Pagar", "Raffles Place", "City Hall", "Orchard", "Newton"]},
}

REGIONS = ["North", "South", "East", "West", "Central"]

STATION_REGION = {
    "Jurong East": "West", "Bukit Batok": "West", "Boon Lay": "West",
    "Buona Vista": "West", "Bukit Panjang": "West", "Clementi": "West",
    "Bishan": "Central", "Toa Payoh": "Central", "Novena": "Central",
    "Orchard": "Central", "City Hall": "Central", "Raffles Place": "Central",
    "Marina Bay": "Central", "Dhoby Ghaut": "Central", "Newton": "Central",
    "Little India": "Central", "Bugis": "Central", "Chinatown": "Central",
    "Clarke Quay": "Central", "Outram Park": "Central", "Tanjong Pagar": "Central",
    "HarbourFront": "Central", "Botanic Gardens": "Central",
    "Punggol": "North East", "Hougang": "North East", "Serangoon": "North East",
    "Paya Lebar": "East", "Tampines": "East", "Pasir Ris": "East", "Expo": "East",
    "Woodlands": "North", "Caldecott": "North",
}


def all_stations():
    seen = {}
    for code, line in LINES.items():
        for station in line["stations"]:
            seen.setdefault(station, set()).add(code)
    return seen  # station name -> set of line codes serving it (interchange if len > 1)


def all_places():
    """Union of MRT stations and bus stops, sorted, for planner dropdowns."""
    places = set(all_stations().keys())
    for svc in BUS_SERVICES.values():
        places.update(svc["stops"])
    return sorted(places)


def region_for(place):
    return STATION_REGION.get(place, "Central")


def lines_serving(station):
    return sorted(all_stations().get(station, set()))


def bus_services_serving(place):
    return sorted(no for no, svc in BUS_SERVICES.items() if place in svc["stops"])
