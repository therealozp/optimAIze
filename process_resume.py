from pydantic import BaseModel, Field
from typing import List, Optional

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from skill_ner import get_skills
from latex_parser import parse_latex_resume
import json


def get_resume_skills(latex_text: str) -> List[str]:
    skills = get_skills(latex_text)
    return skills


def retrieve_absent_skills(resume_skills, job_skills):
    # filter out skills in job_skills that are not in resume_skills
    return [skill for skill in job_skills if skill in resume_skills]


if __name__ == "__main__":
    with open("latex_resume.txt", "r") as f:
        resume_text = f.read()
        print(json.dumps(parse_latex_resume(resume_text)))
        resume_skills = get_resume_skills(resume_text)
        print(resume_skills)

    with open("samples/sample_job.txt", "r") as f:
        job_text = f.read()
        job_skills = get_skills(job_text)
        print(job_skills)

    absent_skills = retrieve_absent_skills(resume_skills, job_skills)
    print(absent_skills)
