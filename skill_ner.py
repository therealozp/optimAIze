import spacy
from spacy.tokens import Span
import re
from spacy.language import Language


def load_initial_skill_list(filename="skills.txt"):
    with open(filename, "r") as f:
        skills = f.read().splitlines()
    return skills


vocabulary = load_initial_skill_list("baseline_taxonomies/skills.txt")


# Your DynamicSkillFilter class to normalize the skills
class DynamicSkillFilter:
    def __init__(self, skill_list):
        self.raw_skills = skill_list
        self.normalized_skills = self._normalize_skills(skill_list)

    def _normalize_skills(self, skill_list):
        """
        Generates normalized versions of skills for fuzzy matching.
        """
        normalized = {}
        for skill in skill_list:
            # Remove anything in parentheses and normalize spaces/case
            clean_skill = re.sub(r"\(.*?\)", "", skill).strip().lower()
            variations = {
                clean_skill,
                clean_skill.replace(" ", ""),
                clean_skill.replace("-", ""),
                clean_skill.replace(".", ""),
            }
            if " " in clean_skill:
                words = clean_skill.split()
                variations.add("".join(words))
                variations.add(" ".join(words))
                if len(words) > 2:
                    variations.add("".join([word[0] for word in words]))
            normalized[skill] = list(variations)
        return normalized


# Instantiate the DynamicSkillFilter
filter = DynamicSkillFilter(vocabulary)

# Create a list of all skill variants (normalized and original)
all_variants = [
    variant for variants in filter.normalized_skills.values() for variant in variants
]


@Language.component("skill_entity_component")
def skill_entity_component(doc):
    entities = []
    for token in doc:
        # Check if the token matches any of the skill variants
        if token.text.lower() in all_variants:
            start = token.i
            end = token.i + 1
            span = Span(doc, start, end, label="SKILL")
            entities.append(span)

    # Add detected entities to the document
    doc.ents = entities
    return doc


@Language.component("company_entity_component")
def company_entity_component(doc):
    entities = []
    for token in doc:
        # Check if the token matches any of the skill variants
        if token.text.lower() in all_variants:
            start = token.i
            end = token.i + 1
            span = Span(doc, start, end, label="ORG")
            entities.append(span)

    # Add detected entities to the document
    doc.ents = entities
    return doc


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("company_entity_component", name="company_ner")
nlp.add_pipe("skill_entity_component", name="skill_ner", last=True)

text = """
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

doc = nlp(text)
for ent in doc.ents:
    print(ent.text, ent.label_)
