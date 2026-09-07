from flask import Blueprint, render_template, request, jsonify
import mysql.connector
from db import get_db_connection
from routes.security import admin_required

students_bp = Blueprint("students", __name__)


# =========================================================
# STUDENTS PAGE
# =========================================================

@students_bp.route("/admin/students")
@admin_required
def students_page():
    return render_template("AdminDashboard(Students).html")


# =========================================================
# GET STUDENTS
# =========================================================

@students_bp.route("/api/students", methods=["GET"])
@admin_required
def get_students():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                s.student_id,
                s.student_name,
                s.student_number,
                s.grade,
                s.class_name,
                s.emergency_contact_name,
                s.emergency_contact_number,
                s.allergy_details,
                GROUP_CONCAT(
                    sub.subject_name
                    ORDER BY sub.subject_name
                    SEPARATOR ', '
                ) AS subjects
            FROM students s
            LEFT JOIN student_subjects ss
                ON s.student_id = ss.student_id
            LEFT JOIN subjects sub
                ON ss.subject_id = sub.subject_id
            GROUP BY
                s.student_id,
                s.student_name,
                s.student_number,
                s.grade,
                s.class_name,
                s.emergency_contact_name,
                s.emergency_contact_number,
                s.allergy_details
            ORDER BY s.student_id DESC
        """)

        students = cursor.fetchall()

        return jsonify({
            "success": True,
            "students": students
        }), 200

    except mysql.connector.Error as error:
        print("GET STUDENTS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not load students."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# ADD STUDENT
# =========================================================

@students_bp.route("/api/students", methods=["POST"])
@admin_required
def add_student():

    connection = None
    cursor = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No student data received."
            }), 400

        student_name = str(data.get("student_name", "")).strip()
        student_number = str(data.get("student_number", "")).strip()
        grade = str(data.get("grade", "")).strip()
        class_name = str(data.get("class_name", "")).strip()
        emergency_contact_name = str(data.get("emergency_contact_name", "")).strip()
        emergency_contact_number = str(data.get("emergency_contact_number", "")).strip()
        allergy_details = str(data.get("allergy_details", "")).strip()
        subjects = data.get("subjects", [])

        # =====================================================
        # VALIDATION
        # =====================================================

        if not student_name:
            return jsonify({
                "success": False,
                "message": "Student name is required."
            }), 400

        if not student_number:
            return jsonify({
                "success": False,
                "message": "Student number is required."
            }), 400

        if not grade:
            return jsonify({
                "success": False,
                "message": "Grade is required."
            }), 400

        if not class_name:
            return jsonify({
                "success": False,
                "message": "Class is required."
            }), 400

        if not isinstance(subjects, list):
            return jsonify({
                "success": False,
                "message": "Invalid subjects."
            }), 400

        # =====================================================
        # DATABASE
        # =====================================================

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check duplicate student number

        cursor.execute("""
            SELECT student_id
            FROM students
            WHERE student_number = %s
        """, (student_number,))

        existing_student = cursor.fetchone()

        if existing_student:
            return jsonify({
                "success": False,
                "message": "Student number already exists."
            }), 409

        # Insert student

        cursor.execute("""
            INSERT INTO students (
                student_name,
                student_number,
                grade,
                class_name,
                emergency_contact_name,
                emergency_contact_number,
                allergy_details
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            student_name,
            student_number,
            grade,
            class_name,
            emergency_contact_name or None,
            emergency_contact_number or None,
            allergy_details or None
        ))

        student_id = cursor.lastrowid

        # =====================================================
        # LINK SUBJECTS
        # =====================================================

        for subject_name in subjects:

            subject_name = str(subject_name).strip()

            if not subject_name:
                continue

            cursor.execute("""
                SELECT subject_id
                FROM subjects
                WHERE subject_name = %s
            """, (subject_name,))

            subject_record = cursor.fetchone()

            if not subject_record:
                connection.rollback()

                return jsonify({
                    "success": False,
                    "message": f"Subject '{subject_name}' does not exist."
                }), 400

            cursor.execute("""
                INSERT INTO student_subjects (
                    student_id,
                    subject_id
                )
                VALUES (%s, %s)
            """, (
                student_id,
                subject_record["subject_id"]
            ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Student added successfully.",
            "student_id": student_id
        }), 201

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("ADD STUDENT ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Database error while adding student."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# DELETE STUDENT
# =========================================================

@students_bp.route("/api/students/<int:student_id>", methods=["DELETE"])
@admin_required
def delete_student(student_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Delete subject relationships first

        cursor.execute("""
            DELETE FROM student_subjects
            WHERE student_id = %s
        """, (student_id,))

        # Delete student

        cursor.execute("""
            DELETE FROM students
            WHERE student_id = %s
        """, (student_id,))

        if cursor.rowcount == 0:
            connection.rollback()

            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Student deleted successfully."
        }), 200

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("DELETE STUDENT ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not delete student."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()