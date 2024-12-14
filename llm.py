from langchain_ollama import ChatOllama
import os
from langchain_core.prompts import ChatPromptTemplate


class Agent:
    def __init__(self, job_description=None):
        self.llm = ChatOllama(model="llama3.2", num_ctx=10000)
        self.base_prompt = """

        """
        self.job_description = job_description

        self.bullet_samples = "samples/bullet-positive-samples.txt"
        self.action_verbs = "samples/action_verbs.txt"

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

        When a bullet point is written, ensure the following criteria:
        - "Fluff" (unnecessary words or phrases), empty, vacuous statements, and vague language are minimized.
        - The bullet point is authentic, engaging, and tailored to the provided job description.
        - Quantify and qualify achievements wherever possible. Use metrics, numbers, results to elaborate on impact.
        - Ensure readability: use action verbs, concise language, and bullet points for easy skimming.
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
