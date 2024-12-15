from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    company_name: str = Field(description="The name of the company.")
    job_title: str = Field(description="The job title.")
    location: str = Field(
        description='The location of the job. Usually the name of a state, a city, or "Remote". '
    )
    company_description: str = Field(
        description="A description of the company. This should contain all information on company such as name, history, work culture, projects, etc."
    )
    responsibilities_description: str = Field(
        description="""Description of all possible responsibilities of the applicant.
        
         Look for phrases such as "you will," "your responsibilities," "expected tasks," "As an X, you will work on:" etc. In your response, include"
        - **Technical Responsibilities**: Tasks related to engineering, development, or any technical skills required (e.g., programming, data analysis).
        - **Impact**: What impact the applicant’s work will have (e.g., contributing to projects, improving processes, fine-tuning X, developing backend, scaling systems, etc.).
        """
    )


class JobKeywordExtractor:
    def __init__(self, job_description=None):
        self.llm = ChatOllama(
            model="llama3.2", num_ctx=10000, temperature=0
        ).with_structured_output(JobDescription)

        self.job_description = job_description

    def extract_all_information(self):
        base = """
        You are an expert job information extractor assistant. Your task is to extract all the relevant details about the company, role responsibilities, technical requirements, and excitement from the job posting. Extract it exhaustively.

        Given the below job posting, exhaustively extract all the relevant information.
            """
        message = base + "\n<Job Posting>\n" + self.job_description + "</Job Posting>"

        response = self.llm.invoke(message)
        return response


class Agent:
    def __init__(self, job_description=None):
        self.llm = ChatOllama(model="llama3.2", num_ctx=10000)
        self.job_description = job_description

        self.bullet_samples = "samples/bullet-positive-samples.txt"
        self.action_verbs = "samples/action_verbs.txt"

    def recommend_active_verbs(self):
        prompt = """
        You are an assistant specializing in finding which action verbs to use based on the job description. Recommend a list of roughly 30-50 action verbs relevant to the job description provided.
    """

    def give_bullet_samples(self):
        with open(self.bullet_samples, "r") as f:
            return f.readlines()

    def give_action_verbs(self):
        with open(self.action_verbs, "r") as f:
            return f.readlines()

    def rewrite_bullet(self, bullet):
        base = """
        You are an assistant specializing in optimizing resume bullet points for maximum impact and technical clarity. For each bullet point provided, iterate through these steps:

        1. Evaluate the bullet point for impact, clarity, and relevance.
        2. Enumerate improvements you plan to make to the bullet point.
        3. Deliver the final rewritten bullet point

        When a bullet point is rewritten, ensure the following criteria:
        - No unnecessarily wordy statements.
        - No statements that are generic and cliche.
        - Everything should be clear. No vague and generic language.
        - Quantify and qualify achievements wherever possible. 
        - Use metrics, numbers, results to elaborate on impact.
        - The bullet point is authentic, engaging, and tailored to the provided job description.
        - Ensure readability. Use action verbs and concise language.
        """
        history = [
            (
                "system",
                base,
            ),
        ]

        ## rewrite in three stages:
        # give the model the original bullet point for first path
        first_iter = "Please help me rewrite the following bullet point: " + bullet
        history.append(("human", first_iter))
        prompt = ChatPromptTemplate.from_messages(history)
        chain = prompt | self.llm
        response = chain.invoke({})

        print(first_iter)
        print(response.content)

        # save response
        history.append(("assistant", response.content))

        # give model action verbs to improve on second path
        second_iter = """
        Here are some action verbs to consider while rewriting the bullet point. Can you improve the bullet point with any of these?"""
        for av in self.give_action_verbs():
            second_iter += f"- {av}\n"
        history.append(("system", second_iter))
        prompt = ChatPromptTemplate.from_messages(history)
        chain = prompt | self.llm
        response = chain.invoke({})

        print(
            "Here are some action verbs. Can you improve the bullet point with any of these?"
        )
        print(response.content)

        # save response
        history.append(("assistant", response.content))

        # give model some sample bullet points to rewrite on third path
        third_iter = "Here are some sample bullet points to help you rewrite the original bullet point: "
        for sample in self.give_bullet_samples():
            third_iter += f"- {sample}\n"

        history.append(("system", third_iter))
        prompt = ChatPromptTemplate.from_messages(history)
        chain = prompt | self.llm
        response = chain.invoke({})

        print(
            "Here are some sample bullet points to help you rewrite the original bullet point:"
        )
        print(response.content)

        # save response
        history.append(("assistant", response.content))

        # last path to enforce requirements
        last_iter = 'Please rewrite the bullet point "{bullet}" with the feedback provided. Note the following requirements: '
        last_iter += """
        - "Fluff", empty, vacuous statements, and vague language are minimized.
        - The bullet point is authentic, engaging.
        - Quantify and qualify achievements wherever possible. Use metrics, numbers, results to elaborate on impact.
        - Skills and achievements should be tailored to the job.
        """

        history.append(("human", last_iter))
        prompt = ChatPromptTemplate.from_messages(history)
        chain = prompt | self.llm
        response = chain.invoke({"bullet": bullet})

        return response.content
