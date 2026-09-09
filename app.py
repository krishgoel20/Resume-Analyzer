import streamlit as st
from file_utils import extract_text
from guardrails import validate_file_size
from graph import pipeline

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖")
st.title("🤖 AI Resume & Job Description Analyzer")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Resume**")
    uploaded_file = st.file_uploader("Upload a file (.pdf or .docx)", type=["pdf", "docx"])
    resume_text_input = st.text_area("...or Paste text", height=250)

    if uploaded_file is not None:
        try:
            validate_file_size(uploaded_file)
            resume_text = extract_text(uploaded_file)
            st.success(f"Using uploaded file: {uploaded_file.name}")
        except ValueError as e:
            st.error(str(e))
            resume_text = ""
    else:
        resume_text = resume_text_input

with col2:
    job_description = st.text_area("Paste the Job Description", height=300)

if st.button("Analyze"):
    if not resume_text.strip() or not job_description.strip():
        st.warning("Please fill in both fields.")
    else:
        with st.spinner("Analyzing..."):
            final_state = pipeline.invoke({
                "resume_text": resume_text,
                "job_description": job_description,
                "error": None,
                "result": None,
                "warnings": [],
            })

        if final_state["error"] is not None:
            st.error(final_state["error"])
        else:
            result = final_state["result"]

            for warning in final_state["warnings"]:
                st.warning(warning)

            st.subheader(f"Match Score: {result.match_score}/100")
            st.progress(result.match_score / 100)

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("### ✅ Matching Skills")
                for skill in result.matching_skills:
                    st.markdown(f"- {skill}")

            with col_b:
                st.markdown("### ❌ Missing Skills")
                for skill in result.missing_skills:
                    st.markdown(f"- {skill}")

            st.markdown("### 💡 Suggestions")
            for suggestion in result.suggestions:
                st.markdown(f"- {suggestion}")