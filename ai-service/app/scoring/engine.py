def calculate_score(features: dict) -> dict:
    """
    Tính điểm CV dựa trên 8 thành phần Rubric (Tối đa 100 điểm).
    Đảm bảo tính Deterministic: Cùng input luôn ra cùng output.
    """
    contact = min(5, max(0, int(features.get("contact_score", 0))))
    summary = min(10, max(0, int(features.get("summary_score", 0))))
    skills = min(15, max(0, int(features.get("skills_score", 0))))
    education = min(10, max(0, int(features.get("education_score", 0))))
    experience = min(20, max(0, int(features.get("experience_score", 0))))
    projects = min(15, max(0, int(features.get("projects_score", 0))))
    achievements = min(10, max(0, int(features.get("achievements_score", 0))))
    impact = min(15, max(0, int(features.get("impact_score", 0))))
    total = contact + summary + skills + education + experience + projects + achievements + impact

    return {
        "contact": contact,
        "summary": summary,
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "achievementsCertifications": achievements,
        "quantifiedImpact": impact,
        "total": total
    }