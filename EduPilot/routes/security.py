from functools import wraps
from flask import session, redirect, jsonify, request


def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("authenticated"):

            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Authentication required."
                }), 401

            return redirect("/login")

        return function(*args, **kwargs)

    return wrapper


def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("authenticated"):

            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Authentication required."
                }), 401

            return redirect("/login")

        if session.get("role") != "admin":

            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Admin access required."
                }), 403

            return redirect("/teacher/dashboard")

        return function(*args, **kwargs)

    return wrapper


def teacher_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("authenticated"):

            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Authentication required."
                }), 401

            return redirect("/login")

        if session.get("role") != "teacher":

            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Teacher access required."
                }), 403

            return redirect("/admin/dashboard")

        return function(*args, **kwargs)

    return wrapper