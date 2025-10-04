import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def generate_quiz_questions(concept_text):
    """Uses Gemini to generate a multiple-choice quiz from the concept text."""
    if not GEMINI_KEY:
        return {"error": "GEMINI_API_KEY not found."}
    
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Based on the following educational text, create a JSON object for a quiz.
        The JSON object must have one key: "questions".
        The value should be a list of 5 multiple-choice question objects.
        Each question object must have three keys:
        1. "question_text": The question itself.
        2. "options": A list of 4 strings, where one is the correct answer.
        3. "correct_answer": The string of the correct answer from the "options" list.

        Educational Text:
        "{concept_text[:4000]}"
        """
        
        response = model.generate_content(prompt)
        # Clean up potential markdown formatting from the response
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        quiz_data = json.loads(json_text)
        return quiz_data

    except Exception as e:
        return {"error": f"Failed to generate quiz: {e}"}