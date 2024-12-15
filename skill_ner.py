import spacy
from spacy.tokens import Span
import re
from spacy.language import Language


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


@Language.component("skill_entity_component")
def skill_entity_component(doc):
    vocabulary = load_initial_skill_list("baseline_taxonomies/skills.txt")
    filter = DynamicSkillFilter(vocabulary)
    all_variants = [
        variant
        for variants in filter.normalized_skills.values()
        for variant in variants
    ]
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


def load_initial_skill_list(filename="skills.txt"):
    with open(filename, "r") as f:
        skills = f.read().splitlines()
    return skills


def filter_skills(job_posting):
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("skill_entity_component", name="skill_ner", last=True)

    doc = nlp(job_posting)
    for ent in doc.ents:
        print(ent.text, ent.label_)

    return [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
