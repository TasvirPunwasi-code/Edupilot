from flask import Blueprint, render_template, request, jsonify, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db_connection
from otp import generate_otp
from email_service import send_otp
from routes.security import admin_required, teacher_required
import mysql.connector

auth_bp = Blueprint("auth", __name__)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@auth_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("AdminDashboard.html", 
        user_name = session.get("name"),
        user_email = session.get("email"),
        user_role = session.get("role")
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@auth_bp.route("/teacher/dashboard")
@teacher_required
def teacher_dashboard():
    return render_template("TeachersDashboard.html",
        user_name = session.get("name"),
        user_email = session.get("email"),
        user_role = session.get("role")
    )
        
# =========================================================
# LOGIN PAGE
# =========================================================

@auth_bp.route("/")
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/about")
def about_page():
    return render_template("about.html")


@auth_bp.route("/support")
def support_page():
    return render_template("support.html")

# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No login information received."
        }), 400

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =====================================================
        # CHECK ADMIN
        # =====================================================

        cursor.execute("""
            SELECT
                admin_id AS user_id,
                name,
                email,
                password_hash
            FROM admins
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()
        role = "admin"

        # =====================================================
        # IF NOT ADMIN, CHECK TEACHER
        # =====================================================

        if not user:

            cursor.execute("""
                SELECT
                    teacher_id AS user_id,
                    name,
                    email,
                    password_hash
                FROM teachers
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()
            role = "teacher"

        # =====================================================
        # ACCOUNT DOES NOT EXIST
        # =====================================================

        if not user:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password."
            }), 401

        # =====================================================
        # CHECK HASHED PASSWORD
        # =====================================================

        if not check_password_hash(user["password_hash"], password):
            return jsonify({
                "status": "error",
                "message": "Invalid email or password."
            }), 401

        # =====================================================
        # GENERATE OTP
        # =====================================================

        otp = generate_otp()

        # Clear any previous login session
        session.clear()

        # This is only a pending login.
        # User is NOT fully authenticated yet.
        session["pending_user_id"] = user["user_id"]
        session["pending_email"] = user["email"]
        session["pending_name"] = user["name"]
        session["pending_role"] = role
        session["otp"] = otp

        # =====================================================
        # SEND OTP
        # =====================================================

        send_otp(user["email"], otp)

        return jsonify({
            "status": "otp",
            "message": "Verification code sent."
        }), 200

    except mysql.connector.Error as error:

        print("LOGIN DATABASE ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Database error."
        }), 500

    except Exception as error:

        print("LOGIN ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Could not complete login."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# OTP PAGE + VERIFY OTP
# =========================================================

@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():

    # =====================================================
    # SHOW OTP PAGE
    # =====================================================

    if request.method == "GET":

        if "pending_user_id" not in session:
            return render_template("/login")

        return render_template("verify.html")

    # =====================================================
    # VERIFY OTP
    # =====================================================

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No OTP received."
        }), 400

    entered_otp = str(data.get("otp", "")).strip()
    saved_otp = str(session.get("otp", "")).strip()

    if not saved_otp:
        return jsonify({
            "status": "error",
            "message": "Your verification session has expired. Please login again."
        }), 401

    if entered_otp != saved_otp:
        return jsonify({
            "status": "error",
            "message": "Incorrect OTP."
        }), 401

    # =====================================================
    # OTP CORRECT - COMPLETE LOGIN
    # =====================================================

    session["user_id"] = session.get("pending_user_id")
    session["email"] = session.get("pending_email")
    session["name"] = session.get("pending_name")
    session["role"] = session.get("pending_role")
    session["authenticated"] = True

    # Remove temporary login information
    session.pop("pending_user_id", None)
    session.pop("pending_email", None)
    session.pop("pending_name", None)
    session.pop("pending_role", None)
    session.pop("otp", None)

    role = session["role"]

    if role == "admin":
        redirect_url = "/admin/dashboard"

    elif role == "teacher":
        redirect_url = "/teacher/dashboard"

    else:
        session.clear()

        return jsonify({
            "status": "error",
            "message": "Invalid account role."
        }), 403

    return jsonify({
        "status": "success",
        "redirect": redirect_url
    }), 200


# =========================================================
# RESEND OTP
# =========================================================

@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():

    email = session.get("pending_email")

    if not email:
        return jsonify({
            "status": "error",
            "message": "Login session expired. Please login again."
        }), 401

    otp = generate_otp()

    session["otp"] = otp

    try:
        send_otp(email, otp)

        return jsonify({
            "status": "success",
            "message": "A new verification code was sent."
        }), 200

    except Exception as error:

        print("RESEND OTP ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Could not send another verification code."
        }), 500

