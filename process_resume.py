from pydantic import BaseModel, Field
from typing import List, Optional

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from latex_parser import parse_latex_resume
from skill_ner import get_skills
