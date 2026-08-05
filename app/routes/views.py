from flask import Blueprint, redirect, render_template, request, url_for

from app.data import world_state
from app.data.stations import LINES, REGIONS, all_places
from app.services import recommendation_engine, route_service

views_bp = Blueprint("views", __name__)

DEFAULT_ORIGIN = "Woodlands"
DEFAULT_DESTINATION = "Raffles Place"


@views_bp.get("/")
def dashboard():
    origin = request.args.get("origin") or DEFAULT_ORIGIN
    destination = request.args.get("destination") or DEFAULT_DESTINATION

    route, route_error = None, None
    recs, summary = [], None
    if origin != destination:
        route = route_service.find_route(origin, destination)
        if route:
            recs, summary = recommendation_engine.build_recommendations(route)
        else:
            route_error = f"No route found between {origin} and {destination}."
    else:
        route_error = "Origin and destination must be different."

    disruptions = world_state.all_disruptions()
    lines = [
        {
            "code": code,
            "name": line["name"],
            "color": line["color"],
            "status": disruptions.get(code),
        }
        for code, line in LINES.items()
    ]

    weather = world_state.all_weather()
    works = sorted(world_state.planned_works(), key=lambda w: w["start"])

    return render_template(
        "dashboard.html",
        places=all_places(),
        origin=origin,
        destination=destination,
        route=[{**leg, "label": route_service.leg_label(leg)} for leg in route] if route else None,
        route_error=route_error,
        recommendations=recs,
        summary=summary,
        lines=lines,
        weather=weather,
        regions=REGIONS,
        planned_works=works,
        line_choices=LINES,
    )


def _back_to_dashboard():
    origin = request.form.get("origin") or DEFAULT_ORIGIN
    destination = request.form.get("destination") or DEFAULT_DESTINATION
    return redirect(url_for("views.dashboard", origin=origin, destination=destination))


@views_bp.post("/simulate/disruption")
def simulate_disruption():
    line = request.form.get("line")
    severity = request.form.get("severity", "delay")
    message = request.form.get("message") or (
        f"{LINES.get(line, {}).get('name', line)} is experiencing {severity}."
    )
    if line in LINES:
        world_state.set_disruption(line, severity, message)
    return _back_to_dashboard()


@views_bp.post("/simulate/clear-disruption")
def simulate_clear_disruption():
    world_state.clear_disruption(request.form.get("line"))
    return _back_to_dashboard()


@views_bp.post("/simulate/weather")
def simulate_weather():
    region = request.form.get("region")
    condition = request.form.get("condition", "clear")
    if region in REGIONS:
        world_state.set_weather(region, condition)
    return _back_to_dashboard()


@views_bp.post("/simulate/reset")
def simulate_reset():
    world_state.reset_all()
    return _back_to_dashboard()
