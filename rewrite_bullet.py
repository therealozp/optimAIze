from llm import Agent

job_posting = """
Who we are
Snackpass’s mission is to unify the physical and digital world for local commerce.

We power mobile order pickup and social commerce for restaurants, modernizing the customer experience while making restaurant operators successful.

Opportunity

Snackpass is one of the fastest growing marketplaces (a16z top marketplaces), and a top 100 YC company. We are backed by Andreeson Horowitz, Y Combinator, General Catalyst, First Round Capital, Craft Ventures and many others. We are hiring people who are humble and hungry to join us in any of our hubs (NYC, SF, LA) or remotely. 

Our vision is to be the dominant platform for pickup, a $750B market globally.

About the Role

You are a product-driven software engineer excited to:

Ship meaningful features end-to-end.
Be mentored by a close-knit group of amazing engineers.
Experience many aspects of modern product development in a short amount of time.
Bring restaurants into the future with flexible self-serve and marketing.
 

What We Are Looking For:

You are a student pursuing or achieving a BS / MS / PhD in Computer Science or related fields.
High competency with TypeScript and/or Kotlin.
Experience with SQL and/or NoSQL databases.
Strong communication and interpersonal skills.
Past participation in projects outside class work are a strong plus.
Prior experience with our core technologies (NextJS, React Native, Android) is a plus.
 

At Snackpass, You Will:

Build high impact features on a product engineering team.
Work on projects based on your interests ranging from frontend (web and native), backend, full stack and more.
Use our tech stack which includes NextJS, React Native, Kotlin, GraphQL and more.
Help evolve our internal tools and processes as we scale.
"""

agent = Agent(job_description=job_posting)
print("thinking...")
print(
    agent.rewrite_bullet(
        "Led a team of 5 engineers to develop a new feature for a mobile app"
    )
)
print("done")
