from agent import Agent

with open("samples/sample_job.txt", "r") as f:
    job_posting = f.read()

agent = Agent(job_description=job_posting)
print(
    agent.rewrite_bullet(
        "Created a script using SQL and Python to measure the accuracy of different chatbot models, which was used to evaluate the effectiveness of new updates and inform further build plans."
    )
)
