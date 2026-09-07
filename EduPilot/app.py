import os
from flask import Flask, request
from dotenv import load_dotenv
from db import get_db_connection

from routes.students import students_bp
from routes.teachers import teachers_bp
from routes.events import events_bp
from routes.chatbot import chatbot_bp
from routes.auth import auth_bp
from routes.marks import marks_bp
from routes.backup import backup_bp
from routes.report_card import report_card_bp

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)

@app.after_request
def prevent_cache(response):

    if request.path.startswith("/teacher/") or request.path.startswith("/admin/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"


    return response
# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = os.getenv("FLASK_SECRET_KEY")


# =========================================================
# REGISTER BLUEPRINTS
# =========================================================

app.register_blueprint(auth_bp)
app.register_blueprint(students_bp)
app.register_blueprint(teachers_bp)
app.register_blueprint(events_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(marks_bp)
app.register_blueprint(report_card_bp)
app.register_blueprint(backup_bp)

# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )