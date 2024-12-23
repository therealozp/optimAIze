from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class ResumeBullet(BaseModel):
    """
    Represents a resume bullet point. Should always follow the following criteria:
    - The bullet point is authentic, engaging, and tailored to the provided job description.
    - Be straightforward. Own the bullet point.
    - No generic or cliche statements.
    - The "technical how" should be concise. Should not cause any run-on sentences/bullet points.
    - Quantify and qualify achievements wherever possible, using metrics, numbers, and tangible results.
    - Ensure readability. Use action verbs and concise language.
    """

    rewritten_bullet: str = Field(
        description="The rewritten bullet point that has been optimized for impact, clarity, and relevance."
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


def generate_improvement_plan(bullet, entry):
    """
    Generate an improvement plan for the bullet point. Takes the bullet, and the entry for context
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
                - Be straightforward. Own the bullet point.
                - No generic or cliche statements.
                - The "technical how" should be concise. Should not cause any run-on sentences/bullet points.
                - Quantify and qualify achievements wherever possible, using metrics, numbers, and tangible results.
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
        self.chat_history = [
            (
                "system",
                """You are an assistant specializing in optimizing resume bullet points for maximum impact and technical clarity. Consider the fit of the bullet point to the job description. Does it exhibit the core competencies demanded by the nature of the job? IGNORE SOFT SKILLS. DO NOT COPY FROM JOB DESCRIPTION.

Guidelines to writing a good bullet point:
- The bullet point and tailored to the provided job description.
- The "technical how" should be concise, not extremely verbose.
- Quantify and qualify achievements wherever possible, using metrics, numbers, and tangible results.
- No generic or cliche statements.
- Be straightforward. Own the bullet point.
- Ensure readability. Use action verbs and concise language.
                """,
            )
        ]

    def rewrite_bullet(self, entry, bullet):
        """
        Rewrite the bullet point based on the evaluation and improvement plan.
        """
        resp = None
        if "responsibilities" in entry:
            resp = entry["responsibilities"]
        else:
            resp = entry["details"]

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

        rewriting_prompt = """
        Q: Built a custom pipeline for real-time data processing, using Kafka and Spark, which made the data ingestion faster.
        A: Developed a custom data pipeline for real-time data processing with Kafka and Spark, enabling 10x faster data ingestion and processing.

        Q: Improved the algorithm used to select stocks by making it more efficient and boosting performance.
        A: Improved performance of stock selection algorithm based on CAPM by introducing mixed integer programming, increasing Sharpe ratio by 6% and reducing drawdown by 5%.

        Q: Created a backtesting tool for Treasury bond strategies, implementing it in Python.
        A: Wrote fully functional backtesting program with Python to implement statistical arbitrage strategies of Treasury bond futures based on residual deviation signal.

        Q: Applied moving averages and Kalman filters to strategy parameters to improve outcomes.
        A: Used moving average and Kalman filter to better fit time-varying strategy parameters, which significantly improved strategy performance in most cases.

        Q: Changed the program structure to use numpy arrays and vectorization, making it run much faster.
        A: Optimized program by restricting data structure to pure numpy array and using vectorization heavily; improved average running speed of backtesting program 22-fold

        Q: Designed a Kafka-based system for streaming reports, reducing costs slightly.
        A: Architected and deployed a Kafka-driven pipeline to stream finance reports, achieving a 15% reduction in costs.

        Q: Rewrite the bullet point below to better tailor it to the job description:
        <BULLET TO REWRITE>
        {bullet}
        </BULLET TO REWRITE>
        
        <JOB DESCRIPTION>
        {job_description}
        </JOB DESCRIPTION>
        
        A: 
        """

        prompt = ChatPromptTemplate.from_messages(
            self.chat_history + [("human", rewriting_prompt)]
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "bullet": bullet,
                "job_description": self.job_description,
            }
        )

        if not response or not response.rewritten_bullet:
            raise Exception("Model did not produce any output.")
        return True, response.rewritten_bullet
