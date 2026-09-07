# Imports the Flask tools needed for routes, HTML pages, requests and JSON responses
from flask import Blueprint, render_template, request, jsonify

# Imports the function that generates the chatbot's response
from bot import get_bot_response

# Imports the security check that allows only teachers to access the chatbot
from routes.security import teacher_required

# Creates a Blueprint to group all chatbot-related routes
chatbot_bp = Blueprint("chatbot", __name__)

# Creates the route used to open the teacher chatbot page
@chatbot_bp.route("/teacher/chatbot")

# Checks that the user is an authorised teacher before opening the page
@teacher_required
def chatbot_page():

    # Loads and displays the teacher AI chatbot HTML page
    return render_template("TeacherDashboard(AIChatbot).html")

# Creates the API route that receives chatbot messages from the frontend.This route only accepts POST requests
@chatbot_bp.route("/api/chatbot", methods=["POST"])

# Makes sure only authorised teachers can use the chatbot API
@teacher_required
def chatbot():
    # Starts error handling in case something goes wrong
    try:
        # Gets the JSON data sent from the chatbot frontend
        data = request.get_json()

        # Checks if any data was received
        if not data:
            # Returns an error if no chatbot data was sent
            return jsonify({
                "success": False,
                "message": "No chatbot message received."
            }), 400

        # Gets the message from the JSON data
        # str() converts it to text and strip() removes extra spaces
        message = str(data.get("message", "")).strip()

        # Checks if the user entered an empty message
        if not message:
            # Returns an error asking the user to enter a message
            return jsonify({
                "success": False,
                "message": "Please enter a message."
            }), 400

        # Sends the user's message to the bot and stores the generated response
        response = get_bot_response(message)

        # Sends the chatbot response back to the frontend as JSON. Status code 200 means the request was successful
        return jsonify({
            "success": True,
            "response": response
        }), 200

    # Catches any unexpected errors that occur while processing the message
    except Exception as error:
        # Prints the actual error in the terminal to help with debugging
        print("CHATBOT ERROR:", error)

        # Returns a user-friendly error message.Status code 500 means an internal server error occurred
        return jsonify({
            "success": False,
            "message": "The AI Assistant could not process your request."
        }), 500
