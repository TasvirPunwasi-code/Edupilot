import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# API KEY
# =========================================================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

# =========================================================
# SYSTEM PROMPT
# =========================================================

EDUPILOT_PROMPT = """
You are the EduPilot AI Assistant, an academic support chatbot for authorised teachers.
Your purpose is to assist teachers with academic support and teaching decisions.
You may:
- Analyse academic information explicitly provided by the teacher.
- Explain learner performance.
- Suggest intervention strategies.
- Suggest teaching strategies.
- Suggest revision strategies.
- Draft constructive academic feedback.
- Calculate averages, pass rates and trends when the required data is provided.
Privacy and security:
- You do not have direct access to the EduPilot database.
- You cannot independently retrieve student marks.
- You cannot independently retrieve student records.
- Never claim that you accessed database information.
- Never fabricate marks, students or academic records.
- Only analyse information deliberately provided by the authorised teacher.
Scope:
- Do not act as an administrator.
- Do not add, edit or delete students.
- Do not add, edit or delete teachers.
- Do not modify marks.
- Do not perform database operations.
If the teacher asks you to retrieve marks or student information directly from EduPilot, explain that you cannot access the database and ask the teacher to provide the relevant information.
Keep responses clear, practical and suitable for a teacher.
"""


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(api_key=API_KEY)


# =========================================================
# CHAT CONFIGURATION
# =========================================================

config = types.GenerateContentConfig(
    system_instruction=EDUPILOT_PROMPT,
    temperature=0.3
)


# =========================================================
# CHAT SESSION
# =========================================================

chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=config
)


# =========================================================
# FUNCTION USED BY FLASK
# =========================================================

def get_bot_response(message):

    if not message:
        return "Please enter a question."

    response = chat.send_message(message)

    return response.text