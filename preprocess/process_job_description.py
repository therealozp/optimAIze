from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from typing import List
from langchain_core.output_parsers import PydanticOutputParser


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
        
        **LOOK EVERYWHERE THAT CONTAIN** phrases such as "you will," "your responsibilities," "expected tasks," "As an X, you will work on:" etc. Your response should include:
        - **Technical Responsibilities**: Tasks related to engineering, development, or any technical skills required (e.g., programming, data analysis).
        - **Impact**: What impact the applicant’s work will have (e.g., contributing to projects, improving processes, fine-tuning X, developing backend, scaling systems, etc.).
        Be very exhaustive in your extraction. Extract all required information and you get a 1000 points bonus on top.
        """
    )


class HighLevelObjectives(BaseModel):
    high_level_objectives: str = Field(
        description="""High-level objectives of the job. This should contain the overview responsibilities of work involved, such as "designing X", "building Y for Z", etc.
        """
    )


def extract_all_information(job_description):
    llm = ChatOllama(
        model="llama3.2", num_ctx=4096, temperature=0
    ).with_structured_output(JobDescription)

    parser = PydanticOutputParser(pydantic_object=JobDescription)

    base = """
    You are an expert job information extractor assistant. Your task is to extract all the relevant details about the company, role responsibilities, technical requirements, verbatim from the posting. 

    You are to scan the entire passage of information, and extract all the relevant details. Sometimes, the responsibilities are clearly stated, but sometimes, it is hidden inside the "Requirements" or "Qualifications" section. For example, if the job description mentions "Have experience with training LLMs in research and production environments," you should extract "training LLMs in research and production environments" as a responsibility.

    **LOOK EVERYWHERE THAT CONTAIN** phrases such as "you will," "your responsibilities," "expected tasks," "As an X, you will work on:" etc. Your response should include:
        - **Technical Responsibilities**: Tasks related to engineering, development, or any technical skills required (e.g., programming, data analysis).
        - **Impact**: What impact the applicant’s work will have (e.g., contributing to projects, improving processes, fine-tuning X, developing backend, scaling systems, etc.).
        Be very exhaustive in your extraction. Extract all required information and you get a 1000 points bonus on top of your existing 100 point reward.

    Extract exhaustively."""

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
        model="llama3.2", num_ctx=10000, temperature=0.2
    ).with_structured_output(HighLevelObjectives)

    base = """
    You are an expert job information extractor assistant specializing in summarizing specific responsibilities from a job description. Consider the entire job description as a whole, do not tunnel vision into one section
     
    You are to scan the entire passage of information, and extract all the relevant details. Sometimes, the responsibilities are clearly stated, but sometimes, it is hidden inside the "Requirements" or "Qualifications" section. For example, if the job description mentions "Have experience with training LLMs in research and production environments," you should extract "training LLMs in research and production environments" as a responsibility.

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


class ListOfKeywords(BaseModel):
    keywords: str = Field(
        description="a comma-separated list of active verbs recommended based on the job description. It should be highly relevant."
    )


class ActiveVerbRecommender:
    def __init__(self):
        self.llm = ChatOllama(model="llama3.2", num_ctx=4096).with_structured_output(
            ListOfKeywords
        )
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

        return response
