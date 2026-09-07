from flask import Blueprint, render_template, request, jsonify
import mysql.connector
from routes.security import admin_required
from db import get_db_connection

events_bp = Blueprint("events", __name__)


@events_bp.route("/admin/events")
@admin_required
def events_page():
    return render_template("AdminDashboard(Events).html")




@events_bp.route("/api/events", methods=["GET"])
@admin_required
def get_events():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT
                event_id,
                event_name,
                event_type,
                event_date,
                event_time,
                venue,
                organizer,
                created_at

            FROM events

            ORDER BY
                event_date ASC,
                event_time ASC
        """)


        events = cursor.fetchall()


        # Convert MySQL values to strings

        for event in events:

            if event["event_date"]:

                event["event_date"] = (
                    event[
                        "event_date"
                    ].strftime(
                        "%Y-%m-%d"
                    )
                )


            if event["event_time"]:

                total_seconds = int(
                    event[
                        "event_time"
                    ].total_seconds()
                )


                hours = (
                    total_seconds // 3600
                )


                minutes = (
                    total_seconds % 3600
                ) // 60


                event["event_time"] = (
                    f"{hours:02d}:{minutes:02d}"
                )


            if event["created_at"]:

                event["created_at"] = (
                    event[
                        "created_at"
                    ].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )


        return jsonify({
            "success": True,
            "events": events
        }), 200


    except mysql.connector.Error as error:

        print(
            "GET EVENTS ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Could not retrieve events."
        }), 500


    finally:

        if cursor:
            cursor.close()


        if (
            connection
            and connection.is_connected()
        ):
            connection.close()


# =========================================================
# ADD EVENT
# =========================================================

@events_bp.route("/api/events", methods=["POST"])
@admin_required
def add_event():

    connection = None
    cursor = None

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "message":
                    "No event data was provided."
            }), 400


        event_name = str(
            data.get(
                "event_name",
                ""
            )
        ).strip()


        event_type = str(
            data.get(
                "event_type",
                ""
            )
        ).strip()


        event_date = str(
            data.get(
                "event_date",
                ""
            )
        ).strip()


        event_time = str(
            data.get(
                "event_time",
                ""
            )
        ).strip()


        venue = str(
            data.get(
                "venue",
                ""
            )
        ).strip()


        organizer = str(
            data.get(
                "organizer",
                ""
            )
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not event_name:

            return jsonify({
                "success": False,
                "message":
                    "Event name is required."
            }), 400


        allowed_types = [
            "Academic",
            "Sports",
            "Meeting",
            "Social",
            "Other"
        ]


        if event_type not in allowed_types:

            return jsonify({
                "success": False,
                "message":
                    "Invalid event type."
            }), 400


        if not event_date:

            return jsonify({
                "success": False,
                "message":
                    "Event date is required."
            }), 400


        if not event_time:

            return jsonify({
                "success": False,
                "message":
                    "Event time is required."
            }), 400


        if not venue:

            return jsonify({
                "success": False,
                "message":
                    "Venue is required."
            }), 400


        if not organizer:

            return jsonify({
                "success": False,
                "message":
                    "Organizer is required."
            }), 400


        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO events (
                event_name,
                event_type,
                event_date,
                event_time,
                venue,
                organizer
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                event_name,
                event_type,
                event_date,
                event_time,
                venue,
                organizer
            )
        )


        event_id = cursor.lastrowid


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Event added successfully.",
            "event_id":
                event_id
        }), 201


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()


        print(
            "ADD EVENT ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Database error while adding event."
        }), 500


    finally:

        if cursor:
            cursor.close()


        if (
            connection
            and connection.is_connected()
        ):
            connection.close()


# =========================================================
# DELETE EVENT
# =========================================================

@events_bp.route("/api/events/<int:event_id>", methods=["DELETE"])
@admin_required
def delete_event(event_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            DELETE FROM events
            WHERE event_id = %s
            """,
            (
                event_id,
            )
        )


        if cursor.rowcount == 0:

            connection.rollback()


            return jsonify({
                "success": False,
                "message":
                    "Event not found."
            }), 404


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Event deleted successfully."
        }), 200


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()


        print(
            "DELETE EVENT ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Database error while deleting event."
        }), 500


    finally:

        if cursor:
            cursor.close()


        if (
            connection
            and connection.is_connected()
        ):
            connection.close()
