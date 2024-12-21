import streamlit as st

from preprocess.process_job_description import (
    extract_all_information,
    extract_high_level_responsibilites,
)

from preprocess.skill_ner import get_skills


def st_write_bullet(entry):
    if not entry:
        return
    st.write(entry["position_name"], "at", entry["company_name"])
    st.write(entry["location"], ":", entry["start_date"], "-", entry["end_date"])
    st.write("bullets:")
    for bullet in entry["responsibilities"]:
        st.write("-", bullet)


st.title("Process Job Description")
st.write("Rewrite your resume based on the job description because why not")

st.write("## Job Description")
st.write("Paste the job description here:")
job_description = st.text_area("Job Description", height=500)

if "job_info" not in st.session_state:
    st.session_state.job_info = None

if st.button("extract job information", disabled=not job_description):
    # allows users to keep pressing until ready
    with st.spinner("Wait for it..."):
        st.session_state.job_info = extract_all_information(job_description)
        job_skills = get_skills(job_description)
        st.session_state.job_skills = "|".join(job_skills)

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
    st.write("Extracted high-level responsibilities")
    with st.spinner("Wait for it..."):
        high_level_responsibilities = extract_high_level_responsibilites(
            job_info.responsibilities_description
        )
        st.session_state.hlr = high_level_responsibilities.high_level_objectives

if "hlr" in st.session_state:
    hlr_value = st.text_area("High-level responsibilities", value=st.session_state.hlr)
    if button := st.button("Update high-level responsibilities"):
        st.session_state.hlr = hlr_value
