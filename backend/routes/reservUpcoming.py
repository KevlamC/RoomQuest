from flask import Blueprint, jsonify
from backend.config import get_connection
import logging

reservUpcoming = Blueprint("reservUpcoming", __name__)

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@reservUpcoming.route("/api/user/<int:user_id>/reservations", methods=["GET"])
def get_user_upcoming_reservations(user_id):
    try:
        logger.info(f"Fetching upcoming reservations for user_id: {user_id}")
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # SQL Query to fetch upcoming reservations
                cursor.execute("""
                    SELECT 
                        RoomNumber,
                        Building,
                        Date,
                        Hour AS time,
                        Duration
                    FROM TIME_SLOT
                    WHERE UserID = %s
                      AND Date >= CURDATE()
                      AND IsApproved = TRUE
                    ORDER BY Date ASC, Hour ASC
                    LIMIT 3
                """, (user_id,))
                
                reservations = cursor.fetchall()

                if not reservations:
                    logger.info(f"No upcoming reservations found for user_id: {user_id}")
                    return jsonify({
                        "success": True,
                        "reservations": [],
                        "message": "No upcoming reservations found."
                    }), 200
        
        logger.info(f"Reservations fetched successfully for user_id: {user_id}")
        return jsonify({
            "success": True,
            "reservations": reservations
        }), 200

    except Exception as e:
        logger.error(f"Error fetching reservations for user_id {user_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An error occurred while fetching reservations. Please try again later."
        }), 500
