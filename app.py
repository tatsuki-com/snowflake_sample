from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'match-me-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
messages = {}
online_users = set()

INTERESTS = [
    "Music", "Sports", "Travel", "Cooking", "Reading",
    "Gaming", "Art", "Movies", "Tech", "Fitness",
    "Photography", "Nature", "Fashion", "Science", "Food"
]

SEED_USERS = [
    {"id": "demo001", "name": "Alice",   "interests": ["Music", "Travel", "Photography", "Art"]},
    {"id": "demo002", "name": "Bob",     "interests": ["Gaming", "Tech", "Movies", "Science"]},
    {"id": "demo003", "name": "Carol",   "interests": ["Cooking", "Food", "Travel", "Nature"]},
    {"id": "demo004", "name": "Dave",    "interests": ["Fitness", "Sports", "Nature", "Travel"]},
    {"id": "demo005", "name": "Eve",     "interests": ["Reading", "Science", "Art", "Music"]},
]

for u in SEED_USERS:
    users[u["id"]] = {"name": u["name"], "interests": u["interests"], "created_at": "seed"}


def get_matches(user_id):
    if user_id not in users:
        return []
    user_interests = set(users[user_id]["interests"])
    matches = []
    for uid, udata in users.items():
        if uid == user_id:
            continue
        common = user_interests & set(udata["interests"])
        if common:
            matches.append({
                "id": uid,
                "name": udata["name"],
                "interests": udata["interests"],
                "common": sorted(common),
                "score": len(common),
                "online": uid in online_users,
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def get_room_id(id1, id2):
    return "_".join(sorted([id1, id2]))


@app.route("/")
def index():
    if "user_id" in session and session["user_id"] in users:
        return redirect(url_for("chat"))
    return render_template("index.html", interests=INTERESTS)


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = (data.get("name") or "").strip()
    interests = data.get("interests") or []
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if len(interests) < 2:
        return jsonify({"error": "Please select at least 2 interests"}), 400
    user_id = str(uuid.uuid4())[:8]
    users[user_id] = {"name": name, "interests": interests, "created_at": datetime.now().isoformat()}
    session["user_id"] = user_id
    return jsonify({"user_id": user_id, "redirect": "/chat"})


@app.route("/chat")
def chat():
    if "user_id" not in session or session["user_id"] not in users:
        return redirect(url_for("index"))
    user_id = session["user_id"]
    user = users[user_id]
    matches = get_matches(user_id)
    return render_template("chat.html", user=user, user_id=user_id, matches=matches)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/api/matches")
def api_matches():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(get_matches(session["user_id"]))


@app.route("/api/messages/<room_id>")
def api_messages(room_id):
    return jsonify(messages.get(room_id, []))


@socketio.on("connect")
def handle_connect():
    if "user_id" in session:
        online_users.add(session["user_id"])
        emit("status", {"online": list(online_users)}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    if "user_id" in session:
        online_users.discard(session["user_id"])
        emit("status", {"online": list(online_users)}, broadcast=True)


@socketio.on("join")
def handle_join(data):
    if "user_id" not in session:
        return
    other_id = data.get("user_id")
    if other_id:
        join_room(get_room_id(session["user_id"], other_id))


@socketio.on("message")
def handle_message(data):
    if "user_id" not in session:
        return
    user_id = session["user_id"]
    other_id = data.get("to")
    text = (data.get("text") or "").strip()
    if not text or not other_id:
        return
    room = get_room_id(user_id, other_id)
    msg = {
        "from": user_id,
        "from_name": users[user_id]["name"],
        "text": text,
        "timestamp": datetime.now().strftime("%H:%M"),
    }
    messages.setdefault(room, []).append(msg)
    emit("message", msg, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
