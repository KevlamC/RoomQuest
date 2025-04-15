from flask import Flask, jsonify
from flask_cors import CORS
from routes.rooms import rooms_bp  # import your rooms blueprint
from config import get_connection  # to check DB connection

app = Flask(__name__)
CORS(app)  # Enable CORS so Wix can connect

# Register blueprints
app.register_blueprint(rooms_bp, url_prefix="/api/rooms")

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

if __name__ == "__main__":
    app.run(debug=True)
