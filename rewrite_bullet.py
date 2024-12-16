from process_job_description import (
    Agent,
    extract_all_information,
    extract_high_level_responsibilites,
    ActiveVerbRecommender,
)

job_posting = """
Intel put the Silicon in Silicon Valley. No one else is this obsessed with engineering a brighter future. Every day, we create world changing technology that enriches the lives of every person on earth. So, if you have a big idea, let’s do something wonderful together. Join us, because at Intel, we are building a better tomorrow. Want to learn more? Visit our YouTube Channel or the links below!

Life at Intel
Diversity at Intel
Reporting to the Manager of Software Engineering is responsible for wearing multiple hats from viewing the architectural approach with a critical eye, making implementation decisions, and proactively communicating this with the team.

Designs, implements, and maintains tools and processes for the continuous integration, delivery, and deployment of software. Will work with developers, testers, and system administrators to ensure the entire software development life cycle is efficient, smooth, and error-free.

The successful candidate will possess the following attributes:

Leadership
Problem Solving
Decision Making
Communication
Multi-tasking
Critical Thinking skills
This is a full-time, Hybrid,  3-month internship, targeting a start date of early 2025.  Intern must be able to be on-site in Santa Clara CA, Folsom CA, or Phoenix AZ.  

#DesignEnablement

Qualifications:
What we need to see (Minimum Qualifications):

Must be pursuing a Bachelors degree in computer science or related STEM technical field.
3+ months experience developing tools, libraries, and infrastructure for data preprocessing, model training/finetuning, and deployment of LLMs.


Preferred Qualifications:

1+ years experience developing tools, libraries, and infrastructure for data preprocessing, model training/finetuning, and deployment of LLMs in research and production environments.
Technology stack: Exposure to one or more of these is preferred:

Cloud Platforms: AWS, Azure, GCP
Programming Languages: Python, Node.js, Go, Ruby
APIs and Integration: OpenAPI, FastAPI, Swagger, Flask, REST
Databases: PostgreSQL, MySQL, MongoDB, Redis
ML Frameworks: PyTorch, Scikit-learn, Keras
Development and Deployment: Jenkins, Docker, Kubernetes
Monitoring and Logging: Prometheus, Grafana, ELK Stack.
Version Control: Git, GitHub, GitLab
Architecture Design and Modeling: Microsoft Visio, Drawio.
Collaboration and Project Management: JIRA, Confluence, Trello
"""

agent = Agent(job_description=job_posting)
print(
    agent.rewrite_bullet(
        "Created a script using SQL and Python to measure the accuracy of different chatbot models, which was used to evaluate the effectiveness of new updates and inform further build plans."
    )
)
