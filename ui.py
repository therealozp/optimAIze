import streamlit as st
from latex_parser import parse_latex_resume

from process_job_description import (
    extract_all_information,
    extract_high_level_responsibilites,
)

from skill_ner import get_skills
from streamlit_tags import st_tags

from agent import evaluate_resume_entry


def st_write_bullet(entry):
    if not entry:
        return
    st.write(entry["position_name"], "at", entry["company_name"])
    st.write(entry["location"], ":", entry["start_date"], "-", entry["end_date"])
    st.write("bullets:")
    for bullet in entry["responsibilities"]:
        st.write("-", bullet)


st.title("Resume rewriter")
st.write("Rewrite your resume based on the job description because why not")

st.write("# Preprocessing")
st.write("## Resume")
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None

if st.session_state.resume_data is not None:
    st.write("**There is a resume found in the system.**")

st.write("Upload your resume:")
resume_file = st.file_uploader("Resume", type=["txt", "tex"])


if resume_file is not None:
    resume_bytes = resume_file.read()
    resume = resume_bytes.decode("utf-8")

    parsed_data = parse_latex_resume(resume)
    st.session_state.resume_data = parsed_data

resume_data = st.session_state.resume_data
if resume_data is not None:
    st.write(resume_data)
    with st.container(height=500):
        for section in resume_data["sections"]:
            if section["name"].lower() == "experience":
                for entry in section["entries"]:
                    st.write(entry["position_name"], "at", entry["company_name"])
                    st.write(
                        entry["location"],
                        ":",
                        entry["start_date"],
                        "-",
                        entry["end_date"],
                    )
                    for bullet in entry["responsibilities"]:
                        st.write("-", bullet)
            elif section["name"].lower() == "projects":
                for entry in section["entries"]:
                    st.write(entry["project_name"])
                    st.write(entry["date"])
                    st.write(entry["tech_stack"])
                    for bullet in entry["details"]:
                        st.write("-", bullet)

st.write("## Job Description")
st.write("Paste the job description here:")
job_description = st.text_area("Job Description", height=500)

if "job_info" not in st.session_state:
    st.session_state.job_info = None

job_skills = []
if job_description:
    if st.button("extract job information"):
        # allows users to keep pressing until ready
        with st.spinner("Wait for it..."):
            st.session_state.job_info = extract_all_information(job_description)
            job_skills = get_skills(job_description)

if st.session_state.job_info:
    job_info = st.session_state.job_info
    st.write("### Company name:")
    st.write(job_info.company_name)
    st.write("### Job title:")
    st.write(job_info.job_title)
    st.write("### Location:")
    st.write(job_info.location)
    st.write("### Company description:")
    st.write(job_info.company_description)
    st.write("### Responsibilities description:")
    st.write(job_info.responsibilities_description)

if st.session_state.job_info and st.button("(re)generate high-level responsibilities"):
    with st.spinner("Wait for it..."):
        high_level_responsibilities = extract_high_level_responsibilites(
            job_info.responsibilities_description
        )
        st.session_state.hlr = high_level_responsibilities.high_level_objectives

st.write("Extracted high-level responsibilities")
if "hlr" in st.session_state:
    hlr_value = st.text_area("High-level responsibilities", value=st.session_state.hlr)
    if button := st.button("Update high-level responsibilities"):
        st.session_state.hlr = hlr_value

    # recognized keywords

# # recognized keywords in the resume
# if resume_data:
#     resume_skills = get_skills(resume)
#     rkw = st_tags(
#         job_skills,
#         label="### Skills in Resume",
#         key="resume_skills",
#         text="type to add more",
#     )
#     print(rkw)

### tailoring
# tailor all bullets
st.write("# Tailoring")
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

            st.write("Comments:", model_response.comments)
            st.write("Score:", model_response.evaluation)
            st.write("Final verdict:", model_response.keep_or_throw)
