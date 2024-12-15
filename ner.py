import spacy
from spacy.tokens import DocBin
from spacy.matcher import PhraseMatcher
from spacy.language import Language
from rapidfuzz import process
import re

from skill_ner import nlp


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
            }
            if " " in clean_skill:
                words = clean_skill.split()
                variations.add("".join(words))
                variations.add(" ".join(words))
                variations.add("".join([word[0] for word in words]))
            normalized[skill] = list(variations)
        return normalized

    def match_skill(self, term):
        term = term.lower()
        best_match, score = None, 0
        for skill, variations in self.normalized_skills.items():
            match, fuzz_score = process.extractOne(term, variations)
            if fuzz_score > score:
                best_match, score = skill, fuzz_score
        return best_match if score > 80 else None

    def update_skills(self, new_skills):
        self.raw_skills.extend(new_skills)
        self.normalized_skills.update(self._normalize_skills(new_skills))


class SkillNERPipeline:
    def __init__(self, skill_filter, base_model="en_core_web_sm"):
        self.skill_filter = skill_filter
        self.nlp = spacy.load(base_model)  # Load spaCy model
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Add skills to the matcher
        for skill_variations in skill_filter.normalized_skills.values():
            print(skill_variations)
            patterns = [self.nlp.make_doc(variation) for variation in skill_variations]
            self.matcher.add("SKILL", patterns)

        # Add matcher as a custom component
        @Language.component("skill_matcher")
        def skill_matcher(doc):
            matches = self.matcher(doc)
            spans = [doc[start:end] for match_id, start, end in matches]
            doc.ents = list(doc.ents) + spans
            return doc

        # Insert matcher into the spaCy pipeline
        self.nlp.add_pipe("skill_matcher", last=True)

    def process_job_description(self, job_description):
        job_description = job_description.lower()  # Lowercase the input text
        doc = self.nlp(job_description)
        extracted_skills = set()
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                normalized_skill = self.skill_filter.match_skill(ent.text)
                if normalized_skill:
                    extracted_skills.add(normalized_skill)
        return list(extracted_skills)

    def train_ner(self, annotations):
        doc_bin = DocBin()
        for text, entities in annotations:
            doc = self.nlp.make_doc(text)
            spans = [
                doc.char_span(start, end, label=label) for start, end, label in entities
            ]
            spans = [span for span in spans if span is not None]
            doc.ents = spans
            doc_bin.add(doc)
        return doc_bin

    def save_model(self, output_path):
        self.nlp.to_disk(output_path)

    def load_model(self, model_path):
        self.nlp = spacy.load(model_path)
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")  # Recreate matcher
        for skill_variations in self.skill_filter.normalized_skills.values():
            patterns = [self.nlp.make_doc(variation) for variation in skill_variations]
            self.matcher.add("SKILL", patterns)


def load_initial_skill_list(filename="skills.txt"):
    with open(filename, "r") as f:
        skills = f.read().splitlines()
    return skills


# Example usage
if __name__ == "__main__":
    # Load initial skills list
    skills = load_initial_skill_list("baseline_taxonomies/skills.txt")
    # print(skills)

    skill_filter = DynamicSkillFilter(skills)
    ner_pipeline = SkillNERPipeline(skill_filter, base_model="en_core_web_sm")

    # Example job description
    job_description = "We are looking for a software engineer skilled in Python, ReactJS, and IoT applications."
    extracted_skills = ner_pipeline.process_job_description(job_description)
    print("Extracted Skills:", extracted_skills)

    # # Add new skills dynamically
    # skill_filter.update_skills(["Natural Language Processing", "Data Science"])
    # updated_skills = ner_pipeline.process_job_description(
    #     "Looking for expertise in NLP and Data Science."
    # )
    # print("Updated Extracted Skills:", updated_skills)

    # # Save the updated model
    # ner_pipeline.save_model("path/to/skill_ner_model")

    # # Load the model later
    # new_pipeline = SkillNERPipeline(skill_filter)
    # new_pipeline.load_model("path/to/skill_ner_model")
    # print(
    #     "Reloaded Extracted Skills:",
    #     new_pipeline.process_job_description(job_description),
    # )
