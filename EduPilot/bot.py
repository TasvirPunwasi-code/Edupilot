# Imports the os module to access environment variables
import os

# Imports load_dotenv to load variables from the .env file
from dotenv import load_dotenv

# Imports the Google Gen AI library used to connect to Gemini
from google import genai

# Imports configuration types used to control the Gemini AI
from google.genai import types

# Loads environment variables from the .env file
load_dotenv()

# Gets the Gemini API key from the environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

# Checks if the Gemini API key was successfully found
if not API_KEY:

    # Stops the application if the API key is missing
    raise ValueError("GEMINI_API_KEY was not found in the .env file.")

# Creates the system prompt that defines the role and rules of the EduPilot AI Assistant
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

# Creates the Gemini client using the API key. This allows EduPilot to communicate with the Gemini AI service
client = genai.Client(api_key=API_KEY)

# Creates the configuration that controls how the AI responds
config = types.GenerateContentConfig(

    # Gives Gemini the EduPilot rules and instructions defined above
    system_instruction=EDUPILOT_PROMPT,

    # Uses a low temperature to keep responses more focused and consistent
    temperature=0.3
)


# Creates the Gemini chat session
chat = client.chats.create(
    # Specifies the Gemini model used by the EduPilot chatbot
    model="gemini-3.5-flash-lite",
    # Applies the EduPilot chat configuration to the model
    config=config
)


# Creates the function used by the Flask chatbot route to get an AI response
def get_bot_response(message):
    # Checks if the teacher's message is empty
    if not message:
        # Returns a message asking the teacher to enter a question
        return "Please enter a question."

    # Sends the teacher's message to Gemini and stores the generated response
    response = chat.send_message(message)

    # Extracts and returns only the text from Gemini's response
    return response.text
