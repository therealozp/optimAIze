import streamlit as st
import os

st.title("Resume rewriter")
st.write("Rewrite your resume based on the job description because why not")

if os.path.exists("resume.tex") or os.path.exists("resume.txt"):
    st.write(
        'Found an existing resume file. Click "Upload Resume" to upload a new resume.'
    )
st.write("Upload your resume:")
job_description_file = st.file_uploader("Resume", type=["txt", "tex"])

if job_description_file is not None:
    job_description = job_description_file.read()
    with st.container(height=500):
        st.write(job_description)

st.write("Paste the job description here:")
job_description = st.text_area("Job Description", height=500)
