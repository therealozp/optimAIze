from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from process_job_description import (
    extract_all_information,
    extract_high_level_responsibilites,
)

from skill_ner import get_skills
from process_job_description import ActiveVerbRecommender


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

        with open(self.bullet_samples_path, "r") as f:
            self.bullet_samples = ",".join(f.readlines())

    def rewrite_bullet(self, bullet):
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
        # prompt consists of 5 main parts:
        # bullet point
        # relevant job description info, from extract_high_level_responsibilities
        # technologies required, from skill_ner
        # action verbs
        # sample bullet points

        message = """
        Rewrite the bullet point below:

        <BULLET TO REWRITE>
        {bullet}
        </BULLET TO REWRITE>
        
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

        print("processing job description...")
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
        else:
            print("job description has been processed, and entry exists in cache.")
        print()

        print("processing high level responsibilities...")
        while self.high_level_responsibilities is None:
            hlr = extract_high_level_responsibilites(jd.responsibilities_description)
            print(hlr)
            user_hlr_ok = input(
                f"Is this the correct high level responsibilities? (Y/N)"
            )
            if user_hlr_ok.lower() == "y":
                self.high_level_responsibilities = hlr
                break
            else:
                print("trying again...")
        else:
            print(
                "high level responsibilities have been processed, and entry exists in cache."
            )
        print()

        print("processing skills...")
        self.skills = get_skills(self.job_description)
        print("Recognized skills in processing: ", self.skills)
        print()
        self.action_verbs = ActiveVerbRecommender().recommend(
            jd.responsibilities_description
        )

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
