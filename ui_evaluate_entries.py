import streamlit as st

from exec.evaluate_entries import evaluate_resume_entry
from exec.rank_entries import max_score_combination, get_final_score

resume_data = st.session_state.resume_data
job_skills = st.session_state.job_skills

st.write("# Tailoring")
st.write("## Role debrief")
st.write("### General Responsibilities")
st.write(st.session_state.hlr)
st.write("### Skills")
st.write(job_skills)

st.write("## Relevance evaluation")
if st.button("Evaluate bullets"):
    # for each entry, gather context -> feed into LLM
    # LLM should gather context between job description and resume -> give a score as to how close each project / experience is to the line of work involved in the job description
    st.session_state.exp_evals = []
    st.session_state.proj_evals = []

    try:
        for section in resume_data["sections"]:
            for entry in section["entries"]:
                if section["name"].lower() == "experience":
                    st.write(
                        "### Entry:",
                        entry["position_name"],
                        "at",
                        entry["company_name"],
                    )
                elif section["name"].lower() == "projects":
                    st.write("### Entry:", entry["project_name"])

                st.write(entry)
                retries = 0
                model_response = None
                while model_response is None and retries <= 3:
                    try:
                        model_response = evaluate_resume_entry(
                            entry,
                            job_description=st.session_state.hlr,
                            job_skills=", ".join(job_skills),
                            project_mode=(section["name"].lower() == "projects"),
                        )
                    except Exception as e:
                        st.write(f"An error occurred: {e}. Retrying {retries} times...")
                        retries += 1
                        continue
                    finally:

                        if not model_response:
                            retries += 1
                            st.write(
                                f"Model did not produce any output. Retrying {retries} times..."
                            )
                            continue
                        else:
                            break

                if retries > 3:
                    st.write("Failed to get a response after 3 retries.")
                    raise Exception("Model did not produce any output.")

                st.write("Comments:", model_response.comments)
                st.write("Suggestions:", model_response.suggestions)
                st.write("Relevance score:", model_response.relevance_score)
                st.write("Technical score:", model_response.technical_score)
                st.write("Impact score:", model_response.impact_score)
                st.write("Final score:", get_final_score(model_response))

                if section["name"].lower() == "experience":
                    st.session_state.exp_evals.append((entry, model_response))
                elif section["name"].lower() == "projects":
                    st.session_state.proj_evals.append((entry, model_response))
    except Exception as e:
        st.write(f"An error occurred: {e}. Press regenerate to try again.")

    try:
        st.session_state.exp_evals.sort(
            key=lambda x: get_final_score(x[1]), reverse=True
        )
        st.session_state.proj_evals.sort(
            key=lambda x: get_final_score(x[1]), reverse=True
        )
        # evaluate max_score achieved for each combination of experiences and projects
        st.write("### Model-recommended resume")
        max_combos = max_score_combination(
            st.session_state.exp_evals, st.session_state.proj_evals
        )
        st.session_state.optimal_combination = max_combos
        st.write("The following entries are recommended:")
        print()
        for exp, eval_ in max_combos:
            if "position_name" in exp:
                st.write(exp["position_name"], "at", exp["company_name"])
                st.write(
                    "Total score:",
                    eval_.relevance_score + eval_.technical_score + eval_.impact_score,
                )
            else:
                st.write(exp["project_name"])
                st.write(
                    "Total score:",
                    eval_.relevance_score + eval_.technical_score + eval_.impact_score,
                )
    except Exception as e:
        st.write(f"An error occurred: {e}. Press regenerate to try again.")
