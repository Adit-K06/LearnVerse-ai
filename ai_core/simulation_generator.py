import os
from dotenv import load_dotenv
import google.generativeai as genai
import re

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def generate_simulation_code(concept_title, context_text):
    """Generates self-contained HTML/JS code for an interactive simulation by injecting AI-written JS into a template."""
    if not GEMINI_KEY:
        return "Error: GEMINI_API_KEY not found."

    # This boilerplate provides the structure, so the AI only has to write the core logic.
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-g">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Simulation</title>
        <style>
            body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; margin: 0; background-color: #f0f0f0; }}
            #simulationCanvas {{ border: 1px solid #ccc; background-color: #fff; }}
            .controls {{ margin-top: 10px; padding: 0 10px; }}
            label {{ margin: 0 10px; }}
        </style>
    </head>
    <body>
        <h4>{concept_title} Simulation</h4>
        <canvas id="simulationCanvas" width="700" height="400"></canvas>
        <div class="controls" id="simulationControls">
            </div>

        <script>
            // --- AI-GENERATED JAVASCRIPT LOGIC GOES HERE ---
        </script>
    </body>
    </html>
    """

    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Act as an expert JavaScript developer. Your task is to write **only the JavaScript code** that goes inside the `<script>` tag of an HTML file to create an interactive simulation.
        - The simulation must be for the concept: **"{concept_title}"**.
        - It must run on the HTML canvas element with the id 'simulationCanvas'.
        - If you need interactive controls like sliders or buttons, generate the HTML for them and use JavaScript to insert them into the 'simulationControls' div.
        - The code must be self-contained and not require any external libraries.
        - Add comments to explain the logic.
        - Make it interactive (e.g., draggable objects, sliders to change values).
        - Do not include the `<script>` tags or any other HTML in your response. Output only the raw JavaScript code.

        Here is some context for the concept:
        "{context_text[:2000]}"
        """

        response = model.generate_content(prompt)
        
        # Clean up potential markdown formatting from the AI's response
        js_code = response.text.strip().replace("```javascript", "").replace("```", "")
        
        # Inject the AI-generated JavaScript into our HTML template
        final_html = html_template.replace("// --- AI-GENERATED JAVASCRIPT LOGIC GOES HERE ---", js_code)
        
        return final_html

    except Exception as e:
        return f"Error: Failed to generate simulation code: {e}"