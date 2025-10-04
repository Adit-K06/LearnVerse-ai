import streamlit as st
import os
import re
from dotenv import load_dotenv
from streamlit_mermaid import st_mermaid

# --- Local Imports ---
from ai_core.extractor import extract_text_from_pdf
from ai_core.generator import extract_key_concepts, generate_detailed_explanation_with_diagrams, generate_practical_scenario, evaluate_user_answer
from ai_core.quiz_generator import generate_quiz_questions
from ai_core.utils import ensure_dir

# --- Load Environment Variables ---
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="AI Interactive Learning", layout="wide")
st.title("🧠 AI Interactive Learning Assistant")

# --- Initializations ---
OUTPUT_DIR = "output"
ensure_dir(OUTPUT_DIR)

# Initialize session state
if 'concepts' not in st.session_state: st.session_state.concepts = []
if 'selected_concept' not in st.session_state: st.session_state.selected_concept = None
if 'explanation' not in st.session_state: st.session_state.explanation = ""
if 'scenario' not in st.session_state: st.session_state.scenario = None
if 'feedback' not in st.session_state: st.session_state.feedback = None

# --- Sidebar ---
with st.sidebar:
    st.header("1. Get Started")
    pdf_file = st.file_uploader("Upload Chapter PDF", type="pdf")

    if pdf_file and st.button("Analyze Chapter"):
        st.session_state.concepts, st.session_state.selected_concept, st.session_state.explanation = [], None, ""
        st.session_state.scenario, st.session_state.feedback = None, None
        
        with st.spinner("Reading PDF and finding key concepts..."):
            file_path = os.path.join(OUTPUT_DIR, pdf_file.name)
            with open(file_path, "wb") as f: f.write(pdf_file.getbuffer())
            st.session_state.full_text = extract_text_from_pdf(file_path)
            if st.session_state.full_text:
                st.session_state.concepts = extract_key_concepts(st.session_state.full_text)
                st.success("Analysis complete! Please choose a concept.")
            else:
                st.error("Could not extract text from the PDF.")

    if st.session_state.concepts and not st.session_state.concepts[0].lower().startswith("error"):
        st.header("2. Choose a Concept")
        selected = st.radio("Topics:", st.session_state.concepts, key="concept_radio")
        if selected != st.session_state.selected_concept:
            st.session_state.selected_concept, st.session_state.explanation = selected, ""
            st.session_state.scenario, st.session_state.feedback = None, None
            st.rerun()

# --- Main Content Area ---
if not st.session_state.selected_concept:
    st.info("Upload a PDF and click 'Analyze Chapter' to begin.")
else:
    st.header(f"📖 Learning: {st.session_state.selected_concept}")

    if not st.session_state.explanation:
        with st.spinner("Generating your detailed lesson with visuals..."):
            explanation_data = generate_detailed_explanation_with_diagrams(st.session_state.full_text, st.session_state.selected_concept)
            if "error" in explanation_data.lower():
                st.error(explanation_data)
                st.session_state.explanation = "Failed"
            else:
                st.session_state.explanation = explanation_data

    if st.session_state.explanation and st.session_state.explanation != "Failed":
        # Use regex to find and render mermaid diagrams inline
        parts = re.split(r"(```mermaid.*?```)", st.session_state.explanation, flags=re.DOTALL)
        for i, part in enumerate(parts):
            if part.strip():
                if part.startswith("```mermaid"):
                    mermaid_code = part.replace("```mermaid", "").replace("```", "").strip()
                    st_mermaid(mermaid_code, height="400px", key=f"mermaid_{i}")
                else:
                    st.markdown(part, unsafe_allow_html=True)
        st.markdown("---")

        # --- INTERACTIVE SCENARIO SECTION ---
        st.subheader("🚀 Apply Your Knowledge!")
        if st.button("Generate a Practical Scenario"):
            with st.spinner("AI is creating a scenario for you..."):
                st.session_state.feedback = None
                scenario_text = generate_practical_scenario(st.session_state.selected_concept, st.session_state.explanation)
                if "error" in scenario_text.lower():
                    st.error(scenario_text)
                else:
                    st.session_state.scenario = scenario_text
        
        if st.session_state.scenario:
            st.info(st.session_state.scenario)
            with st.form(key="scenario_form"):
                user_solution = st.text_area("Your solution:")
                submitted = st.form_submit_button("Submit Solution")
                if submitted:
                    with st.spinner("AI is evaluating your answer..."):
                        feedback = evaluate_user_answer(st.session_state.scenario, user_solution, st.session_state.explanation)
                        st.session_state.feedback = feedback
        
        if st.session_state.feedback:
            st.markdown(st.session_state.feedback)
        st.markdown("---")
        
        # --- QUIZ SECTION ---
        st.subheader("✍️ Test Your Knowledge!")
        if st.button("Start Quiz"):
            with st.spinner("AI is generating your quiz questions..."):
                quiz_data = generate_quiz_questions(st.session_state.explanation)
                if "error" in quiz_data:
                    st.error(quiz_data["error"])
                else:
                    st.session_state.quiz_questions = quiz_data.get("questions", [])
                    st.session_state.current_question_index = 0
                    st.session_state.score = 0
        
        if 'quiz_questions' in st.session_state and st.session_state.quiz_questions:
            # Quiz display logic remains the same
            index = st.session_state.current_question_index
            if index < len(st.session_state.quiz_questions):
                q = st.session_state.quiz_questions[index]
                with st.form(key=f"quiz_form_{index}"):
                    st.write(f"**Question {index + 1}:** {q['question_text']}")
                    user_answer = st.radio("Choose your answer:", q['options'], key=f"q_options_{index}")
                    submitted = st.form_submit_button("Submit Answer")
                    if submitted:
                        if user_answer == q['correct_answer']:
                            st.success("Correct! 🎉")
                            st.session_state.score += 1
                        else:
                            st.error(f"Not quite. The correct answer was: **{q['correct_answer']}**")
                        st.session_state.current_question_index += 1
                        st.rerun()
            else:
                st.success(f"Quiz Complete! Your final score: {st.session_state.score} / {len(st.session_state.quiz_questions)}")
                st.balloons()
                del st.session_state.quiz_questions