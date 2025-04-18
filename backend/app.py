from flask import Flask, jsonify
from flask_cors import CORS
from .routes.rooms import rooms_bp  # This is now a relative import
from backend.config import get_connection
from .routes.test_connection_route import test_connection_bp  # This is also a relative import
from .routes.init_db_route import init_db_bp  # Import the init_db route
from .routes.signup_db import user_bp


app = Flask(__name__)  # make sure this comes first!
CORS(app, origins=["https://yashdhaneshwari.wixsite.com", "http://localhost:5173"], methods=["GET", "POST", "OPTIONS"])

# Register blueprints
app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
app.register_blueprint(test_connection_bp) 
app.register_blueprint(init_db_bp)
app.register_blueprint(user_bp)


# TEMP: Add health check endpoint directly
@app.route("/health", methods=["GET"])
def health_check():
    try:
        conn = get_connection()
        if conn.is_connected():
            conn.close()
            return jsonify({"status": "ok", "db": "connected"}), 200
        else:
            return jsonify({"status": "error", "db": "not connected"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "RoomQuest backend is running!"})

@app.route("/api/rooms/test", methods=["GET"])
def test_rooms():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

# Optional: Add an environment debug route
# @app.route("/env", methods=["GET"])
# def show_env():
#     import os
#     return jsonify(dict(os.environ))

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
