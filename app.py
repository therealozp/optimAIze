import streamlit as st

pg = st.navigation(
    [
        st.Page("ui_manage_resume.py", title="Manage Resume Entries"),
        st.Page("ui_process_job.py", title="Process Job Description"),
        st.Page("ui_evaluate_entries.py", title="Evaluate Entries"),
    ],
)
pg.run()
