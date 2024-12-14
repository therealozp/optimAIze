from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import sys

system_message = """
You are a professional writing assistant specializing in tailoring cover letters. You will be given an original cover letter as input, and also provided with additional information about the job posting or the company. You will retain the cheerful and passionate tone of the original cover letter. When you rewrite, keep buzzwords and fluff to a minimum and only use them where it is impactful.

You are expected to tailor the cover letter to be as closely related to the job posting and company as possible, and make it truly unique to that company by mentioning some of its initiatives if appropriate. Highlight the necessary skillsets and align the content to the target role, while ensuring the following:

1. Do not distort the truth of the provided information or fabricate details.
2. Preserve the tone and phrasing of the original cover letter as much as possible.
3. Maintain professionalism and a compelling, engaging tone.

Focus on improving clarity, alignment with the job role, and effectiveness while respecting the constraints provided. Only give the cover letter a unique touch by incorporating relevant details about the company or the job posting.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_message,
        ),
        (
            "human",
            "This is my cover letter: {ogcv} Please help me tailor my cover letter for the following job posting: {company_info}",
        ),
    ]
)

llm = ChatOllama(model="llama3.2", num_ctx=10000)
chain = prompt | llm

original_cover_letter = """
Phu Anh Khang Le
Tampa, Florida
anhkhang.le0910@gmail.com
346-252-9698

Dear [Company Name] Hiring Team,

I am excited to apply for the [Job Position] position at [Company Name], as I believe it would be a perfect next step for both my technical skills and my passion for continuous learning. While my resume provides a snapshot of my experience, I would love to share some additional details about what drives me as an engineer and why I think I would be a great fit for your team.

Throughout my journey in computer science, I have been driven by curiosity and a desire to take on meaningful challenges. My recent internship at Kyanon Digital was a turning point, where I got to push the boundaries of AI to solve real-world problems, like improving customer profiling with representation learning. The days and nights were worth it in the end, as I have managed to improve on the existing solution of the company by over 20%! This experience taught me the importance of diving deep into complex problems and the power of innovative thinking to unlock better solutions. 

Beyond my internship, I am involved in a research group at the RANCS Lab, where I am helping to develop an autonomous vehicle. While the technical side of this project has been fascinating-working with everything from sensor fusion to C++ libraries-what excites me most is the collaboration aspect. Because this is such a huge project, I have gotten to work with so many brilliant mechanical engineers that I wouldn't have the chance to interact with otherwise. It has been a lesson in how different skill sets and perspectives come together to solve problems that no one person could tackle alone. This emphasis on teamwork is one of the reasons I am drawn to [Company Name], as I admire the collaborative, cross-functional nature of your projects.

On a personal level, I have always been a bit obsessed with coding challenges. What started as a goal to solve 100 problems quickly snowballed into solving over 400, and I am currently on a 115-day streak. I think this reflects how much I enjoy pushing myself to get better and solve problems efficiently. But beyond the numbers, what I have learned is how to approach problems systematically-breaking them down into manageable parts and looking for creative, optimized solutions.

I am also really passionate about Linux and open-source software. It has been my go-to environment for years, and I am finally at the point where I want to give back by contributing to the projects I have relied on. Learning the internals of systems I have been using has not only deepened my technical understanding but also solidified my appreciation for the open-source community. I hope to bring this mindset of collaboration and contribution to the teams I work with.

In addition to coding and open-source, I have been working on a few side projects to help local businesses improve their digital presence. One of the highlights has been collaborating with An Thai Duong Maritime to enhance their online reach. It has been a rewarding experience to apply my technical skills outside of the classroom and internship settings, directly impacting their customer engagement.

At the heart of all my work is a love for solving problems, learning, and contributing to the bigger picture. I am excited about the possibility of bringing my experience and enthusiasm to your team, and I would love the chance to discuss how I can contribute to the innovative work happening at [Company Name].

Warm regards,
Khang Le
"""

inputlist = sys.stdin.read()
company_information = inputlist


print("\n\nThinking...")
response = chain.invoke(
    {"company_info": company_information, "ogcv": original_cover_letter}
)

print(response.content)
