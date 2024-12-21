import streamlit as st
import pickle
from pathlib import Path

from preprocess.latex_parser import parse_latex_resume


# Functions
def save_to_file(filepath):
    with open(filepath, "wb") as f:
        pickle.dump(st.session_state.resume_data, f)


def load_from_file(filepath):
    if Path(filepath).is_file():
        with open(filepath, "rb") as f:
            st.session_state.resume_data = pickle.load(f)
        st.success(f"Data loaded from {filepath}")
    else:
        st.error("File not found!")


st.sidebar.header("Save/Load Data")
save_path = st.sidebar.text_input("Save File Path", "resume_data.pkl")
if st.sidebar.button("Save"):
    try:
        save_to_file(save_path)
        st.success(f"Data successfully saved to {save_path}!")
    except Exception as e:
        st.error(f"Error saving data: {e}")


load_path = st.sidebar.text_input("Load File Path", "resume_data.pkl")
if st.sidebar.button("Load"):
    try:
        load_from_file(load_path)
        st.rerun()
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Initialize session state
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {
        "sections": [
            {"name": "Education", "entries": []},
            {"name": "Experience", "entries": []},
            {"name": "Projects", "entries": []},
            {"name": "Leadership", "entries": []},
            {"name": "Skills", "entries": []},
            {"name": "Honors & Awards", "entries": []},
        ]
    }


def add_entry_to_section(section_idx, entry_data):
    st.session_state.resume_data["sections"][section_idx]["entries"].append(entry_data)


def delete_bullet(section_idx, entry_idx, bullet_idx):
    del st.session_state.resume_data["sections"][section_idx]["entries"][entry_idx][
        "responsibilities"
    ][bullet_idx]


def update_bullet(section_idx, entry_idx, bullet_idx, new_text):
    st.session_state.resume_data["sections"][section_idx]["entries"][entry_idx][
        "responsibilities"
    ][bullet_idx] = new_text


# Main Layout
st.title("Resume Manager")

tab1, tab2, tab3 = st.tabs(["Manage Experience", "Manage Projects", "Upload Resume"])
resume_data = st.session_state.resume_data

# tab 1 allows management of experience directly
# through UI of the application
with tab1:
    st.header("Manage Experience")
    section = resume_data["sections"][1]
    for entry_idx, entry in enumerate(section["entries"]):
        if section["name"].lower() == "experience":
            st.write(f"**{entry['position_name']}** at **{entry['company_name']}**")
            st.write(
                f"{entry['location']} : {entry['start_date']} - {entry['end_date']}"
            )
            for bullet_idx, bullet in enumerate(entry["responsibilities"]):
                col1, col2 = st.columns([7, 1], gap="small")
                with col1:
                    editable_bullet = st.text_area(
                        f"Edit Bullet {bullet_idx + 1}",
                        bullet,
                        key=f"bullet_{1}_{entry_idx}_{bullet_idx}",
                    )
                    if editable_bullet != bullet:
                        update_bullet(1, entry_idx, bullet_idx, editable_bullet)
                        st.success("Bullet updated!")
                with col2:
                    st.write(" ")
                    st.write(" ")

                    if st.button(
                        "⛔",
                        key=f"delete_bullet_{1}_{entry_idx}_{bullet_idx}",
                    ):
                        delete_bullet(1, entry_idx, bullet_idx)
                        st.rerun()

            if st.button("Add Bullet", key=f"add_bullet_{1}_{entry_idx}"):
                entry["responsibilities"].append("New responsibility")
                st.rerun()

    with st.expander(f"Add new entry to Experiences"):
        new_position = st.text_input("Position Name", key=f"new_position_{1}")
        new_company = st.text_input("Company Name", key=f"new_company_{1}")
        new_location = st.text_input("Location", key=f"new_location_{1}")
        new_start_date = st.text_input("Start Date", key=f"new_start_date_{1}")
        new_end_date = st.text_input("End Date", key=f"new_end_date_{1}")
        if st.button("Add Entry", key=f"add_entry_{1}"):
            add_entry_to_section(
                1,
                {
                    "position_name": new_position,
                    "company_name": new_company,
                    "location": new_location,
                    "start_date": new_start_date,
                    "end_date": new_end_date,
                    "responsibilities": [],
                },
            )
            st.rerun()

# tab 2 allows management of projects directly.
# similar to tab1, but for projects
with tab2:
    section = resume_data["sections"][2]
    for entry_idx, entry in enumerate(section["entries"]):
        st.write(f"**{entry['project_name']}**")
        st.write(f"{entry['date']} | {entry['tech_stack']}")
        for bullet_idx, bullet in enumerate(entry["details"]):
            col1, col2 = st.columns([4, 1])
            with col1:
                editable_bullet = st.text_area(
                    f"Edit Bullet {bullet_idx + 1}",
                    bullet,
                    key=f"bullet_{2}_{entry_idx}_{bullet_idx}",
                )
                if editable_bullet != bullet:
                    update_bullet(2, entry_idx, bullet_idx, editable_bullet)
                    st.success("Bullet updated!")
            with col2:
                if st.button("⛔", key=f"delete_bullet_{2}_{entry_idx}_{bullet_idx}"):
                    delete_bullet(2, entry_idx, bullet_idx)
                    st.rerun()

        if st.button("Add Bullet", key=f"add_bullet_{2}_{entry_idx}"):
            entry["details"].append("New detail")
            st.rerun()

    with st.expander(f"Add new entry to Projects"):
        new_project_name = st.text_input("Project Name", key=f"new_project_name_{2}")
        new_date = st.text_input("Date", key=f"new_date_{2}")
        new_tech_stack = st.text_input("Tech Stack", key=f"new_tech_stack_{2}")
        if st.button("Add Entry", key=f"add_entry_{2}"):
            add_entry_to_section(
                2,
                {
                    "project_name": new_project_name,
                    "date": new_date,
                    "tech_stack": new_tech_stack,
                    "details": [],
                },
            )
            st.rerun()

# tab 3 allows users to bootstrap information with a resume
with tab3:
    st.write("Upload your resume:")
    resume_file = st.file_uploader("Resume", type=["txt", "tex"])

    if st.button("Upload"):
        if resume_file is not None:
            resume_bytes = resume_file.read()
            resume = resume_bytes.decode("utf-8")

            parsed_data = parse_latex_resume(resume)
            st.session_state.resume_data = parsed_data
        st.rerun()

    resume_data = st.session_state.resume_data
    if resume_data is not None:
        with st.container():
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
