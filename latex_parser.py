import re
import json


def parse_latex_resume(latex_text):
    # Define patterns for different parts of the LaTeX
    text_bf = r"\\textbf{(.+?)}"
    latex_text = re.sub(r"\\%", "%", latex_text)
    latex_text = re.sub(text_bf, r"**\1**", latex_text)

    # matches \section{...}
    section_pattern = r"\\section{(.+?)}"

    # matches \resumeSubheading{...}{...}{...}{...}
    subheading_pattern = r"\\resumeSubheading\s*{(.+?)}\s*{(.+?)}\s*{(.+?)}\s*{(.+?)}"

    # matches \resumeItem{...}
    item_pattern = r"\\resumeItem\s*{(.+?)}"

    # matches \resumeProjectHeading{\textbf{...}...}{...}
    project_pattern = r"\\resumeProjectHeading\s*{\s*\\textbf{(.+?)}.*?}\s*{\s*(.+?)}"

    # Initialize result dictionary
    parsed_data = {"sections": []}

    # Find sections
    sections = re.findall(section_pattern, latex_text)
    for section in sections:
        section_data = {"name": section, "entries": []}

        # Extract entries within each section
        if section.lower() == "experience":
            experience_matches = re.findall(subheading_pattern, latex_text)
            for match in experience_matches:
                position, company, location, dates = match
                entry = {
                    "position_name": position.strip(),
                    "company_name": company.strip(),
                    "location": location.strip(),
                    "start_date": dates.split("--")[0].strip(),
                    "end_date": dates.split("--")[1].strip(),
                    "responsibilities": [],
                }
                # Extract bullet points for this entry
                bullets = re.findall(item_pattern, latex_text)
                entry["responsibilities"].extend([bullet.strip() for bullet in bullets])
                section_data["entries"].append(entry)

        elif section.lower() == "projects":
            project_matches = re.findall(project_pattern, latex_text)
            for match in project_matches:
                project_name, date = match
                entry = {
                    "project_name": project_name.strip(),
                    "date": date.strip(),
                    "details": [],
                }
                # Extract bullet points for this project
                bullets = re.findall(item_pattern, latex_text)
                entry["details"].extend([bullet.strip() for bullet in bullets])
                section_data["entries"].append(entry)

        # Add section data to result
        parsed_data["sections"].append(section_data)

    return parsed_data


if __name__ == "__main__":
    latex_source = r"""
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {AI Researcher/Engineer Intern}{Kyanon Digital}
      {Vietnam}{May -- August 2024}
      \resumeItemListStart
        \resumeItem{Enhanced customer profiling accuracy \textbf{by 22\%} by applying transformer-based embedding models to transaction data.}
        \resumeItem{Designed PoC to solve cold-start and knowledge transfer challenges in recommender systems, increasing baseline XGBoost accuracy \textbf{by 10\%}, leading to improved targeting for personalized marketing campaigns.}
        \resumeItem{Delivered tabular learning proposal using \textbf{PyTorch} and \textbf{HuggingFace}, enhancing model deployment with \textbf{Docker} and \textbf{Streamlit} for user-friendly ML applications.}
      \resumeItemListEnd

    \resumeSubheading
      {Software Engineering Lab Assistant}{Univ. of South Florida RANCS Lab}{Tampa}{October 2023 -- Present}
      \resumeItemListStart
        \resumeItem{Collaborated on autonomous vehicle engineering, integrating \textbf{lidars, radars, cameras}, and controllers for sensor fusion.}
        \resumeItem{Developed C++ SDK and network socket libraries for Cohda on-board units, enabling custom data packet transmission.}
        \resumeItem{Programmed firmware for GNSS (GPS) devices, ensuring high-accuracy data for an FDOT autonomous bus project.}
      \resumeItemListEnd
  \resumeSubHeadingListEnd

%----------- Projects ------------%
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {\textbf{the last data structures visualizer you will ever need} $|$ \emph{Vite, Chakra-UI}}{January 2024}
          \resumeItemListStart
            \resumeItem{Created interactive visualizations for graphs, trees, and various data structures with react-force-graph and Vite.}
            \resumeItem{Optimized animation performance for Dijkstra's algorithm and A* pathfinding using memoization and batch updates, achieving a \textbf{120\% reduction} in rendering latency (\textbf{+20\% average frames} per second, \textbf{-30ms average time} to render).}
          \resumeItemListEnd
      \resumeProjectHeading
          {\textbf{LegAI} $|$ \emph{NextJS, FastAPI, Python, PostgreSQL, ChromaDB}}{October 2023}
          \resumeItemListStart
            \resumeItem{Optimized embedding storage in PostgreSQL using ChromaDB references, resulting in a \textbf{90\% increase} in retrieval speed.}
            \resumeItem{Developed a scalable Fast API backend to support high-volume image and text processing with \textbf{Ada-002 text embeddings} and \textbf{LangChain}, resulting in \textbf{15\% increase}s in accurate content identification.}
          \resumeItemListEnd
    \resumeSubHeadingListEnd
"""

    parsed_data = parse_latex_resume(latex_source)
    print(json.dumps(parsed_data, indent=2))
