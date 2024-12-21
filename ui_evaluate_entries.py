import streamlit as st

from exec.agent import evaluate_resume_entry

resume_data = st.session_state.resume_data
job_skills = st.session_state.job_skills

st.write("# Tailoring")
st.write("## Role debrief")
st.write("### General Responsibilities")
st.write(st.session_state.hlr)
st.write("### Skills")
st.write(job_skills)

st.write("## Relevance evaluation")
if st.button("Evaluate bullets"):
    # for each entry, gather context -> feed into LLM
    # LLM should gather context between job description and resume -> give a score as to how close each project / experience is to the line of work involved in the job description
    for section in resume_data["sections"]:
        for entry in section["entries"]:
            if section["name"].lower() == "experience":
                st.write(
                    "### Entry:", entry["position_name"], "at", entry["company_name"]
                )
            elif section["name"].lower() == "projects":
                st.write("### Entry:", entry["project_name"])

            st.write(entry)

            model_response = evaluate_resume_entry(
                entry,
                job_description=st.session_state.hlr,
                job_skills=", ".join(job_skills),
                project_mode=(section["name"].lower() == "projects"),
            )
            retries = 1
            while not model_response:
                st.write(
                    f"Model did not produce any output. Retrying {retries} times..."
                )
                model_response = evaluate_resume_entry(
                    entry,
                    job_description=st.session_state.hlr,
                    job_skills=", ".join(job_skills),
                    project_mode=(section["name"].lower() == "projects"),
                )

            st.write("Comments:", model_response.comments)
            st.write("Suggestions:", model_response.suggestions)
            st.write("Score:", model_response.evaluation)
            st.write("Final verdict:", model_response.keep_or_throw)
