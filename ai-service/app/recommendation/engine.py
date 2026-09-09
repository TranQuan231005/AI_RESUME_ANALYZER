TAXONOMY_BY_FIELD = {
    "Data Science": ["Python", "SQL", "Pandas", "NumPy", "scikit-learn", "TensorFlow"],
    "Web Development": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "SQL"],
    "Android Development": ["Java", "Kotlin", "SQL"],
    "iOS Development": ["Swift", "SwiftUI"],
    "UI/UX": ["Figma", "Adobe XD", "CSS", "HTML"],
    "Unknown": ["Python", "JavaScript", "SQL", "React", "HTML", "CSS", "Java", "Figma"]
}

def generate_recommendations(score_breakdown: dict, existing_skills: list, predicted_field: str) -> dict:
    """
    Gợi ý kỹ năng và nội dung cải thiện CV (Max 8 skills, Max 8 recommendations).
    """
    available_skills = TAXONOMY_BY_FIELD.get(predicted_field, TAXONOMY_BY_FIELD["Unknown"])
    normalized_existing = [s.casefold() for s in existing_skills if isinstance(s, str)]

    recommended_skills = [
        skill for skill in available_skills 
        if skill.casefold() not in normalized_existing
    ][:8]

    recommendations = []

    def _get_score(key_camel: str, key_snake: str, default: int = 0) -> int:
        if key_camel in score_breakdown:
            return score_breakdown[key_camel]
        if key_snake in score_breakdown:
            return score_breakdown[key_snake]
        return default

    if _get_score("contact", "contact") < 5:
        recommendations.append("Ensure your full name and professional email are clearly visible at the top of your resume.")
    if _get_score("summary", "summary") < 10:
        recommendations.append("Add a concise professional summary highlighting your key achievements and career goal.")
    if _get_score("skills", "skills") < 15:
        recommendations.append("Expand your skills section with specific technical tools relevant to your target role.")
    if _get_score("education", "education") < 10:
        recommendations.append("Include details about your degree, institution name, and graduation year.")
    if _get_score("experience", "experience") < 20:
        recommendations.append("Detail your recent work experience using strong action verbs for each key responsibility.")
    if _get_score("projects", "projects") < 15:
        recommendations.append("Highlight practical projects showcasing your specific technical role and outcomes.")
    if _get_score("achievementsCertifications", "achievements_certifications") < 10:
        recommendations.append("Add relevant professional certifications or awards to strengthen your credibility.")
    if _get_score("quantifiedImpact", "quantified_impact") < 15:
        recommendations.append("Quantify your accomplishments using metrics and numbers (e.g., improved speed by 30%).")

    return {
        "recommendedSkills": recommended_skills[:8],
        "recommendations": recommendations[:8]
    }