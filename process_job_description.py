from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from skill_ner import get_skills_from_posting


class JobDescription(BaseModel):
    company_name: str = Field(description="The name of the company.")
    job_title: str = Field(description="The job title.")
    location: str = Field(
        description='The location of the job. Usually the name of a state, a city, or "Remote". '
    )
    company_description: str = Field(
        description="A description of the company. This should contain all information on company such as name, history, work culture."
    )
    responsibilities_description: str = Field(
        description="""
        Description of all possible responsibilities of the applicant.
        
        Look for phrases such as "you will," "your responsibilities," "expected tasks," "As an X, you will work on:" etc. In your response, include"
        - **Technical Responsibilities**: Tasks related to engineering, development, or any technical skills required (e.g., programming, data analysis).
        - **Impact**: What impact the applicant’s work will have (e.g., contributing to projects, improving processes, fine-tuning X, developing backend, scaling systems, etc.).
        """
    )


class HighLevelObjectives(BaseModel):
    high_level_objectives: str = Field(
        description="""High-level objectives of the job. This should contain the overview responsibilities of work involved, such as designing X, building Y for Z, etc.
        """
    )


def extract_all_information(job_description):
    llm = ChatOllama(
        model="llama3.2", num_ctx=4096, temperature=0
    ).with_structured_output(JobDescription)

    parser = PydanticOutputParser(pydantic_object=JobDescription)

    base = """
    You are an expert job information extractor assistant. Your task is to extract all the relevant details about the company, role responsibilities, technical requirements, verbatim from the posting. Look inside "Qualifications" sections for hints of the role responsibilities as well. Evaluate carefully and extract exhaustively."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                base + " Wrap the output in `json` tags\n{format_instructions}",
            ),
            ("human", "{query}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    message = (
        "Extract requested information from posting below:\n"
        + "\n<Job Posting>\n"
        + job_description
        + "</Job Posting>"
    )

    chain = prompt | llm
    raw_response = chain.invoke({"query": message})
    # print(raw_response)
    return raw_response


def extract_high_level_responsibilites(parsed_responsibilities_description):
    llm = ChatOllama(
        model="llama3.2", num_ctx=10000, temperature=0.5
    ).with_structured_output(HighLevelObjectives)

    base = """
    You are an expert job information extractor assistant specializing in summarizing specific responsibilities from a job description. Consider the entire job description as a whole, do not tunnel vision into one section
     
    You are to scan the entire passage of information, and extract all the relevant details. Sometimes, the responsibilities are clearly stated, but sometimes, it is hidden inside the "Requirements" or "Qualifications" section.

    Your task is to extract the specific technical work involved, but NOT programming languages. Generally, the requested data follow the same patterns, such as:
    
    <Examples>
    - Design and develop SDKs to...
    - Build and maintain infrastructure to...
    - Create intuitive UI tools that generate automated insights from telemetry data
    - Create/Update Web basic User Interfaces and back-end code as per the functional needs using the latest technologies such as C#, JavaScript, and Angular
    - Develop tools, libraries, and infrastructure for data preprocessing,
    - Train/finetune machine learning models...
    - Deployment of LLMs in research and production environments
    - Write mission-critical software for autonomous drones
    - AND MORE!
    </Examples>
    """

    prompt = ChatPromptTemplate.from_messages(
        [("system", base), ("human", "The provided job description is: \n{query}")]
    )
    chain = prompt | llm

    message = (
        "Extract requested information from the below job information:\n"
        + "\n<Job Posting>\n"
        + parsed_responsibilities_description
        + "</Job Posting>"
    )
    response = chain.invoke({"query": message})
    return response


class ActiveVerbRecommender:
    def __init__(self):
        self.llm = ChatOllama(model="llama3.2", num_ctx=4096)
        av_file = "samples/action_verbs.txt"
        with open(av_file, "r") as f:
            self.action_verbs = f.readlines()

    def recommend(self, role_information):
        base = """
        You are an assistant specializing in finding which action verbs to use based on the job description. Recommend a list of roughly 20-30 action verbs inside the provided comma-separated list relevant to the job description provided.
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    base + "\n, ".join(self.action_verbs),
                ),
                ("human", "{role_info}"),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke({"role_info": role_information})

        return response.content


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
        self.skills = get_skills_from_posting(self.job_description)
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
