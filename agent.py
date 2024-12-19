from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from process_job_description import (
    extract_all_information,
    extract_high_level_responsibilites,
)

from skill_ner import get_skills
from process_job_description import ActiveVerbRecommender

from pydantic import BaseModel, Field


class Agent:
    def __init__(self, job_description=None):
        self.llm = ChatOllama(model="llama3.2", num_ctx=10000, temperature=0.2)
        self.job_description = job_description
        self.bullet_samples_path = "samples/bullet-positive-samples.txt"

        self.processed_job_description = None
        self.high_level_responsibilities = None
        self.skills = None
        self.action_verbs = None
        self.bullet_samples = None

        self.load_bullet_samples()

    def load_bullet_samples(self):
        with open(self.bullet_samples_path, "r") as f:
            self.bullet_samples = ",".join(f.readlines())

    def process_job_description(self):
        while self.processed_job_description is None:
            jd = extract_all_information(self.job_description)
            print(jd.company_name)
            print(jd.job_title)
            print(jd.location)
            print(jd.company_description)
            print(jd.responsibilities_description)
            user_jd_ok = input(f"Is this the correct job description? (Y/N)")
            if user_jd_ok.lower() == "y":
                self.processed_job_description = jd
                break
            else:
                print("trying again...")

    def process_high_level_responsibilities(self):
        while self.high_level_responsibilities is None:
            hlr = extract_high_level_responsibilites(
                self.processed_job_description.responsibilities_description
            )
            print(hlr)
            user_hlr_ok = input(
                f"Is this the correct high level responsibilities? (Y/N)"
            )
            if user_hlr_ok.lower() == "y":
                self.high_level_responsibilities = hlr
                break
            else:
                print("trying again...")

    def process_skills(self):
        self.skills = get_skills(self.job_description)
        print("Recognized skills in processing: ", self.skills)

    def process_action_verbs(self):
        self.action_verbs = ActiveVerbRecommender().recommend(
            self.processed_job_description.responsibilities_description
        )

    def generate_prompt(self, bullet):
        base = """
        You are an assistant specializing in optimizing resume bullet points for maximum impact and technical clarity. For each bullet point provided, iterate through these steps:

        1. Evaluate the bullet point for impact, clarity, and relevance.
        2. If the bullet is of good quality and relevant, keep it as-is, and tell the user it's good.
        3. Enumerate improvements you plan to make to the bullet point.
        3. Deliver the final rewritten bullet point

        When a bullet point is rewritten, ensure the following criteria:
        - Be straightforward. Own the bullet point. No unnecessarily wordy statements.
        - No statements that are generic and cliche.
        - Everything should be clear. No vague and generic language.
        - Quantify and qualify achievements wherever possible. 
        - Use metrics, numbers, results to elaborate on impact.
        - The bullet point is authentic, engaging, and tailored to the provided job description.
        - Ensure readability. Use action verbs and concise language.
        """
        message = """
        Rewrite the bullet point below:

        <BULLET TO REWRITE>
        {bullet}
        </BULLET TO REWRITE>
        
        <BULLET CONTEXT>
        {bullet_context}
        </BULLET CONTEXT>
        
        <JOB DESCRIPTION>
        {job_description}
        </JOB DESCRIPTION>

        <RELEVANT TECHNOLOGIES>
        {relevant_technologies}
        </RELEVANT TECHNOLOGIES>

        <ACTION VERBS>
        {action_verbs}
        </ACTION VERBS>

        <EXAMPLE BULLETS FOR REFERENCE ONLY>
        {sample_bullets}
        </EXAMPLE BULLETS FOR REFERENCE ONLY>
        """
        return base, message

    def evaluate_entry(self, entry, job_description):
        prompt = """
        You are a robust candidate matcher who specializes in evaluating resumes for job postings. For the resume entry and job description provided, iterate through these steps:

        1. Evaluate the relevancy of the resume entry. Does the resume entry contain a lot of relevant experience that matches or transfer well to the type of work described inside the job posting? 
        
        For example, if the job posting is for a Web Developer:
         - a very good entry would have a lot of front-end and back-end work, explaining all different kinds of details.
         - a slightly worse match would contain only a simplistic programming project, with minimal effort. 
         - a bad match would contain no relevant programming work at all.
         
        2. Evaluate the quality of the resume entry. Is the resume entry well-written, clear, and concise? Does it contain a lot of jargon or buzzwords? Is it easy to read and understand? 
        3. Give your final evaluation of the resume entry. Is it a good match for the job posting? Why or why not? What could be improved in the resume entry to make it a better match? Or, should it be replaced entirely with another ? Format your answers to fall very clearly whether it deserves to be kept or thrown out. Be very pragmatic and clear in your evaluation.
        """

    def rewrite_bullet(self, bullet):
        self.process_job_description()
        self.process_high_level_responsibilities()
        self.process_skills()
        self.process_action_verbs()

        base, message = self.generate_prompt(bullet)

        prompt = ChatPromptTemplate.from_messages(
            {("system", base), ("human", message)}
        )

        chain = prompt | self.llm
        user_ok = "y"
        while user_ok.lower() == "y":
            response = chain.invoke(
                {
                    "bullet": bullet,
                    "job_description": self.high_level_responsibilities,
                    "relevant_technologies": self.skills,
                    "action_verbs": self.action_verbs,
                    "sample_bullets": self.bullet_samples,
                }
            )
            print("response received: ", response.content)
            user_ok = input("try again?")

        return response.content

    def rewrite_all_bullets(
        self,
        entry,
    ):
        for bullet in entry["responsibilities"]:
            rewritten_bullet = self.rewrite_bullet(bullet)
            print(rewritten_bullet)


class EntryEvaluation(BaseModel):
    comments: str = Field(
        description="Detailed comments evaluating the relevancy, quality, and suggestions for the resume entry."
    )
    evaluation: int = Field(
        description="Numerical evaluation of the resume entry on a scale of 1 to 10, with 10 being a perfect fit."
    )
    keep_or_throw: str = Field(
        description='Decision on the resume entry: "keep" if it is worth retaining or "throw" if it should be discarded.'
    )


def evaluate_resume_entry(entry, job_description, job_skills, project_mode=False):
    base = """
        You are an expert resume evaluator who evaluates resume entries for relevance to a job posting. For the resume entry and job description provided:
        
        Evaluate the relevance of the resume entry. Does the resume entry contain a lot of relevant experience that matches or transfer well to the type of work described inside the job posting? 
        
        For example, if the job posting is for a Site Reliability Engineer:
         - a stellar entry (10/10) would be direct professional experience in the field, such as an internship or similar that has directly involved maintaining or creating websites.
         - a less stellar entry (9/10) would be an internship that does not have to be related to web development, but not directly involved in the field; such as a Machine Learning position, or a Data Science position.
         - a good entry (7-9/10) is a high-quality position/project that has quantifiable metrics, solves a particular problem, and demonstrates technical skill. If the project utilizes relevant technologies, warrants an 8-9. If not so relevant, warrants a 7-8.
         - an "okay" match (4-6/10) would contain only a simplistic programming project, with minimal effort.
         - a bad match (0-4/10) would contain no relevant programming work at all.
        """

    llm = ChatOllama(
        model="llama3.2", num_ctx=10000, temperature=0.2
    ).with_structured_output(EntryEvaluation)

    message_exp = """
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
                "details": "\n".join(entry["details"]),
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
                "responsibilities": "\n".join(entry["responsibilities"]),
                "job_description": job_description,
                "skills": job_skills,
            }
        )
    return response
