from flask import Blueprint, jsonify
from backend.config import get_connection

init_db_bp = Blueprint('init_db', __name__)

@init_db_bp.route('/init-db', methods=['GET'])
def init_db():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # --- Example schema ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            capacity INT NOT NULL
        );
        """)

        # Insert test data
        cursor.execute("INSERT INTO rooms (name, capacity) VALUES ('Room A', 10);")
        cursor.execute("INSERT INTO rooms (name, capacity) VALUES ('Room B', 20);")
        cursor.execute("INSERT INTO rooms (name, capacity) VALUES ('Room C', 15);")

        connection.commit()
        
        # --- Retrieve and print inserted rows ---
        cursor.execute("SELECT * FROM rooms;")
        results = cursor.fetchall()
        rooms_data = []
        for row in results:
            rooms_data.append(f"ID: {row[0]}, Name: {row[1]}, Capacity: {row[2]}")
        
        # Drop table after retrieval
        cursor.execute("DROP TABLE IF EXISTS rooms;")
        
        cursor.close()
        connection.close()

        # Return results to the browser
        return jsonify({
            "message": "Tables created and test data inserted successfully.",
            "rooms": rooms_data,
            "table_dropped": "Table 'rooms' dropped successfully."
        })
    
    except Exception as e:
        return jsonify({
            "message": "Error occurred",
            "error": str(e)
        })
