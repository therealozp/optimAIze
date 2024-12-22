# resume entry evaluation pipeline

this project provides a robust pipeline to evaluate resume entries against job descriptions using llms. the system is designed to assess the relevancy, quality, and impact of resume entries, assigning numerical scores and determining whether each entry should be "kept" or "thrown."

after that, the model will automatically select the "best" ranking ones and proceed to tailor them to the job description.

## features

- evaluates resume entries based on relevancy, quality, and measurable impact.
- assigns a numerical score (0-10) for each entry.
- prioritizes and reorders entries based on importance.
- provides detailed feedback for improvement.
- uses the ollama model (e.g., llama3.2) for evaluations.

## prerequisites

1. **install ollama**

   - download and set up ollama from [ollama's official website](https://ollama.ai).
   - ensure the required model (`llama3.2`) is available.

2. **python environment**
   - install python 3.8 or later.
   - install dependencies using `pip install -r requirements.txt`.

## usage

**prepare inputs**
currently, the only supported resume format is LaTeX, which allows for the easiest processing thanks to its structured input capabilities.

functionality to process PDF files or Word files **will be added soon**, but is likely to be _less deterministic_ than latex because of its high unstructuredness.

## project structure

- `app.py` contains all of the UI pages managed by Streamlit.
  |-- `preprocess` folder contains all "parsing" or "extraction" functions defined
  |-- `exec` contains everything to do with "evaluation" or "writing", etc.
  |-- `samples` contain sample, testing data of

## customization

you can extend or modify the evaluation criteria by editing the prompt in `evaluate_resume_entry`. adjust parameters such as `temperature` or `context_length` in the ollama configuration for different evaluation behaviors.

## contributing

1. fork the repository.
2. create a feature branch (`git checkout -b feature-name`).
3. commit your changes (`git commit -m "add feature-name"`).
4. push the branch (`git push origin feature-name`).
5. open a pull request.

### **Completed Tasks**

- [x] parse job information
- [x] predefined latex parsing for resumes
- [x] skill NER pipeline with spacy
- [x] relevancy evaluation with ollama

---

### TODO

#### **1. make a resume "bank" for automation**

1. [x] define schema for resume metadata (e.g., position, skills, experience, and contact details).
2. [x] create a database or file-based storage solution for storing resumes (e.g., sqlite, json files). **this is currently using a .pkl object**
3. [x] develop an interface to update and maintain the resume bank (e.g., add/remove resumes). **everything maintained with Streamlit right now**
4. [x] add ranking logic to select the most relevant resumes from the bank.

#### **2. automate bullet point rewriting pipeline**

1. [x] design prompt templates for rewriting resume bullets based on job description and requirements.
2. [x] integrate rewriting functionality with the ollama model for refinement.
3. [x] define quality checks to ensure rewritten bullets are concise, impactful, and measurable.
4. [ ] build a feedback loop for iterative improvement of rewritten bullets.

EXTRAS

- [ ] define character/word limits to avoid overwriting
- [ ] implement better non-redundancy check between bullet points
- [ ] figure out a better way of handling rewrites + few-shot prompting (THERE IS ONE BULLET THAT REFUSES TO REWRITE FOR SOME REASON)

#### **3. integrate pdfLatex compiler**

1. [ ] set up a pdfLatex compiler in the environment (e.g., install `texlive`).
2. [ ] test basic LaTeX templates for compatibility with the compiler.
3. [ ] integrate the compilation process into the pipeline.
4. [ ] handle errors and edge cases during LaTeX compilation (e.g., missing packages, syntax errors).
