from flask import Blueprint, request, jsonify
from backend.config import get_connection

profile_bp = Blueprint('profile', __name__)

def serialize_booking_dict(row):
    return {
        "BookingID":     row["BookingID"],
        "UserID":        row["UserID"],
        "Date":          str(row["Date"]),
        "Hour":          str(row["Hour"]),
        "Duration":      row["Duration"],           # INT, already serializable
        "RoomNumber":    row["RoomNumber"],
        "Building":      row["Building"],
        "BookingType":   row["BookingType"],
        "CourseID":      str(row.get("CourseID")),       # might be None
        "IsApproved":    bool(row["IsApproved"]),   # MySQL returns 0/1
    }


@profile_bp.route("/api/profile/past-res", methods=["GET"])
def get_student_reservations():
    try:
        user_id = request.args.get("UserID")
        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400
        
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM TIME_SLOT 
            WHERE (BookingType = 'student' OR BookingType = 'club')
            AND IsApproved = TRUE
            AND UserID = %s
            AND (
                Date < CURDATE()
                OR
                (
                    Date = CURDATE() 
                    AND ADDTIME(Hour, SEC_TO_TIME(Duration * 3600)) <= CURTIME()
                )
            )
        """, (user_id,))


        raw = cur.fetchall()
        cur.close()
        conn.close()

        reservations = [serialize_booking_dict(r) for r in raw]
        return jsonify({"success": True, "reservations": reservations}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    

@profile_bp.route("/api/profile/reset-pass", methods=["GET", "POST"])
def change_user_password():
    try:
        email = request.args.get("email")
        old_password = request.args.get("old_password")
        new_password = request.args.get("new_password")

        if not email or not old_password or not new_password:
            return jsonify({"success": False, "message": "Missing email, old password, or new password."}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Check if user exists and old password matches
        cur.execute("SELECT * FROM USER WHERE Email = %s AND Password = %s", (email, old_password))
        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Incorrect email or old password."}), 401

        # Update password
        cur.execute("UPDATE USER SET Password = %s WHERE Email = %s", (new_password, email))
        conn.commit()

        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Password successfully updated."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

