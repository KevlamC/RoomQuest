from flask import Flask, jsonify
from flask_cors import CORS
from routes.rooms import rooms_bp
from config import get_connection
from routes.test_connection_route import test_connection_bp  # this import is fine

app = Flask(__name__)  # make sure this comes first!
CORS(app)

# Register blueprints
app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
app.register_blueprint(test_connection_bp)  # now it's safe to register this

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

# Optional: Add an environment debug route
# @app.route("/env", methods=["GET"])
# def show_env():
#     import os
#     return jsonify(dict(os.environ))

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
