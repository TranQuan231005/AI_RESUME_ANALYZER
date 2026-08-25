TAXONOMY_BY_FIELD = {
    "Software Engineering": ["Docker", "Kubernetes", "CI/CD", "TypeScript", "React", "Node.js", "Redis", "GraphQL", "PostgreSQL", "AWS"],
    "Data Science": ["Python", "Pandas", "PyTorch", "SQL", "Scikit-Learn", "Docker", "Airflow", "Tableau", "Spark", "MLflow"],
    "Unknown": ["Communication", "Problem Solving", "Teamwork", "Time Management", "Git", "Project Management"]
}

def generate_recommendations(score_breakdown: dict, existing_skills: list, predicted_field: str) -> dict:
    """
    Gợi ý kỹ năng và nội dung cải thiện CV (Max 8 skills, Max 8 recommendations).
    """
    available_skills = TAXONOMY_BY_FIELD.get(predicted_field, TAXONOMY_BY_FIELD["Unknown"])
    normalized_existing = [s.lower() for s in existing_skills]

    recommended_skills = [
        skill for skill in available_skills 
        if skill.lower() not in normalized_existing
    ][:8]

    recommendations = []

    if score_breakdown.get("contact", 0) < 5:
        recommendations.append("Ensure your full name, professional email, and phone number are clearly visible at the top.")
    if score_breakdown.get("summary", 0) < 10:
        recommendations.append("Add a concise professional summary highlighting your key achievements and career goal.")
    if score_breakdown.get("skills", 0) < 15:
        recommendations.append("Expand your skills section with specific technical tools relevant to your target role.")
    if score_breakdown.get("education", 0) < 10:
        recommendations.append("Include details about your degree, institution name, and graduation year.")
    if score_breakdown.get("experience", 0) < 20:
        recommendations.append("Detail your recent work experience using strong action verbs for each key responsibility.")
    if score_breakdown.get("projects", 0) < 15:
        recommendations.append("Highlight practical projects showcasing your specific technical role and outcomes.")
    if score_breakdown.get("achievementsCertifications", 0) < 10:
        recommendations.append("Add relevant professional certifications or awards to strengthen your credibility.")
    if score_breakdown.get("quantifiedImpact", 0) < 15:
        recommendations.append("Quantify your accomplishments using metrics and numbers (e.g., improved speed by 30%).")

    return {
        "recommendedSkills": recommended_skills[:8],
        "recommendations": recommendations[:8]
    }