from flask import Blueprint, render_template, request, jsonify, session, send_file
import mysql.connector
from db import get_db_connection
from routes.security import teacher_required
import io
from matplotlib.figure import Figure


marks_bp = Blueprint("marks", __name__)


# =========================================================
# CAPTURE MARKS PAGE
# =========================================================

@marks_bp.route("/teacher/capture-marks")
@teacher_required
def capture_marks_page():

    return render_template(
        "CaptureMarks.html",
        user_name=session.get("name"),
        user_role=session.get("role")
    )


# =========================================================
# GET TEACHER CLASSES + SUBJECTS
# =========================================================

@marks_bp.route("/api/teacher/mark-options", methods=["GET"])
@teacher_required
def get_mark_options():

    teacher_id = session.get("user_id")

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Teacher classes
        cursor.execute("""
            SELECT DISTINCT class_name
            FROM teacher_classes
            WHERE teacher_id = %s
            ORDER BY class_name
        """, (teacher_id,))

        classes = cursor.fetchall()

        # Teacher subjects
        cursor.execute("""
            SELECT DISTINCT
                s.subject_id,
                s.subject_name
            FROM teacher_subjects ts
            JOIN subjects s
                ON ts.subject_id = s.subject_id
            WHERE ts.teacher_id = %s
            ORDER BY s.subject_name
        """, (teacher_id,))

        subjects = cursor.fetchall()

        return jsonify({
            "success": True,
            "classes": classes,
            "subjects": subjects
        }), 200

    except mysql.connector.Error as error:
        print("MARK OPTIONS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not load teacher classes and subjects."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# GET STUDENTS FOR SELECTED CLASS + SUBJECT
# =========================================================

@marks_bp.route("/api/teacher/mark-students", methods=["GET"])
@teacher_required
def get_mark_students():

    teacher_id = session.get("user_id")

    class_name = str(request.args.get("class_name", "")).strip()
    subject_id = request.args.get("subject_id", type=int)

    if not class_name or not subject_id:
        return jsonify({
            "success": False,
            "message": "Class and subject are required."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # CHECK TEACHER IS ASSIGNED TO CLASS
        # =====================================================

        cursor.execute("""
            SELECT teacher_class_id
            FROM teacher_classes
            WHERE teacher_id = %s
            AND class_name = %s
        """, (teacher_id, class_name))

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "You are not assigned to this class."
            }), 403

        # =====================================================
        # CHECK TEACHER IS ASSIGNED TO SUBJECT
        # =====================================================

        cursor.execute("""
            SELECT teacher_subject_id
            FROM teacher_subjects
            WHERE teacher_id = %s
            AND subject_id = %s
        """, (teacher_id, subject_id))

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "You are not assigned to this subject."
            }), 403

        # =====================================================
        # GET STUDENTS
        # =====================================================

        cursor.execute("""
            SELECT DISTINCT
                st.student_id,
                st.student_name,
                st.student_number
            FROM students st
            JOIN student_subjects ss
                ON st.student_id = ss.student_id
            WHERE st.class_name = %s
            AND ss.subject_id = %s
            ORDER BY st.student_name
        """, (class_name, subject_id))

        students = cursor.fetchall()

        return jsonify({
            "success": True,
            "students": students
        }), 200

    except mysql.connector.Error as error:
        print("LOAD MARK STUDENTS ERROR:", error)

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
# SAVE MARKS
# =========================================================

