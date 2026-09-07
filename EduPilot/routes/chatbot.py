from flask import Blueprint, render_template, request, jsonify
from bot import get_bot_response
from routes.security import teacher_required

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/teacher/chatbot")
@teacher_required
def chatbot_page():
    return render_template("TeacherDashboard(AIChatbot).html")


@chatbot_bp.route("/api/chatbot", methods=["POST"])
@teacher_required
def chatbot():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No chatbot message received."
            }), 400

        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "success": False,
                "message": "Please enter a message."
            }), 400

        response = get_bot_response(message)

        return jsonify({
            "success": True,
            "response": response
        }), 200

    except Exception as error:
        print("CHATBOT ERROR:", error)

        return jsonify({
            "success": False,
            "message": "The AI Assistant could not process your request."
        }), 500