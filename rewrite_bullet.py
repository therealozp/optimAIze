from llm import (
    Agent,
    extract_all_information,
    extract_high_level_responsibilites,
    ActiveVerbRecommender,
)

job_posting = """
NVIDIA pioneered accelerated computing to tackle challenges no one else can solve. Our work in AI and digital twins is transforming the world's largest industries and profoundly impacting society — from gaming to robotics, self-driving cars to life-saving healthcare, climate change to virtual worlds where we can all connect and create. 

 

Our internships offer an excellent opportunity to expand your career and get hands on with one of our industry leading Software teams. We’re seeking strategic, ambitious, hard-working, and creative individuals who are passionate about helping us tackle challenges no one else can solve. 

 

Throughout the minimum 12-week internship, students will work on projects that have a measurable impact on our business. We’re looking for students pursuing Bachelor's, Master's, or PhD degree within a relevant or related field. 

 

Potential Internships in this field include:  

Development Tools 

Debugging complex system-level issues using Jenkins  

Course or internship experience related to the following areas could be required: Relational Databases, Linear Algebra & Numerical Methods, Operating Systems (memory/resource management), Scheduling and Process Control, Hardware Virtualization 

Cloud 

Supporting overall architecture and design of our cloud storage infrastructure  

Implementing and troubleshooting storage and data platform tools, automating storage infrastructure end-to-end 

Course or internship experience related to the following areas could be required: Distributed Systems, Data Structures & Algorithms, Virtualization, Automation/Scripting, Container & Cluster Management, Debugging 

Tools Infrastructure 

Building industry leading technology by proving workflows and infrastructure, alongside a team of experts in production software development and chip design methodologies 

Enabling success for content running on the chip from application tracing and analysis to modeling, diagnostics, performance tuning, and debugging  

Course or internship experience related to the following areas and technologies could be required: Unix/Shell Scripting, Linux, Java, JavaScript (including Node, React, Vue), C++, CUDA, OOP, Go, Python, Git, GitLab, Perforce, Kubernetes and Microservices, Schedulers (LSF, SLURM), Containers (Docker), Configuration Automation (Ansible) 

Data Science 

Supporting cloud and on-premise infrastructure for backend analytics  

Working on diverse data technologies including, Kafka, ELK, Cassandra, and Spark 

Course or internship experience related to the following areas could be required: Data Science, Data Engineering, Open Source Data Science Tools, Open Source Libraries 

What we need to see:  

Currently pursuing a Bachelor's, Master's, or PhD degree within Computer Engineering, Electrical Engineering, Computer Science, or a related field 

Depending on the internship role, prior experience or knowledge requirements could include the following programming skills and technologies: Java, JavaScript, (including Node, React, Vue), SQL, C++, CUDA, OOP, Go, Python, Git, Perforce, Kubernetes and Microservices, Schedulers (LSF, SLURM), Containers (Docker), Configuration Automation (Ansible)  
"""

job_description = extract_all_information(job_posting)

print(job_description.responsibilities_description)
hlr = extract_high_level_responsibilites(job_description.responsibilities_description)
avr = ActiveVerbRecommender()
print(avr.recommend(hlr))
