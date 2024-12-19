import re
import json
import pickle


def parse_latex_resume(latex_text):
    # Define patterns for different parts of the LaTeX
    text_bf = r"\\textbf{(.+?)}"
    latex_text = re.sub(r"\\%", "%", latex_text)
    latex_text = re.sub(text_bf, r"**\1**", latex_text)

    # matches \section{...}
    section_pattern = r"\\section{(.+?)}"

    # matches \resumeSubheading{...}{...}{...}{...}
    subheading_pattern = re.compile(
        r"\\resumeSubheading\s*{(.+?)}\s*{(.+?)}\s*{(.+?)}\s*{(.+?)}"  # Subheading
        r"(.*?)\\resumeItemListEnd",  # Non-greedy match for everything until \resumeItemListEnd
        re.DOTALL,  # Match across multiple lines
    )
    # matches \resumeItem{...}
    bullet_point_pattern = re.compile(r"\\resumeItem\s*{(.+?)}", re.DOTALL)

    # matches \resumeProjectHeading{\textbf{...}...}{...}
    project_pattern = re.compile(
        r"\\resumeProjectHeading\s*{(.+?)}\s*{(.+?)}\s*{(.+?)}"
        r"(.*?)\\resumeItemListEnd",
        re.DOTALL,
    )

    # Initialize result dictionary
    parsed_data = {"sections": []}

    # Find sections
    sections = re.findall(section_pattern, latex_text)
    for section in sections:
        section_data = {"name": section, "entries": []}
        # Extract entries within each section
        if section.lower() == "experience":
            exp_matches = subheading_pattern.finditer(latex_text)
            for match in exp_matches:
                role, company, location, duration, items_block = match.groups()
                entry = {
                    "position_name": role.strip(),
                    "company_name": company.strip(),
                    "location": location.strip(),
                    "start_date": duration.split("--")[0].strip(),
                    "end_date": duration.split("--")[1].strip(),
                    "responsibilities": bullet_point_pattern.findall(items_block),
                }
                section_data["entries"].append(entry)

        elif section.lower() == "projects":
            project_matches = project_pattern.finditer(latex_text)
            for match in project_matches:
                project_name, tech_stack, date, items_block = match.groups()
                entry = {
                    "project_name": project_name.strip(),
                    "date": date.strip(),
                    "tech_stack": tech_stack.strip(),
                    "details": bullet_point_pattern.findall(items_block),
                }
                # Extract bullet points for this project
                section_data["entries"].append(entry)

        # Add section data to result
        parsed_data["sections"].append(section_data)

    return parsed_data


def save_resume(parsed_data, output_file_path):
    if not output_file_path.endswith(".pkl"):
        output_file_path += ".pkl"
    with open(output_file_path, "wb") as f:
        pickle.dump(parsed_data, f)


def load_resume(input_file_path):
    if not input_file_path.endswith(".pkl"):
        input_file_path += ".pkl"
    input_file = pickle.load(open(input_file_path, "rb"))
