import streamlit as st


def get_final_score(evaluation):
    # can add weights here later down the line
    return (
        evaluation.relevance_score
        + evaluation.technical_score
        + evaluation.impact_score
    )


def rank_experiences(exp_eval_pairs, min_experiences=2, max_experiences=4):
    categories = {
        "primary": 7,
        "secondary": 5,
        "fallback": 3,  # just to pad resume if min_experiences are not reached
    }
    exp_eval_pairs.sort(key=lambda x: get_final_score(x[1]), reverse=True)

    st.write("Based on the ranked metrics, the order to include experiences is:")
    selected_bullets = []
    for exp, eval in exp_eval_pairs:
        score = eval.relevance_score + eval.technical_score + eval.impact_score
        if len(selected_bullets) >= min_experiences:
            break
        if score >= categories["primary"]:
            selected_bullets.append(exp)

    if len(selected_bullets) < min_experiences:
        for exp, eval in exp_eval_pairs:
            if len(selected_bullets) >= max_experiences:
                break
            if score >= categories["secondary"]:
                selected_bullets.append(exp)

    if len(selected_bullets) < min_experiences:
        for exp, eval in exp_eval_pairs:
            if len(selected_bullets) >= max_experiences:
                break
            if score >= categories["fallback"]:
                selected_bullets.append(exp)

    return selected_bullets


def rank_projects(proj_eval_pairs, min_projects=2, max_projects=4):
    categories = {
        "primary": 7,
        "secondary": 5,
        "fallback": 3,  # just to pad resume if min_projects are not reached
    }
    proj_eval_pairs.sort(key=lambda x: get_final_score(x[1]), reverse=True)

    st.write("Based on the ranked metrics, the order to include projects is:")
    selected_projects = []
    for proj, eval in proj_eval_pairs:
        score = eval.relevance_score + eval.technical_score + eval.impact_score
        if len(selected_projects) >= min_projects:
            break
        if eval.relevance_score >= categories["primary"]:
            selected_projects.append(proj)

    for proj, eval in proj_eval_pairs:
        if len(selected_projects) >= max_projects:
            break
        if eval.relevance_score >= categories["secondary"]:
            selected_projects.append(proj)

    if len(selected_projects) < min_projects:
        for proj, eval in proj_eval_pairs:
            if len(selected_projects) >= max_projects:
                break
            if eval.relevance_score >= categories["fallback"]:
                selected_projects.append(proj)

    return selected_projects


def get_final_score(
    evaluation, relevance_weight=1, technical_weight=1, impact_weight=1
):
    return (
        evaluation.relevance_score * relevance_weight
        + evaluation.technical_score * technical_weight
        + evaluation.impact_score * impact_weight
    )


def max_score_combination(
    experiences,
    projects,
    min_total: int = 4,  # Minimum total entries needed
    max_total: int = 6,  # Maximum total entries allowed
    min_exp: int = 2,
    min_proj: int = 1,
):
    """
    Find optimal combination of experiences and projects that maximizes total score
    while satisfying minimum requirements.

    Args:
        experiences: List of (experience, evaluation) tuples, sorted by descending score
        projects: List of (project, evaluation) tuples, sorted by descending score
        min_total: Minimum total entries needed
        max_total: Maximum total entries allowed
        min_exp: Minimum experiences needed
        min_proj: Minimum projects needed

    Returns:
        List of selected (entry, evaluation) tuples
    """
    best_score = 0
    best_combination = None

    # Get available counts
    num_exp_available = len(experiences)
    num_proj_available = len(projects)

    # Try all valid combinations
    for num_exp in range(min_exp, min(num_exp_available + 1, max_total - min_proj + 1)):
        for num_proj in range(
            min_proj, min(num_proj_available + 1, max_total - num_exp + 1)
        ):
            total = num_exp + num_proj

            # Check if total is within bounds
            if total < min_total or total > max_total:
                continue

            # Get top N entries from each list
            selected_exp = experiences[:num_exp]
            selected_proj = projects[:num_proj]

            # Calculate total score
            total_score = sum(
                get_final_score(eval_) for _, eval_ in selected_exp + selected_proj
            )

            # Update best if this is better
            if total_score > best_score:
                best_score = total_score
                best_combination = selected_exp + selected_proj

    if best_combination is None:
        raise ValueError("No valid combination found with given constraints")

    return best_combination
