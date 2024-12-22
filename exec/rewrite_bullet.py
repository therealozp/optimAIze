from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class ResumeBullet(BaseModel):
    """
    Represents a resume bullet point. Should always follow the following criteria:
    - Be straightforward. Own the bullet point. No unnecessarily wordy statements.
    - Quantify and qualify achievements wherever possible. Use metrics, numbers, results to elaborate on impact.
    - Ensure readability. Use action verbs and concise language.
    - The bullet point is authentic, engaging, and tailored to the provided job description.
    - No statements that are cliche or overly generic.
    """

    rewritten_bullet: str = Field(
        description="The rewritten bullet point that has been optimized for impact, clarity, and relevance to the specific job description."
    )


class NeedsRewrite(BaseModel):
    """
    This class represents a model response on whether a bullet point needs rewriting or not. A bullet point will need rewriting if it can be improved for relevance to the job description, or does not meet the criteria for a good bullet point. If the bullet point is already good, it does not need rewriting.
    """

    needs_rewrite: bool = Field(
        description="A boolean value indicating whether the bullet point requires rewriting. Ignore Markdown syntax if there is some."
    )


def check_needs_rewrite(bullet, job_description, current_bullets):
    """
    Check if the bullet point needs rewriting.
    """
    llm = ChatOllama(
        model="llama3.2", num_ctx=4096, temperature=0.2
    ).with_structured_output(NeedsRewrite)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an evaluator for resume bullet points."),
            (
                "human",
                """
                Does the following bullet point need rewriting? Consider the job description and current bullet points for context. Ensure there are no redundancies.
                
                <JOB DESCRIPTION>
                {job_description}
                </JOB DESCRIPTION>
                
                <CURRENT BULLETS>
                {current_bullets}
                </CURRENT BULLETS>
                
                <BULLET TO EVALUATE>
                {bullet}
                </BULLET TO EVALUATE>
                """,
            ),
        ]
    )
    chain = prompt | llm
    response = chain.invoke(
        {
            "bullet": bullet,
            "job_description": job_description,
            "current_bullets": current_bullets,
        }
    )
    return response.needs_rewrite


class ImprovementPlan(BaseModel):
    """
    Represents the improvement plan for a resume bullet point. A good bullet point should:
    - Be straightforward. Own the bullet point. No unnecessarily wordy statements.
    - No statements that are generic and cliche.
    - Everything should be clear. No vague and generic language.
    - Quantify and qualify achievements wherever possible.
    - Use metrics, numbers, results to elaborate on impact.
    - The bullet point is authentic, engaging, and tailored to the provided job description.
    - Ensure readability. Use action verbs and concise language.
    """

    improvements: str = Field(
        description="A list of improvements that can be made to the bullet point. Be very specific in devising your improvement plan"
    )


def generate_improvement_plan(bullet):
    """
    Generate an improvement plan for the bullet point.
    """
    llm = ChatOllama(
        model="llama3.2", num_ctx=4096, temperature=0.2
    ).with_structured_output(ImprovementPlan)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an assistant providing improvement plans for resume bullet points."
                "a good bullet point should have the following criteria:"
                """
                - Be straightforward. Own the bullet point. No unnecessarily wordy statements.
                - No statements that are generic and cliche.
                - Everything should be clear. No vague and generic language.
                - Quantify and qualify achievements wherever possible. 
                - Use metrics, numbers, results to elaborate on impact.
                - The bullet point is authentic, engaging, and tailored to the provided job description.
                - Ensure readability. Use action verbs and concise language.
                """,
            ),
            (
                "human",
                "Provide an improvement plan for the following bullet point: {bullet}\n\n"
                "Here are some example bullet points for reference:\n{bullet_samples}",
            ),
        ]
    )
    chain = prompt | llm
    response = chain.invoke({"bullet": bullet, "bullet_samples": load_bullet_samples()})
    return response


def load_bullet_samples(bullet_samples_path="samples/bullet-positive-samples.txt"):
    """
    Load "good" bullet samples from a text file.
    """
    with open(bullet_samples_path, "r") as file:
        bullet_samples = file.read()
    return bullet_samples


class ResumeRewriter:
    def __init__(self, job_description=None):
        self.llm = ChatOllama(
            model="llama3.2", num_ctx=8192, temperature=0.2
        ).with_structured_output(ResumeBullet)
        self.job_description = job_description
        self.bullet_samples = load_bullet_samples()

    def rewrite_bullet(self, entry, bullet):
        """
        Rewrite the bullet point based on the evaluation and improvement plan.
        """
        resp = None
        if "responsibilities" in entry:
            resp = entry["responsibilities"]
        else:
            resp = entry["details"]

        posn = None
        if "position_name" in entry:
            posn = entry["position_name"]
        else:
            posn = entry["project_name"]

        if check_needs_rewrite(bullet, self.job_description, resp):
            return self.rewrite_no_check(entry, bullet)
        else:
            return False, bullet  # No changes needed

    def rewrite_no_check(self, entry, bullet):
        resp = None
        if "responsibilities" in entry:
            resp = entry["responsibilities"]
        else:
            resp = entry["details"]

        posn = None
        if "position_name" in entry:
            posn = entry["position_name"]
        else:
            posn = entry["project_name"]

        improvement_plan = generate_improvement_plan(bullet)
        rewriting_prompt = """
        Rewrite the bullet point below, incorporating the following improvements:

        <IMPROVEMENT PLAN>
        {improvement_plan}
        </IMPROVEMENT PLAN>

        <BULLET TO REWRITE>
        {bullet}
        </BULLET TO REWRITE>
        
        <JOB DESCRIPTION>
        {job_description}
        </JOB DESCRIPTION>

        Resume entry for context. For reference, if other bullets have contained important information, DO NOT include them in your rewrite. There should be 0 redundancies.
        Position: {position_name}
        Responsibilities:
        {responsibilities}

        Reference good bullet samples that fulfill these criteria:
        {bullet_samples}
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an assistant specializing in optimizing resume bullet points for maximum impact and technical clarity. For each bullet point provided, iterate through these steps:

                    1. Evaluate the bullet point for impact, clarity, and relevance.
                    2. Enumerate improvements you plan to make to the bullet point.
                    3. Deliver the final rewritten bullet point

                    When a bullet point is rewritten, ensure the following criteria:
                    - Be straightforward. Own the bullet point. No unnecessarily wordy statements.
                    - No statements that are generic and cliche.
                    - Everything should be clear. No vague or generic language.
                    - Quantify and qualify achievements wherever possible. 
                    - Use metrics, numbers, results to elaborate on impact.
                    - The bullet point is authentic, engaging, and tailored to the provided job description.
                    - Ensure readability. Use action verbs and concise language.
                    """,
                ),
                ("human", rewriting_prompt),
            ]
        )

        chain = prompt | self.llm
        print(bullet)
        print(improvement_plan.improvements)
        print(self.job_description)
        print(posn)
        print(";".join(resp))

        response = chain.invoke(
            {
                "bullet": bullet,
                "improvement_plan": improvement_plan.improvements,
                "job_description": self.job_description,
                "bullet_samples": self.bullet_samples,
                "position_name": posn,
                "responsibilities": ";".join(resp),
            }
        )

        return True, response