@marks_bp.route("/api/teacher/marks", methods=["POST"])
@teacher_required
def save_marks():

    teacher_id = session.get("user_id")

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No marks data received."
        }), 400

    class_name = str(data.get("class_name", "")).strip()
    subject_id = data.get("subject_id")
    assessment_type = str(data.get("assessment_type", "")).strip()
    term = data.get("term")
    marks = data.get("marks", [])

    if not class_name or not subject_id or not assessment_type or not term:
        return jsonify({
            "success": False,
            "message": "Class, subject, assessment and term are required."
        }), 400

    if not isinstance(marks, list) or len(marks) == 0:
        return jsonify({
            "success": False,
            "message": "No student marks were provided."
        }), 400

    try:
        subject_id = int(subject_id)
        term = int(term)

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid subject or term."
        }), 400

    if term not in [1, 2, 3, 4]:
        return jsonify({
            "success": False,
            "message": "Invalid term."
        }), 400

    allowed_assessments = [
        "Test 1",
        "Assignment",
        "Practical",
        "Exam"
    ]

    if assessment_type not in allowed_assessments:
        return jsonify({
            "success": False,
            "message": "Invalid assessment type."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # VERIFY TEACHER CLASS
        # =====================================================

        cursor.execute("""
            SELECT teacher_class_id
            FROM teacher_classes
            WHERE teacher_id = %s
            AND class_name = %s
        """, (teacher_id, class_name))

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "You are not assigned to this class."
            }), 403

        # =====================================================
        # VERIFY TEACHER SUBJECT
        # =====================================================

        cursor.execute("""
            SELECT teacher_subject_id
            FROM teacher_subjects
            WHERE teacher_id = %s
            AND subject_id = %s
        """, (teacher_id, subject_id))

        if not cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "You are not assigned to this subject."
            }), 403

        # =====================================================
        # SAVE EACH STUDENT MARK
        # =====================================================

        for item in marks:

            student_id = item.get("student_id")
            mark = item.get("mark")

            try:
                student_id = int(student_id)
                mark = float(mark)

            except (TypeError, ValueError):
                connection.rollback()

                return jsonify({
                    "success": False,
                    "message": "Invalid mark information."
                }), 400

            if mark < 0 or mark > 100:
                connection.rollback()

                return jsonify({
                    "success": False,
                    "message": "Marks must be between 0 and 100."
                }), 400

            # =================================================
            # VERIFY STUDENT BELONGS TO CLASS + SUBJECT
            # =================================================

            cursor.execute("""
                SELECT st.student_id
                FROM students st
                JOIN student_subjects ss
                    ON st.student_id = ss.student_id
                WHERE st.student_id = %s
                AND st.class_name = %s
                AND ss.subject_id = %s
            """, (student_id, class_name, subject_id))

            if not cursor.fetchone():
                connection.rollback()

                return jsonify({
                    "success": False,
                    "message": "A student does not belong to the selected class and subject."
                }), 403

            # =================================================
            # INSERT MARK
            # =================================================

            cursor.execute("""
                INSERT INTO marks (
                    student_id,
                    subject_id,
                    teacher_id,
                    class_name,
                    assessment_type,
                    term,
                    mark
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                subject_id,
                teacher_id,
                class_name,
                assessment_type,
                term,
                mark
            ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Marks saved successfully."
        }), 201

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Marks for one or more students have already been captured for this assessment."
        }), 409

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("SAVE MARKS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Database error while saving marks."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            
# =========================================================
# EDIT MARKS PAGE
# =========================================================

@marks_bp.route("/teacher/edit-marks")
@teacher_required
def edit_marks_page():

    return render_template(
        "EditMarks.html",
        user_name=session.get("name"),
        user_role=session.get("role")
    )


# =========================================================
# LOAD EXISTING MARKS
# =========================================================

@marks_bp.route("/api/teacher/edit-marks", methods=["GET"])
@teacher_required
def get_existing_marks():

    teacher_id = session.get("user_id")

    class_name = str(request.args.get("class_name", "")).strip()
    subject_id = request.args.get("subject_id", type=int)
    assessment_type = str(request.args.get("assessment_type", "")).strip()
    term = request.args.get("term", type=int)


    if not class_name or not subject_id or not assessment_type or not term:

        return jsonify({
            "success": False,
            "message": "Class, subject, assessment and term are required."
        }), 400


    connection = None
    cursor = None


    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        # Check teacher's class
        cursor.execute("""
            SELECT teacher_class_id
            FROM teacher_classes
            WHERE teacher_id = %s
            AND class_name = %s
        """, (teacher_id, class_name))


        if not cursor.fetchone():

            return jsonify({
                "success": False,
                "message": "You are not assigned to this class."
            }), 403


        # Check teacher's subject
        cursor.execute("""
            SELECT teacher_subject_id
            FROM teacher_subjects
            WHERE teacher_id = %s
            AND subject_id = %s
        """, (teacher_id, subject_id))


        if not cursor.fetchone():

            return jsonify({
                "success": False,
                "message": "You are not assigned to this subject."
            }), 403


        # Get marks belonging to THIS teacher
        cursor.execute("""
            SELECT
                m.mark_id,
                m.mark,
                st.student_id,
                st.student_name,
                st.student_number
            FROM marks m
            JOIN students st
                ON m.student_id = st.student_id
            WHERE m.teacher_id = %s
            AND m.class_name = %s
            AND m.subject_id = %s
            AND m.assessment_type = %s
            AND m.term = %s
            ORDER BY st.student_name
        """, (
            teacher_id,
            class_name,
            subject_id,
            assessment_type,
            term
        ))


        marks = cursor.fetchall()


        for item in marks:
            item["mark"] = float(item["mark"])


        return jsonify({
            "success": True,
            "marks": marks
        }), 200


    except mysql.connector.Error as error:

        print("LOAD EDIT MARKS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not retrieve marks."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# UPDATE ONE MARK
# =========================================================

@marks_bp.route("/api/teacher/marks/<int:mark_id>", methods=["PUT"])
@teacher_required
def update_mark(mark_id):

    teacher_id = session.get("user_id")

    data = request.get_json()


    if not data or "mark" not in data:

        return jsonify({
            "success": False,
            "message": "A mark is required."
        }), 400


    try:

        mark = float(data["mark"])

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Invalid mark."
        }), 400


    if mark < 0 or mark > 100:

        return jsonify({
            "success": False,
            "message": "Mark must be between 0 and 100."
        }), 400


    connection = None
    cursor = None


    try:

        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("""
            UPDATE marks
            SET mark = %s
            WHERE mark_id = %s
            AND teacher_id = %s
        """, (
            mark,
            mark_id,
            teacher_id
        ))


        if cursor.rowcount == 0:

            connection.rollback()

            return jsonify({
                "success": False,
                "message": "Mark not found or you do not have permission to edit it."
            }), 404


        connection.commit()


        return jsonify({
            "success": True,
            "message": "Mark updated successfully."
        }), 200


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print("UPDATE MARK ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Database error while updating mark."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# UPDATE ALL MARKS
# =========================================================

@marks_bp.route("/api/teacher/marks/bulk-update", methods=["PUT"])
@teacher_required
def bulk_update_marks():

    teacher_id = session.get("user_id")

    data = request.get_json()


    if not data or not isinstance(data.get("marks"), list):

        return jsonify({
            "success": False,
            "message": "No marks were provided."
        }), 400


    marks = data["marks"]


    if len(marks) == 0:

        return jsonify({
            "success": False,
            "message": "No marks were provided."
        }), 400


    connection = None
    cursor = None


    try:

        connection = get_db_connection()
        cursor = connection.cursor()


        for item in marks:

            try:

                mark_id = int(item.get("mark_id"))
                mark = float(item.get("mark"))

            except (TypeError, ValueError):

                connection.rollback()

                return jsonify({
                    "success": False,
                    "message": "Invalid mark information."
                }), 400


            if mark < 0 or mark > 100:

                connection.rollback()

                return jsonify({
                    "success": False,
                    "message": "All marks must be between 0 and 100."
                }), 400


            cursor.execute("""
                UPDATE marks
                SET mark = %s
                WHERE mark_id = %s
                AND teacher_id = %s
            """, (
                mark,
                mark_id,
                teacher_id
            ))


            if cursor.rowcount == 0:

                # It might be unchanged, so verify ownership
                cursor.execute("""
                    SELECT mark_id
                    FROM marks
                    WHERE mark_id = %s
                    AND teacher_id = %s
                """, (
                    mark_id,
                    teacher_id
                ))


                if not cursor.fetchone():

                    connection.rollback()

                    return jsonify({
                        "success": False,
                        "message": "A mark could not be updated because you do not have permission."
                    }), 403


        connection.commit()


        return jsonify({
            "success": True,
            "message": "All marks updated successfully."
        }), 200


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print("BULK UPDATE ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Database error while updating marks."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# DELETE MARK
# =========================================================

@marks_bp.route("/api/teacher/marks/<int:mark_id>", methods=["DELETE"])
@teacher_required
def delete_mark(mark_id):

    teacher_id = session.get("user_id")

    connection = None
    cursor = None


    try:

        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("""
            DELETE FROM marks
            WHERE mark_id = %s
            AND teacher_id = %s
        """, (
            mark_id,
            teacher_id
        ))


        if cursor.rowcount == 0:

            connection.rollback()

            return jsonify({
                "success": False,
                "message": "Mark not found or you do not have permission to delete it."
            }), 404


        connection.commit()


        return jsonify({
            "success": True,
            "message": "Mark deleted successfully."
        }), 200


    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print("DELETE MARK ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Database error while deleting mark."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            
# =========================================================
# VIEW STUDENTS PAGE
# =========================================================

@marks_bp.route("/teacher/students")
@teacher_required
def teacher_students_page():

    return render_template(
        "View_Students.html",
        user_name=session.get("name"),
        user_role=session.get("role")
    )


# =========================================================
# GET STUDENTS AVAILABLE TO LOGGED-IN TEACHER
# =========================================================

@marks_bp.route("/api/teacher/students", methods=["GET"])
@teacher_required
def get_teacher_students():

    teacher_id = session.get("user_id")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        # =================================================
        # GET TEACHER CLASSES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT class_name
            FROM teacher_classes
            WHERE teacher_id = %s
            ORDER BY class_name
        """, (teacher_id,))

        classes = cursor.fetchall()


        # =================================================
        # GET TEACHER'S STUDENTS + CURRENT AVERAGE
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                st.student_id,
                st.student_name,
                st.student_number,
                st.class_name,
                averages.current_average

            FROM students st

            JOIN student_subjects ss
                ON st.student_id = ss.student_id

            JOIN teacher_subjects ts
                ON ss.subject_id = ts.subject_id
                AND ts.teacher_id = %s

            JOIN teacher_classes tc
                ON tc.teacher_id = %s
                AND tc.class_name = st.class_name

            LEFT JOIN (
                SELECT
                    student_id,
                    ROUND(AVG(mark), 2) AS current_average
                FROM marks
                WHERE teacher_id = %s
                GROUP BY student_id
            ) averages
                ON st.student_id = averages.student_id

            ORDER BY st.student_name
        """, (teacher_id, teacher_id, teacher_id))

        students = cursor.fetchall()


        for student in students:

            if student["current_average"] is not None:
                student["current_average"] = float(student["current_average"])


        return jsonify({
            "success": True,
            "classes": classes,
            "students": students
        }), 200


    except mysql.connector.Error as error:

        print("GET TEACHER STUDENTS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not retrieve students."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# GET ONE STUDENT WITH SUBJECT BREAKDOWN
# =========================================================

@marks_bp.route("/api/teacher/students/<int:student_id>", methods=["GET"])
@teacher_required
def get_teacher_student_details(student_id):

    teacher_id = session.get("user_id")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        # =================================================
        # VERIFY TEACHER CAN ACCESS STUDENT
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                st.student_id,
                st.student_name,
                st.student_number,
                st.class_name

            FROM students st

            JOIN student_subjects ss
                ON st.student_id = ss.student_id

            JOIN teacher_subjects ts
                ON ts.subject_id = ss.subject_id
                AND ts.teacher_id = %s

            JOIN teacher_classes tc
                ON tc.teacher_id = %s
                AND tc.class_name = st.class_name

            WHERE st.student_id = %s
        """, (teacher_id, teacher_id, student_id))

        student = cursor.fetchone()


        if not student:

            return jsonify({
                "success": False,
                "message": "Student not found or you do not have permission to view this student."
            }), 404


        # =================================================
        # OVERALL AVERAGE FOR THIS TEACHER'S SUBJECTS
        # =================================================

        cursor.execute("""
            SELECT ROUND(AVG(mark), 2) AS current_average
            FROM marks
            WHERE student_id = %s
            AND teacher_id = %s
        """, (student_id, teacher_id))

        overall = cursor.fetchone()


        if overall["current_average"] is not None:
            student["current_average"] = float(overall["current_average"])
        else:
            student["current_average"] = None


        # =================================================
        # SUBJECT-BY-SUBJECT BREAKDOWN
        # =================================================

        cursor.execute("""
            SELECT
                s.subject_id,
                s.subject_name,

                ROUND(AVG(m.mark), 2) AS subject_average,

                ROUND(
                    AVG(
                        CASE
                            WHEN m.assessment_type LIKE 'Test%'
                            THEN m.mark
                        END
                    ),
                    2
                ) AS test_average,

                ROUND(
                    AVG(
                        CASE
                            WHEN m.assessment_type = 'Assignment'
                            THEN m.mark
                        END
                    ),
                    2
                ) AS assignment_average,

                ROUND(
                    AVG(
                        CASE
                            WHEN m.assessment_type = 'Exam'
                            THEN m.mark
                        END
                    ),
                    2
                ) AS exam_average

            FROM teacher_subjects ts

            JOIN subjects s
                ON ts.subject_id = s.subject_id

            JOIN student_subjects ss
                ON ss.subject_id = s.subject_id
                AND ss.student_id = %s

            LEFT JOIN marks m
                ON m.student_id = %s
                AND m.subject_id = s.subject_id
                AND m.teacher_id = %s

            WHERE ts.teacher_id = %s

            GROUP BY
                s.subject_id,
                s.subject_name

            ORDER BY s.subject_name
        """, (student_id, student_id, teacher_id, teacher_id))

        subjects = cursor.fetchall()


        # =================================================
        # CONVERT DECIMAL VALUES TO FLOAT
        # =================================================

        for subject in subjects:

            if subject["subject_average"] is not None:
                subject["subject_average"] = float(subject["subject_average"])

            if subject["test_average"] is not None:
                subject["test_average"] = float(subject["test_average"])

            if subject["assignment_average"] is not None:
                subject["assignment_average"] = float(subject["assignment_average"])

            if subject["exam_average"] is not None:
                subject["exam_average"] = float(subject["exam_average"])


        student["subjects"] = subjects


        return jsonify({
            "success": True,
            "student": student
        }), 200


    except mysql.connector.Error as error:

        print("STUDENT DETAILS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not retrieve student information."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            
# =========================================================
# TEACHER ANALYTICS PAGE
# =========================================================

@marks_bp.route("/teacher/analytics")
@teacher_required
def teacher_analytics_page():

    return render_template(
        "Analytics.html",
        user_name=session.get("name"),
        user_role=session.get("role")
    )


# =========================================================
# ANALYTICS FILTER OPTIONS
# =========================================================

@marks_bp.route("/api/teacher/analytics/options", methods=["GET"])
@teacher_required
def teacher_analytics_options():

    teacher_id = session.get("user_id")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        cursor.execute("""
            SELECT DISTINCT class_name
            FROM teacher_classes
            WHERE teacher_id = %s
            ORDER BY class_name
        """, (teacher_id,))

        classes = cursor.fetchall()


        cursor.execute("""
            SELECT DISTINCT
                s.subject_id,
                s.subject_name
            FROM teacher_subjects ts
            JOIN subjects s ON ts.subject_id = s.subject_id
            WHERE ts.teacher_id = %s
            ORDER BY s.subject_name
        """, (teacher_id,))

        subjects = cursor.fetchall()


        return jsonify({
            "success": True,
            "classes": classes,
            "subjects": subjects
        }), 200


    except mysql.connector.Error as error:

        print("ANALYTICS OPTIONS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not load analytics options."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# BUILD ANALYTICS FILTER
# =========================================================

def build_analytics_filter(teacher_id):

    class_name = str(request.args.get("class_name", "")).strip()
    subject_id = request.args.get("subject_id", type=int)
    term = request.args.get("term", type=int)

    conditions = ["m.teacher_id = %s"]
    parameters = [teacher_id]


    if class_name:

        conditions.append("m.class_name = %s")
        parameters.append(class_name)


    if subject_id:

        conditions.append("m.subject_id = %s")
        parameters.append(subject_id)


    if term:

        conditions.append("m.term = %s")
        parameters.append(term)


    where_clause = " AND ".join(conditions)

    return where_clause, parameters


# =========================================================
# ANALYTICS SUMMARY
# =========================================================

@marks_bp.route("/api/teacher/analytics", methods=["GET"])
@teacher_required
def teacher_analytics():

    teacher_id = session.get("user_id")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        where_clause, parameters = build_analytics_filter(teacher_id)


        # =================================================
        # TOTAL STUDENTS + AVERAGE
        # =================================================

        cursor.execute(f"""
            SELECT
                COUNT(DISTINCT m.student_id) AS total_students,
                ROUND(AVG(m.mark), 2) AS average_mark
            FROM marks m
            WHERE {where_clause}
        """, tuple(parameters))

        summary = cursor.fetchone()


        # =================================================
        # STUDENT AVERAGES
        # =================================================

        cursor.execute(f"""
            SELECT
                m.student_id,
                st.student_name,
                st.class_name,
                ROUND(AVG(m.mark), 2) AS average_mark
            FROM marks m
            JOIN students st ON m.student_id = st.student_id
            WHERE {where_clause}
            GROUP BY
                m.student_id,
                st.student_name,
                st.class_name
            ORDER BY average_mark ASC
        """, tuple(parameters))

        student_averages = cursor.fetchall()


        highest_average = None
        at_risk = 0
        attention_students = []


        for student in student_averages:

            student["average_mark"] = float(student["average_mark"])


            if highest_average is None or student["average_mark"] > highest_average:
                highest_average = student["average_mark"]


            if student["average_mark"] < 50:

                at_risk += 1

                attention_students.append({
                    "student_id": student["student_id"],
                    "student_name": student["student_name"],
                    "class_name": student["class_name"],
                    "average_mark": student["average_mark"]
                })


        if summary["average_mark"] is not None:
            summary["average_mark"] = float(summary["average_mark"])


        summary["highest_average"] = highest_average
        summary["at_risk"] = at_risk


        return jsonify({
            "success": True,
            "summary": summary,
            "attention_students": attention_students
        }), 200


    except mysql.connector.Error as error:

        print("ANALYTICS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not load analytics."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            
# =========================================================
# MATPLOTLIB GRAPH
# =========================================================

@marks_bp.route("/api/teacher/analytics/graph/<graph_name>", methods=["GET"])
@teacher_required
def teacher_analytics_graph(graph_name):

    teacher_id = session.get("user_id")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        where_clause, parameters = build_analytics_filter(teacher_id)


        # =================================================
        # GRAPH 1 - CLASS PERFORMANCE
        # =================================================

        if graph_name == "class-performance":

            cursor.execute(f"""
                SELECT
                    m.class_name AS label,
                    ROUND(AVG(m.mark), 2) AS value
                FROM marks m
                WHERE {where_clause}
                GROUP BY m.class_name
                ORDER BY m.class_name
            """, tuple(parameters))

            data = cursor.fetchall()

            title = "Class Performance"
            x_label = "Class"
            y_label = "Average Mark (%)"


        # =================================================
        # GRAPH 2 - SUBJECT PERFORMANCE
        # =================================================

        elif graph_name == "subject-performance":

            cursor.execute(f"""
                SELECT
                    s.subject_name AS label,
                    ROUND(AVG(m.mark), 2) AS value
                FROM marks m
                JOIN subjects s ON m.subject_id = s.subject_id
                WHERE {where_clause}
                GROUP BY
                    s.subject_id,
                    s.subject_name
                ORDER BY s.subject_name
            """, tuple(parameters))

            data = cursor.fetchall()

            title = "Subject Performance"
            x_label = "Subject"
            y_label = "Average Mark (%)"


        # =================================================
        # GRAPH 3 - ASSESSMENT PERFORMANCE
        # =================================================

        elif graph_name == "assessment-performance":

            cursor.execute(f"""
                SELECT
                    m.assessment_type AS label,
                    ROUND(AVG(m.mark), 2) AS value
                FROM marks m
                WHERE {where_clause}
                GROUP BY m.assessment_type
                ORDER BY m.assessment_type
            """, tuple(parameters))

            data = cursor.fetchall()

            title = "Assessment Performance"
            x_label = "Assessment"
            y_label = "Average Mark (%)"


        # =================================================
        # GRAPH 4 - STUDENT PERFORMANCE DISTRIBUTION
        # =================================================

        elif graph_name == "performance-distribution":

            cursor.execute(f"""
                SELECT
                    student_average
                FROM (
                    SELECT
                        m.student_id,
                        AVG(m.mark) AS student_average
                    FROM marks m
                    WHERE {where_clause}
                    GROUP BY m.student_id
                ) student_results
            """, tuple(parameters))

            results = cursor.fetchall()


            ranges = {
                "0-39": 0,
                "40-49": 0,
                "50-59": 0,
                "60-74": 0,
                "75-100": 0
            }


            for result in results:

                average = float(result["student_average"])


                if average < 40:
                    ranges["0-39"] += 1

                elif average < 50:
                    ranges["40-49"] += 1

                elif average < 60:
                    ranges["50-59"] += 1

                elif average < 75:
                    ranges["60-74"] += 1

                else:
                    ranges["75-100"] += 1


            data = [
                {"label": label, "value": value}
                for label, value in ranges.items()
            ]

            title = "Student Performance Distribution"
            x_label = "Average Range (%)"
            y_label = "Number of Students"


        else:

            return jsonify({
                "success": False,
                "message": "Invalid graph."
            }), 404


        # =================================================
        # CREATE MATPLOTLIB GRAPH
        # =================================================

        labels = [item["label"] for item in data]
        values = [float(item["value"]) for item in data]


        figure = Figure(figsize=(8, 4.5))
        axis = figure.subplots()


        if len(labels) == 0:

            axis.text(
                0.5,
                0.5,
                "No marks available for this selection",
                horizontalalignment="center",
                verticalalignment="center",
                transform=axis.transAxes
            )

            axis.set_xticks([])
            axis.set_yticks([])

        else:

            axis.bar(labels, values)

            axis.set_xlabel(x_label)
            axis.set_ylabel(y_label)

            axis.tick_params(axis="x", rotation=25)


            if graph_name != "performance-distribution":
                axis.set_ylim(0, 100)


            for index, value in enumerate(values):

                label = f"{value:.1f}%"

                if graph_name == "performance-distribution":
                    label = str(int(value))


                axis.text(
                    index,
                    value,
                    label,
                    ha="center",
                    va="bottom"
                )


        axis.set_title(title)

        figure.tight_layout()


        image = io.BytesIO()

        figure.savefig(
            image,
            format="png",
            dpi=120
        )

        image.seek(0)


        return send_file(
            image,
            mimetype="image/png"
        )


    except mysql.connector.Error as error:

        print("GRAPH ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Could not generate graph."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()