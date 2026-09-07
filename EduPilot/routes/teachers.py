from flask import Blueprint, render_template, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
from routes.security import admin_required
from db import get_db_connection

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/admin/teachers")
@admin_required
def teachers_page():
    return render_template("AdminDashboard(Teachers).html")




# =========================================================
# =========================================================
# TEACHERS
# =========================================================
# =========================================================


# =========================================================
# GET TEACHERS
# =========================================================

@teachers_bp.route("/api/teachers", methods=["GET"])
@admin_required
def get_teachers():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT
                t.teacher_id,
                t.name,
                t.email,

                GROUP_CONCAT(
                    DISTINCT s.subject_name
                    ORDER BY s.subject_name
                    SEPARATOR ', '
                ) AS subjects,

                GROUP_CONCAT(
                    DISTINCT tc.class_name
                    ORDER BY tc.class_name
                    SEPARATOR ', '
                ) AS classes

            FROM teachers t

            LEFT JOIN teacher_subjects ts
                ON t.teacher_id =
                   ts.teacher_id

            LEFT JOIN subjects s
                ON ts.subject_id =
                   s.subject_id

            LEFT JOIN teacher_classes tc
                ON t.teacher_id =
                   tc.teacher_id

            GROUP BY
                t.teacher_id,
                t.name,
                t.email

            ORDER BY
                t.teacher_id DESC
        """)


        teachers = cursor.fetchall()


        return jsonify({
            "success": True,
            "teachers": teachers
        }), 200


    except mysql.connector.Error as error:

        print(
            "GET TEACHERS ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Could not load teachers."
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
# ADD TEACHER
# =========================================================

@teachers_bp.route("/api/teachers", methods=["POST"])
@admin_required
def add_teacher():

    connection = None
    cursor = None

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "message":
                    "No teacher data received."
            }), 400


        # -------------------------------------------------
        # GET DATA
        # -------------------------------------------------

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        subjects = data.get(
            "subjects",
            []
        )


        classes = data.get(
            "classes",
            []
        )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:

            return jsonify({
                "success": False,
                "message":
                    "Teacher name is required."
            }), 400


        if not email:

            return jsonify({
                "success": False,
                "message":
                    "Email is required."
            }), 400


        if len(password) < 8:

            return jsonify({
                "success": False,
                "message":
                    "Password must be at least 8 characters."
            }), 400


        if not isinstance(
            subjects,
            list
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid subjects."
            }), 400


        if not isinstance(
            classes,
            list
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid classes."
            }), 400


        if len(subjects) == 0:

            return jsonify({
                "success": False,
                "message":
                    "Select at least one subject."
            }), 400


        if len(classes) == 0:

            return jsonify({
                "success": False,
                "message":
                    "Select at least one class."
            }), 400


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        password_hash = (
            generate_password_hash(
                password
            )
        )


        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # CHECK DUPLICATE EMAIL
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT teacher_id
            FROM teachers
            WHERE email = %s
            """,
            (
                email,
            )
        )


        existing_teacher = cursor.fetchone()


        if existing_teacher:

            return jsonify({
                "success": False,
                "message":
                    "A teacher with this email already exists."
            }), 409


        # -------------------------------------------------
        # KEEP TEXT COLUMNS FOR CURRENT UI
        # -------------------------------------------------

        subjects_text = ", ".join(
            str(subject).strip()
            for subject in subjects
            if str(subject).strip()
        )


        classes_text = ", ".join(
            str(class_name).strip()
            for class_name in classes
            if str(class_name).strip()
        )


        # -------------------------------------------------
        # INSERT TEACHER
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO teachers (
                name,
                email,
                password_hash,
                subjects,
                classes
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                password_hash,
                subjects_text,
                classes_text
            )
        )


        teacher_id = cursor.lastrowid


        # -------------------------------------------------
        # LINK SUBJECTS
        # -------------------------------------------------

        for subject_name in subjects:

            subject_name = str(
                subject_name
            ).strip()


            if not subject_name:
                continue


            cursor.execute(
                """
                SELECT subject_id
                FROM subjects
                WHERE subject_name = %s
                """,
                (
                    subject_name,
                )
            )


            subject_record = cursor.fetchone()


            if not subject_record:

                connection.rollback()


                return jsonify({
                    "success": False,
                    "message":
                        f"Subject '{subject_name}' does not exist."
                }), 400


            cursor.execute(
                """
                INSERT INTO teacher_subjects (
                    teacher_id,
                    subject_id
                )

                VALUES (
                    %s,
                    %s
                )
                """,
                (
                    teacher_id,
                    subject_record[
                        "subject_id"
                    ]
                )
            )


        # -------------------------------------------------
        # LINK CLASSES
        # -------------------------------------------------

        for class_name in classes:

            class_name = str(
                class_name
            ).strip()


            if not class_name:
                continue


            cursor.execute(
                """
                INSERT INTO teacher_classes (
                    teacher_id,
                    class_name
                )

                VALUES (
                    %s,
                    %s
                )
                """,
                (
                    teacher_id,
                    class_name
                )
            )


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Teacher added successfully.",
            "teacher_id":
                teacher_id
        }), 201


    except mysql.connector.IntegrityError as error:

        if connection:
            connection.rollback()


        print(
            "TEACHER INTEGRITY ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Duplicate teacher or relationship."
        }), 409


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()


        print(
            "ADD TEACHER ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Database error while adding teacher."
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
# UPDATE TEACHER
# =========================================================

@teachers_bp.route("/api/teachers/<int:teacher_id>", methods=["PUT"])
@admin_required
def update_teacher(teacher_id):

    connection = None
    cursor = None

    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "success": False,
                "message":
                    "No teacher data received."
            }), 400


        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        subjects = data.get(
            "subjects",
            []
        )


        classes = data.get(
            "classes",
            []
        )


        if not name or not email:

            return jsonify({
                "success": False,
                "message":
                    "Name and email are required."
            }), 400


        if not isinstance(
            subjects,
            list
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid subjects."
            }), 400


        if not isinstance(
            classes,
            list
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid classes."
            }), 400


        if len(subjects) == 0:

            return jsonify({
                "success": False,
                "message":
                    "Select at least one subject."
            }), 400


        if len(classes) == 0:

            return jsonify({
                "success": False,
                "message":
                    "Select at least one class."
            }), 400


        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # CHECK TEACHER EXISTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT teacher_id
            FROM teachers
            WHERE teacher_id = %s
            """,
            (
                teacher_id,
            )
        )


        existing_teacher = cursor.fetchone()


        if not existing_teacher:

            return jsonify({
                "success": False,
                "message":
                    "Teacher not found."
            }), 404


        # -------------------------------------------------
        # TEXT VALUES
        # -------------------------------------------------

        subjects_text = ", ".join(
            str(subject).strip()
            for subject in subjects
            if str(subject).strip()
        )


        classes_text = ", ".join(
            str(class_name).strip()
            for class_name in classes
            if str(class_name).strip()
        )


        # -------------------------------------------------
        # UPDATE TEACHER
        # -------------------------------------------------

        if password:

            if len(password) < 8:

                return jsonify({
                    "success": False,
                    "message":
                        "Password must be at least 8 characters."
                }), 400


            password_hash = (
                generate_password_hash(
                    password
                )
            )


            cursor.execute(
                """
                UPDATE teachers

                SET
                    name = %s,
                    email = %s,
                    password_hash = %s,
                    subjects = %s,
                    classes = %s

                WHERE teacher_id = %s
                """,
                (
                    name,
                    email,
                    password_hash,
                    subjects_text,
                    classes_text,
                    teacher_id
                )
            )


        else:

            cursor.execute(
                """
                UPDATE teachers

                SET
                    name = %s,
                    email = %s,
                    subjects = %s,
                    classes = %s

                WHERE teacher_id = %s
                """,
                (
                    name,
                    email,
                    subjects_text,
                    classes_text,
                    teacher_id
                )
            )


        # -------------------------------------------------
        # REMOVE OLD SUBJECT LINKS
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM teacher_subjects
            WHERE teacher_id = %s
            """,
            (
                teacher_id,
            )
        )


        # -------------------------------------------------
        # INSERT NEW SUBJECT LINKS
        # -------------------------------------------------

        for subject_name in subjects:

            subject_name = str(
                subject_name
            ).strip()


            cursor.execute(
                """
                SELECT subject_id
                FROM subjects
                WHERE subject_name = %s
                """,
                (
                    subject_name,
                )
            )


            subject_record = cursor.fetchone()


            if not subject_record:

                connection.rollback()


                return jsonify({
                    "success": False,
                    "message":
                        f"Subject '{subject_name}' does not exist."
                }), 400


            cursor.execute(
                """
                INSERT INTO teacher_subjects (
                    teacher_id,
                    subject_id
                )

                VALUES (
                    %s,
                    %s
                )
                """,
                (
                    teacher_id,
                    subject_record[
                        "subject_id"
                    ]
                )
            )


        # -------------------------------------------------
        # REMOVE OLD CLASS LINKS
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM teacher_classes
            WHERE teacher_id = %s
            """,
            (
                teacher_id,
            )
        )


        # -------------------------------------------------
        # INSERT NEW CLASS LINKS
        # -------------------------------------------------

        for class_name in classes:

            class_name = str(
                class_name
            ).strip()


            cursor.execute(
                """
                INSERT INTO teacher_classes (
                    teacher_id,
                    class_name
                )

                VALUES (
                    %s,
                    %s
                )
                """,
                (
                    teacher_id,
                    class_name
                )
            )


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Teacher updated successfully."
        }), 200


    except mysql.connector.IntegrityError as error:

        if connection:
            connection.rollback()


        print(
            "UPDATE TEACHER INTEGRITY ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Email or relationship already exists."
        }), 409


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()


        print(
            "UPDATE TEACHER ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Could not update teacher."
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
# DELETE TEACHER
# =========================================================

@teachers_bp.route("/api/teachers/<int:teacher_id>", methods=["DELETE"])
@admin_required
def delete_teacher(teacher_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # Relationships first

        cursor.execute(
            """
            DELETE FROM teacher_subjects
            WHERE teacher_id = %s
            """,
            (
                teacher_id,
            )
        )


        cursor.execute(
            """
            DELETE FROM teacher_classes
            WHERE teacher_id = %s
            """,
            (
                teacher_id,
            )
        )


        cursor.execute(
            """
            DELETE FROM teachers
            WHERE teacher_id = %s
            """,
            (
                teacher_id,
            )
        )


        if cursor.rowcount == 0:

            connection.rollback()


            return jsonify({
                "success": False,
                "message":
                    "Teacher not found."
            }), 404


        connection.commit()


        return jsonify({
            "success": True,
            "message":
                "Teacher deleted successfully."
        }), 200


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()


        print(
            "DELETE TEACHER ERROR:",
            error
        )


        return jsonify({
            "success": False,
            "message":
                "Could not delete teacher."
        }), 500


    finally:

        if cursor:
            cursor.close()


        if (
            connection
            and connection.is_connected()
        ):
            connection.close()

