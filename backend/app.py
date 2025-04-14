from flask import Flask
from flask_cors import CORS
from routes.rooms import rooms_bp  # import your rooms blueprint

app = Flask(__name__)
CORS(app)  # Enable CORS so Wix can connect

# Register blueprints
app.register_blueprint(rooms_bp, url_prefix="/api/rooms")

if __name__ == "__main__":
    app.run(debug=True)
