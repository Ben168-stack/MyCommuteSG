from flask import Blueprint, jsonify, request

from app.data import world_state
from app.data.stations import LINES, REGIONS, all_places
from app.services import recommendation_engine, route_service

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/places")
def places():
    return jsonify(all_places())


@api_bp.get("/route")
def get_route():
    origin = request.args.get("origin", "")
    destination = request.args.get("destination", "")
    if not origin or not destination:
        return jsonify({"error": "origin and destination are required"}), 400

    route = route_service.find_route(origin, destination)
    if not route:
        return jsonify({"error": f"No route found between {origin} and {destination}"}), 404

    recs, summary = recommendation_engine.build_recommendations(route)
    return jsonify({
        "origin": origin,
        "destination": destination,
        "legs": [{**leg, "label": route_service.leg_label(leg)} for leg in route],
        "summary": summary,
        "recommendations": recs,
    })


@api_bp.get("/lines/status")
def lines_status():
    disruptions = world_state.all_disruptions()
    return jsonify({
        code: {
            "name": line["name"],
            "color": line["color"],
            "status": disruptions.get(code, {"severity": "normal", "message": "Good service"}),
        }
        for code, line in LINES.items()
    })


@api_bp.get("/weather")
def weather():
    return jsonify(world_state.all_weather())


@api_bp.get("/planned-works")
def planned_works():
    works = world_state.planned_works()
    for w in works:
        w["start"] = w["start"].isoformat(timespec="minutes")
        w["end"] = w["end"].isoformat(timespec="minutes")
    return jsonify(works)


@api_bp.post("/simulate/disruption")
def simulate_disruption():
    data = request.get_json(force=True, silent=True) or request.form
    line = data.get("line")
    severity = data.get("severity", "delay")
    message = data.get("message") or f"{LINES.get(line, {}).get('name', line)} is experiencing {severity}."
    if line not in LINES:
        return jsonify({"error": "unknown line"}), 400
    world_state.set_disruption(line, severity, message)
    return jsonify({"ok": True})


@api_bp.post("/simulate/clear-disruption")
def simulate_clear_disruption():
    data = request.get_json(force=True, silent=True) or request.form
    line = data.get("line")
    world_state.clear_disruption(line)
    return jsonify({"ok": True})


@api_bp.post("/simulate/weather")
def simulate_weather():
    data = request.get_json(force=True, silent=True) or request.form
    region = data.get("region")
    condition = data.get("condition", "clear")
    if region not in REGIONS:
        return jsonify({"error": "unknown region"}), 400
    world_state.set_weather(region, condition)
    return jsonify({"ok": True})


@api_bp.post("/simulate/reset")
def simulate_reset():
    world_state.reset_all()
    return jsonify({"ok": True})
