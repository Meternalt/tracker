from flask import Flask, render_template, jsonify, request
from src.services.game_engine import GameEngine

app = Flask(__name__, template_folder="templates", static_folder="static")
engine = GameEngine()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    c = engine.character
    return jsonify({
        "name": c.name,
        "level": c.level,
        "xp": c.xp,
        "xp_max": c.xp_max,
        "hp": c.hp,
        "hp_max": c.hp_max,
        "gold": c.gold,
        "freeze": c.freeze_charges,
        "habits": [
            {
                "name": h.name,
                "streak": h.streak,
                "xp_reward": h.xp_reward,
                "done_today": h.is_done_today(),
            }
            for h in engine.habits
        ],
    })


@app.route("/api/complete", methods=["POST"])
def api_complete():
    name = request.json["name"]
    msg = engine.complete_habit(name)
    return jsonify({"message": msg})


@app.route("/api/new_habit", methods=["POST"])
def api_new_habit():
    data = request.json
    engine.add_habit(data["name"], data["difficulty"])
    return jsonify({"ok": True})


@app.route("/api/save", methods=["POST"])
def api_save():
    engine.save()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)