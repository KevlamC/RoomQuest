from flask import Blueprint, request, jsonify, render_template_string 
from backend.config import get_connection

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        user_id = data.get('id')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if ID already exists
        cursor.execute("SELECT 1 FROM USER WHERE ID = %s", (user_id,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "ID already exists."}), 400

        # Check if Email already exists
        cursor.execute("SELECT 1 FROM USER WHERE Email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already registered."}), 400

        # Check if Username already exists
        cursor.execute("SELECT 1 FROM USER WHERE Username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Username already taken."}), 400

        # Insert new user
        cursor.execute("""
            INSERT INTO USER (ID, Email, Username, Password)
            VALUES (%s, %s, %s, %s)
        """, (user_id, email, username, password))
        
        cursor.execute("""
            INSERT INTO STUDENT (ID, Points)
            VALUES (%s, 0)
        """, (user_id,))


        connection.commit()

        # Fetch the ID of the newly inserted user
        cursor.execute("SELECT ID, Email, Username, Password, userType FROM USER WHERE Email = %s", (email,))
        inserted_user = cursor.fetchone()

        cursor.close()
        connection.close()

        if inserted_user:
            return jsonify({
                "success": True,
                "message": "User inserted successfully.",
                "user_id": inserted_user["ID"],
                "username": inserted_user["Username"],
                "userType": inserted_user["userType"]
            })
        else:
            return jsonify({
                "success": False,
                "message": "User inserted but could not retrieve inserted data."
            }), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

# Route to display all users in the USER table (now includes Password)
@user_bp.route('/view-users', methods=['GET'])
def view_users():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # ✅ Change 1: Include Password in the SELECT
        cursor.execute("SELECT ID, Email, Username, Password FROM USER")
        users = cursor.fetchall()

        cursor.close()
        connection.close()

        # ✅ Change 2: Add a Password column to the HTML table
        html = """
        <html>
        <head><title>All Users</title></head>
        <body>
            <h2>Registered Users</h2>
            <table border="1">
                <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Username</th>
                    <th>Password</th>  <!-- Added header -->
                </tr>
                {% for user in users %}
                <tr>
                    <td>{{ user[0] }}</td>
                    <td>{{ user[1] }}</td>
                    <td>{{ user[2] }}</td>
                    <td>{{ user[3] }}</td>  <!-- Display password -->
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """

        return render_template_string(html, users=users)

    except Exception as e:
        return f"<h3>Error retrieving users: {str(e)}</h3>"
