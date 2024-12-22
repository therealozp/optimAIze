import streamlit as st
from exec.rewrite_bullet import ResumeRewriter

st.title("Rewrite Optimal Bullets")
entries = st.session_state.optimal_combination

st.write("The following entries are recommended:")
for exp, eval_ in entries:
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


if st.button("Rewrite Bullets"):
    rewriter = ResumeRewriter(job_description=st.session_state.hlr)
    for entry, eval_ in entries:
        if "responsibilities" in entry:
            st.write("### Entry:", entry["position_name"], "at", entry["company_name"])
            for bullet in entry["responsibilities"]:
                st.write("##### Original Bullet:")
                st.write(bullet)
                rewritten_bullet = None
                retries = 0
                while rewritten_bullet is None and retries < 3:
                    try:
                        is_rewritten, rewritten_bullet = rewriter.rewrite_no_check(
                            entry, bullet
                        )
                        if is_rewritten:
                            st.write("-> Rewritten:", rewritten_bullet)
                        else:
                            st.write(
                                "-> The gods have deemed your bullet satisfactory."
                            )
                    except Exception as e:
                        st.write(
                            f"An error occurred: {e}. Retrying {retries + 1} times..."
                        )
                        retries += 1
                        continue
                    finally:
                        if rewritten_bullet is None:
                            retries += 1
                            st.write(
                                f"Model did not produce any output. Retrying {retries + 1} times..."
                            )
                            continue
                        else:
                            break
        else:
            st.write("### Entry:", entry["project_name"])
            for bullet in entry["details"]:
                st.write("##### Original Bullet:")
                st.write(bullet)
                rewritten_bullet = None
                retries = 0
                while rewritten_bullet is None and retries < 3:
                    try:
                        is_rewritten, rewritten_bullet = rewriter.rewrite_no_check(
                            entry, bullet
                        )
                        if is_rewritten:
                            st.write("-> Rewritten:", rewritten_bullet)
                        else:
                            st.write(
                                "-> The gods have deemed your bullet satisfactory."
                            )
                    except Exception as e:
                        st.write(
                            f"An error occurred: {e}. Retrying {retries + 1} times..."
                        )
                        retries += 1
                        continue
                    finally:
                        if rewritten_bullet is None:
                            retries += 1
                            st.write(
                                f"Model did not produce any output. Retrying {retries + 1} times..."
                            )
                            continue
                        else:
                            break
