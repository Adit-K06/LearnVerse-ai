import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def extract_key_concepts(full_text):
    """Uses Gemini to identify and list the key concepts from the text."""
    if not GEMINI_KEY:
        return ["Error: GEMINI_API_KEY not found."]
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f'Read the following textbook text and identify the main learning concepts. Return as a JSON list of strings. Text: "{full_text[:15000]}"'
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        return [f"Error extracting concepts: {e}"]

def generate_detailed_explanation_with_diagrams(context_text, concept_title):
    """
    Generates a detailed explanation with Mermaid.js diagrams embedded directly in the text.
    """
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY not found."
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Act as an expert science teacher. For the concept "{concept_title}", write a detailed explanation for a 10th-grade student.
        - Use headings, bold text, and bullet points to structure the content.
        - Break the explanation into multiple paragraphs.
        - **Integrate 2-3 simple Mermaid.js flowcharts (`graph TD`) directly within the explanation.**
          - Each diagram must be enclosed in ```mermaid ... ``` blocks.
          - Place them at logical points where a visual would be most helpful.

        Context: "{context_text[:12000]}"
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: Failed to generate explanation: {e}"

def generate_practical_scenario(concept_title, context_text):
    """Uses Gemini to create a practical, real-world scenario question."""
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY not found."
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Based on the concept of "{concept_title}", create a short, practical, real-world scenario problem for a 10th-grade student.
        The scenario should end with a question that requires the student to apply their knowledge.
        For example, for "Reflection of Light", a scenario could be: "You are standing by a calm lake in the morning and see a perfect reflection of a mountain. Based on the concept of relative motion, describe the mountain's state (at rest or in motion) from two different perspectives: a) Your perspective, standing at the bus stop. b) The perspective of another passenger sitting directly opposite Sarah inside the bus. For each perspective, explain your reasoning, explicitly stating the reference point used for your observation."
        Return only the scenario and the question.

        Context: "{context_text[:2000]}"
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating scenario: {e}"

def evaluate_user_answer(scenario, user_answer, context_text):
    """Uses Gemini to evaluate the user's answer to the scenario and provide feedback."""
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY not found."
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        A student was given the following scenario:
        ---
        {scenario}
        ---
        The student provided this answer:
        ---
        {user_answer}
        ---
        Based on the correct scientific principles from the context below, evaluate the student's answer.
        - Start with "### Feedback:"
        - Clearly state if their reasoning is correct, partially correct, or incorrect.
        - Provide a simple, encouraging explanation of the correct answer and why.
        - Use markdown for formatting.

        Correct Context: "{context_text[:4000]}"
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error evaluating answer: {e}"