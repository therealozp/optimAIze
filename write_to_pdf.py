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

Dear CrowdStrike University Program Hiring Team,

I am thrilled to apply for the Frontend Engineer Intern role at CrowdStrike, where I can leverage my passion for building user-centered interfaces and tackling complex problems with innovative solutions. As a computer science student with a strong foundation in JavaScript and web development, I am confident that my skills align perfectly with your team's needs.

Throughout my academic journey, I have been driven by curiosity and a desire to push the boundaries of what is possible on the web platform. My recent internship at Kyanon Digital taught me the importance of diving deep into complex problems and the power of innovative thinking to unlock better solutions. I successfully improved an existing AI solution by over 20%, demonstrating my ability to tackle meaningful challenges and deliver results-driven solutions.

Beyond my internship, I have been actively involved in a research group at the RANCS Lab, where I am contributing to the development of an autonomous vehicle project. While working on this complex problem, I have learned the value of collaboration and teamwork in overcoming technical hurdles. This experience has solidified my passion for building strong relationships with colleagues and delivering high-quality software that meets user needs.

As a self-proclaimed coding enthusiast, I enjoy tackling personal projects and contributing to open-source initiatives. I am particularly drawn to Linux and open-source software due to their emphasis on collaboration, transparency, and continuous learning. My experience working on side projects for local businesses has not only deepened my technical skills but also given me a deeper appreciation for the importance of user-centered design.

I am impressed by CrowdStrike's commitment to innovation and making the digital world a safer place to live and work. As someone who is passionate about solving problems and learning, I am excited about the opportunity to join your team and contribute to the development of cutting-edge cybersecurity solutions. Your emphasis on collaboration, flexibility, and personal growth aligns perfectly with my values and approach to software development.

In addition to my technical skills and passion for coding, I possess excellent communication and problem-solving skills, which have been essential in my academic and professional journey. I am confident that my unique blend of technical expertise, enthusiasm for learning, and collaborative spirit make me an ideal candidate for this role.

I would be thrilled to discuss how my skills and experience align with CrowdStrike's mission and values. Thank you for considering my application!

Warm regards,
Khang Le
"""

write_cv(text)