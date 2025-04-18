from flask import Blueprint, request, jsonify, render_template_string
from backend.config import get_connection

user_bp = Blueprint('user', __name__)

# Route to handle user signup (inserts into USER table)
@user_bp.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        user_id = data.get('id')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO USER (ID, Email, Username, Password)
            VALUES (%s, %s, %s, %s)
        """, (user_id, email, username, password))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "User inserted successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Route to display all users in the USER table
@user_bp.route('/view-users', methods=['GET'])
def view_users():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT ID, Email, Username FROM USER")
        users = cursor.fetchall()

        cursor.close()
        connection.close()

        # HTML template for displaying users
        html = """
        <html>
        <head><title>All Users</title></head>
        <body>
            <h2>Registered Users</h2>
            <table border="1">
                <tr><th>ID</th><th>Email</th><th>Username</th></tr>
                {% for user in users %}
                <tr>
                    <td>{{ user[0] }}</td>
                    <td>{{ user[1] }}</td>
                    <td>{{ user[2] }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """

        return render_template_string(html, users=users)

    except Exception as e:
        return f"<h3>Error retrieving users: {str(e)}</h3>"
