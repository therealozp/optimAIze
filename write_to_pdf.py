from fpdf import FPDF


def write_cv(text, company_name="Company Name", job_position="Job Position"):
    # Create a PDF instance
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_font("Garamond", "", "Garamond.ttf", uni=True)

    # Add a page
    pdf.add_page()

    # Set 1 inch (25.4mm) margins (A4 size is 210mm x 297mm)
    margin_size = 25.4  # 1 inch in millimeters

    # Set the left, right,
    pdf.set_left_margin(margin_size)
    pdf.set_right_margin(margin_size)
    pdf.set_top_margin(margin_size)

    # Move the cursor to the start of the printable area
    pdf.set_auto_page_break(auto=True, margin=margin_size)

    # Set the font (using a default font like Arial)
    pdf.set_font("Garamond", size=11)

    # Add some text
    pdf.multi_cell(
        0,
        5,
        txt=text,
        align="L",
    )

    # Save the generated PDF
    pdf.output(f"Phu Anh Khang Le_CoverLetter_{company_name}_{job_position}.pdf")
    with open(
        f"Phu Anh Khang Le_CoverLetter_{company_name}_{job_position}.txt", "w"
    ) as f:
        f.write(text)


text = """
Phu Anh Khang Le
Tampa, Florida
anhkhang.le0910@gmail.com
346-252-9698

Dear [Company Name] Hiring Team,

I am excited to apply for the Software Engineering Intern position at Dyno Therapeutics. As an aspiring software engineer with a strong foundation in AI and machine learning, I am drawn to Dyno’s mission to transform gene therapy through cutting-edge technologies. Your work at the intersection of AI and gene delivery is a perfect match for both my technical interests and my desire to work on projects that have a tangible, life-changing impact.

Throughout my journey in computer science, I have been driven by curiosity and a desire to take on meaningful challenges. My recent internship at Kyanon Digital was a turning point, where I got to push the boundaries of AI to solve real-world problems, like improving customer profiling with representation learning. The days and nights were worth it in the end, as I have managed to improve on the existing solution of the company by over 20%! This experience taught me the importance of diving deep into complex problems and the power of innovative thinking to unlock better solutions. 

Beyond my internship, I am involved in a research group at the RANCS Lab, where I am helping to develop an autonomous vehicle. While the technical side of this project has been fascinating-working with everything from sensor fusion to C++ libraries-what excites me most is the collaboration aspect. Because this is such a huge project, I have gotten to work with so many brilliant mechanical engineers that I wouldn't have the chance to interact with otherwise. It has been a lesson in how different skill sets and perspectives come together to solve problems that no one person could tackle alone. This emphasis on teamwork is one of the reasons I am drawn to [Company Name], as I admire the collaborative, cross-functional nature of your projects.

On a personal level, I have always been a bit obsessed with coding challenges. What started as a goal to solve 100 problems quickly snowballed into solving over 400, and I am currently on a 115-day streak. I think this reflects how much I enjoy pushing myself to get better and solve problems efficiently. But beyond the numbers, what I have learned is how to approach problems systematically-breaking them down into manageable parts and looking for creative, optimized solutions.

In addition to my experience, I am deeply passionate about building new technologies. Recently, I’ve been exploring the use of large language models (LLMs) and developing applications that leverage these models to solve specific problems. I am excited about the opportunity to bring this knowledge to Dyno, particularly in the context of optimizing gene delivery systems. I am confident that my skills in Python, AI frameworks like HuggingFace, and my experience in full-stack development will allow me to contribute meaningfully to your team and actually make an impact on the world.

At the heart of all my work is a love for solving problems, learning, and contributing to the bigger picture. I am excited about the possibility of bringing my experience and enthusiasm to your team, and I would love the chance to discuss how I can contribute to the innovative work happening at [Company Name].

Warm regards,
Khang Le
"""

text = text.replace("[Company Name]", "Dyno Therapeutics")

write_cv(text)
