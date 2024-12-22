from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field
from typing import Optional


class EntryEvaluation(BaseModel):
    """
    Represents the evaluation of a resume entry by an expert recruiter for technical roles.

    This class is designed to assess the relevance of a resume entry in relation to a specific job posting.

    The evaluation focuses on technical skills and experience, temporarily ignoring soft skills.
    The expert will score candidates based on three main categories: relevance of experience, technical skills demonstrated, and impact and outcomes. Each category has a defined scoring range, allowing for a total score out of 10.

    The evaluation process is crucial for ensuring that candidates are matched effectively and correctly evaluated. That is why evaluation must be done rigorously, focusing on the candidate's ability to meet the requirements of the job posting.
    """

    comments: str = Field(
        description="Detailed comments evaluating the relevance, quality, and suggestions for the resume entry. "
        "Include specific strengths and weaknesses of the entry."
    )

    suggestions: Optional[str] = Field(
        description="Specific suggestions for improving the resume entry itself. "
        "Focus on concrete changes that could enhance the match with the job posting, "
        "rather than general advice applicable to all resumes."
    )

    relevance_score: int = Field(
        description="""Numerical evaluation (0-5 points) of how relevant the resume entry is to the job posting. 
        A higher score indicates a closer alignment with the required experience for the role, 
        based on the following criteria:
         - **5 points:** Directly-related professional experience, such as intern, internships, or full-time roles in target field.
        - **4 points:** Related technical roles or projects, but is not directly involved in the target field. However, there might be a lot of transferable skills to be picked up here e.g. there is a lot of relevance between machine learning engineer and AI engineer/researcher intern.
        - **3 points**: Technical roles or projects that have little relevance in the target field, e.g. target field machine learning engineer and resume entry web developer.
        - **1-2 points:** General roles or projects that has little overlap. The variance depends on the amount of transferable skills, or the impressiveness/scale of the project, or role.
        - **0 points:** No relevant experience.
        """
    )

    technical_score: int = Field(
        description="""Numerical evaluation (0-3 points) of the technical skills demonstrated in the resume entry. 
        This score reflects the candidate's proficiency with relevant tools and technologies, 
        categorized as follows:
        - 3 points: Proficiency with highly relevant tools/technologies.
        - 2 points: Experience with broadly useful technologies.
        - 1 point: Basic technical skills with limited applicability.
        - 0 points: No demonstrable technical skills.
        """
    )

    impact_score: int = Field(
        description="""Numerical evaluation (0-2 points) of the impact and outcomes demonstrated in the resume entry. 
        This score assesses the candidate's ability to deliver quantifiable results, with the following criteria:
        - 2 points: Clear, quantifiable results showing high impact.
        - 1 point: Demonstrates problem-solving and value without strong metrics.
        - 0 points: No demonstrated outcomes.
        """
    )


def evaluate_resume_entry(entry, job_description, job_skills, project_mode=False):
    base = """
        You are an **expert recruiter specializing in technical roles**, with a focus on evaluating resume entries for their relevance to specific job postings. Your task is to score and provide feedback on the provided resume entry. Ignore soft skills and prioritize technical skills, experience, and demonstrated impact. Evaluation must be done rigorously, focusing on the candidate's ability to meet the requirements of the job posting.

        Score candidates using the following categories:

        1. **Relevance of Experience (0-5 points):**
        - **5 points:** Directly-related professional experience, such as intern, internships, or full-time roles in target field.
        - **4 points:** Related technical roles or projects, but is not directly involved in the target field. However, there might be a lot of transferable skills to be picked up here e.g. there is a lot of relevance between machine learning engineer and AI engineer/researcher intern.
        - **3 points**: Technical roles or projects that have little relevance in the target field, e.g. target field machine learning engineer and resume entry web developer.
        - **1-2 points:** General roles or projects that has little overlap. The variance depends on the amount of transferable skills, or the impressiveness/scale of the project, or role.
        - **0 points:** No relevant experience.

        2. **Technical Skills Demonstrated (0-3 points):**
        - **3 points:** Proficiency with highly relevant tools/technologies for the role.
        - **2 points:** Experience with broadly useful technologies (e.g., general programming skills).
        - **1 point:** Basic technical skills with limited applicability.
        - **0 points:** No demonstrable technical skills.

        3. **Impact and Outcomes (0-2 points):**
        - **2 points:** Clear, quantifiable results showing high impact (e.g., “Reduced downtime by 20%”).
        - **1 points:** Demonstrates problem-solving and value without strong quantifiable metrics.
        - **0 points:** No demonstrated outcomes.

        **Total Score:** Add the scores from all categories for a score out of 10.
        """

    llm = ChatOllama(
        model="llama3.2", num_ctx=10000, temperature=0.2
    ).with_structured_output(EntryEvaluation)

    message_exp = """
        Evaluate the following experience entry for relevance to the job description.

        <RESUME ENTRY>
        Position: {position_name}
        Company: {company_name}
        Responsibilities:
        {responsibilities}
        </RESUME ENTRY>

        <JOB DESCRIPTION>
        {job_description}
        Skills Required:
        {skills}
        </JOB DESCRIPTION>
    """

    message_project = """
        Evaluate the following project entry for relevance to the job description:

        <RESUME ENTRY>
        Project: {project_name}
        Details:
        {details}
        Technologies Used:
        {tech_stack}
        </RESUME ENTRY>

        <JOB DESCRIPTION>
        {job_description}
        Skills Required:
        {skills}
        </JOB DESCRIPTION>
    """

    message = message_project if project_mode else message_exp
    prompt = ChatPromptTemplate.from_messages([("system", base), ("human", message)])

    chain = prompt | llm

    response = None
    if project_mode:
        print("project mode initiated")
        response = chain.invoke(
            {
                "project_name": entry["project_name"],
                "details": ";".join(entry["details"]),
                "tech_stack": entry["tech_stack"],
                "job_description": job_description,
                "skills": job_skills,
            }
        )
    else:
        print("experience mode initiated")
        response = chain.invoke(
            {
                "position_name": entry["position_name"],
                "company_name": entry["company_name"],
                "responsibilities": ";".join(entry["responsibilities"]),
                "job_description": job_description,
                "skills": job_skills,
            }
        )
    return response
