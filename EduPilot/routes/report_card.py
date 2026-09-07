from flask import Blueprint, render_template, jsonify, request, session, make_response
from weasyprint import HTML

from db import get_db_connection
from routes.security import admin_required


report_card_bp = Blueprint("report_card", __name__)


@report_card_bp.route("/admin/report-card")
@admin_required
def report_card_page():
    return render_template(
        "ReportCard.html",
        user_name=session.get("name"),
        user_role=session.get("role")
    )


@report_card_bp.route("/api/admin/report-card/students", methods=["GET"])
@admin_required
def report_card_students():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            student_id,
            student_name,
            student_number,
            grade,
            class_name
        FROM students
        ORDER BY student_name
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(students)


def get_report_data(student_id, term):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            student_id,
            student_name,
            student_number,
            grade,
            class_name
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        connection.close()
        return None

    cursor.execute("""
        SELECT
            s.subject_id,
            s.subject_name,
            ROUND(AVG(CASE WHEN m.assessment_type LIKE 'Test%' THEN m.mark END), 2) AS test_average,
            ROUND(AVG(CASE WHEN m.assessment_type = 'Assignment' THEN m.mark END), 2) AS assignment_average,
            ROUND(AVG(CASE WHEN m.assessment_type = 'Exam' THEN m.mark END), 2) AS exam_average
        FROM student_subjects ss
        JOIN subjects s ON ss.subject_id = s.subject_id
        LEFT JOIN marks m ON m.student_id = ss.student_id
            AND m.subject_id = ss.subject_id
            AND m.term = %s
        WHERE ss.student_id = %s
        GROUP BY s.subject_id, s.subject_name
        ORDER BY s.subject_name
    """, (term, student_id))

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    final_marks = []

    for subject in subjects:
        test = float(subject["test_average"]) if subject["test_average"] is not None else None
        assignment = float(subject["assignment_average"]) if subject["assignment_average"] is not None else None
        exam = float(subject["exam_average"]) if subject["exam_average"] is not None else None

        if test is not None and assignment is not None and exam is not None:
            final_mark = round((test * 0.20) + (assignment * 0.20) + (exam * 0.60), 2)
            final_marks.append(final_mark)
        else:
            final_mark = None

        subject["test_average"] = test
        subject["assignment_average"] = assignment
        subject["exam_average"] = exam
        subject["final_mark"] = final_mark

    overall_average = round(sum(final_marks) / len(final_marks), 2) if final_marks else None

    return {
        "student": student,
        "term": term,
        "subjects": subjects,
        "overall_average": overall_average
    }


@report_card_bp.route("/api/admin/report-card/<int:student_id>", methods=["GET"])
@admin_required
def report_card_data(student_id):
    term = request.args.get("term", type=int)

    if term not in [1, 2, 3, 4]:
        return jsonify({
            "message": "Invalid term."
        }), 400

    report = get_report_data(student_id, term)

    if not report:
        return jsonify({
            "message": "Student not found."
        }), 404

    return jsonify(report)


@report_card_bp.route("/admin/report-card/<int:student_id>/pdf", methods=["POST"])
@admin_required
def generate_report_pdf(student_id):
    term = request.form.get("term", type=int)

    if term not in [1, 2, 3, 4]:
        return "Invalid term.", 400

    report = get_report_data(student_id, term)

    if not report:
        return "Student not found.", 404

    html = render_template(
        "ReportCardPDF.html",
        report=report,
        admin_name=session.get("name")
    )

    pdf = HTML(string=html, base_url=request.url_root).write_pdf()

    response = make_response(pdf)

    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'inline; filename="EduPilot_Report_{student_id}_Term_{term}.pdf"'

    return response