@auth_bp.route("/change-password/resend-otp", methods=["POST"])
def resend_password_otp():

    email = session.get("reset_email")

    if not email:
        return jsonify({
            "status": "error",
            "message": "Password change session expired. Please start again."
        }), 401

    try:
        otp = generate_otp()

        session["reset_otp"] = otp
        session["reset_verified"] = False

        send_otp(email, otp)

        return jsonify({
            "status": "success",
            "message": "A new verification code was sent."
        }), 200

    except Exception as error:
        print("PASSWORD OTP RESEND ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Could not resend the verification code."
        }), 500
        
        
# =========================================================
# REQUEST PASSWORD CHANGE
# =========================================================

@auth_bp.route("/change-password/request", methods=["POST"])
def request_password_change():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No email was provided."
        }), 400

    email = str(data.get("email", "")).strip().lower()

    if not email:
        return jsonify({
            "status": "error",
            "message": "Email is required."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check admin
        cursor.execute("""
            SELECT
                admin_id AS user_id,
                email
            FROM admins
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()
        role = "admin"

        # If not admin, check teacher
        if not user:
            cursor.execute("""
                SELECT
                    teacher_id AS user_id,
                    email
                FROM teachers
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()
            role = "teacher"

        if not user:
            return jsonify({
                "status": "error",
                "message": "No EduPilot account was found with that email."
            }), 404

        otp = generate_otp()

        session["reset_user_id"] = user["user_id"]
        session["reset_email"] = user["email"]
        session["reset_role"] = role
        session["reset_otp"] = otp
        session["reset_verified"] = False

        send_otp(user["email"], otp)

        return jsonify({
            "status": "otp",
            "message": "A verification code was sent to your email."
        }), 200

    except mysql.connector.Error as error:
        print("PASSWORD RESET DATABASE ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Database error."
        }), 500

    except Exception as error:
        print("PASSWORD RESET ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Could not start the password change."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# VERIFY PASSWORD RESET PAGE
# =========================================================

@auth_bp.route("/verify-password", methods=["GET"])
def verify_password_page():

    if "reset_user_id" not in session:
        return render_template("login.html")

    return render_template("verify_password.html")


# =========================================================
# VERIFY PASSWORD RESET OTP
# =========================================================

@auth_bp.route("/verify-password", methods=["POST"])
def verify_password_otp():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No OTP was provided."
        }), 400

    entered_otp = str(data.get("otp", "")).strip()
    saved_otp = str(session.get("reset_otp", "")).strip()

    if not saved_otp:
        return jsonify({
            "status": "error",
            "message": "Password reset session expired."
        }), 401

    if entered_otp != saved_otp:
        return jsonify({
            "status": "error",
            "message": "Incorrect verification code."
        }), 401

    session["reset_verified"] = True
    session.pop("reset_otp", None)

    return jsonify({
        "status": "success",
        "redirect": "/new-password"
    }), 200


# =========================================================
# NEW PASSWORD PAGE
# =========================================================

@auth_bp.route("/new-password", methods=["GET"])
def new_password_page():

    if not session.get("reset_verified"):
        return render_template("login.html")

    return render_template("new_password.html")


# =========================================================
# UPDATE PASSWORD
# =========================================================

@auth_bp.route("/new-password", methods=["POST"])
def update_password():

    if not session.get("reset_verified"):
        return jsonify({
            "status": "error",
            "message": "Password reset has not been verified."
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No password data received."
        }), 400

    new_password = str(data.get("password", ""))
    confirm_password = str(data.get("confirm_password", ""))

    if len(new_password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must be at least 8 characters."
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "status": "error",
            "message": "Passwords do not match."
        }), 400

    user_id = session.get("reset_user_id")
    role = session.get("reset_role")

    if not user_id or not role:
        return jsonify({
            "status": "error",
            "message": "Password reset session expired."
        }), 401

    password_hash = generate_password_hash(new_password)

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if role == "admin":
            cursor.execute("""
                UPDATE admins
                SET password_hash = %s
                WHERE admin_id = %s
            """, (password_hash, user_id))

        elif role == "teacher":
            cursor.execute("""
                UPDATE teachers
                SET password_hash = %s
                WHERE teacher_id = %s
            """, (password_hash, user_id))

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid account role."
            }), 400

        if cursor.rowcount == 0:
            connection.rollback()

            return jsonify({
                "status": "error",
                "message": "Account could not be found."
            }), 404

        connection.commit()

        session.pop("reset_user_id", None)
        session.pop("reset_email", None)
        session.pop("reset_role", None)
        session.pop("reset_verified", None)
        session.pop("reset_otp", None)

        return jsonify({
            "status": "success",
            "message": "Password changed successfully.",
            "redirect": "/login"
        }), 200

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        print("PASSWORD UPDATE ERROR:", error)

        return jsonify({
            "status": "error",
            "message": "Could not update password."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/login")