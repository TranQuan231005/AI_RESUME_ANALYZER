import re
from typing import Set
from app.schemas import ParsedDocument, ResumeFeatures, ScoreBreakdown


def calculate_score(document: ParsedDocument, features: ResumeFeatures) -> ScoreBreakdown:
    text = document.text or ""
    contact_score = 0.0
    cand_name = getattr(features, "candidateName", None) or getattr(features, "candidate_name", None)
    if cand_name and str(cand_name).strip():
        contact_score += 2.5
    cand_email = getattr(features, "candidateEmail", None) or getattr(features, "candidate_email", None)
    if cand_email and str(cand_email).strip():
        contact_score += 2.5
    contact = min(5, max(0, int(contact_score)))

    ALL_SECTION_HEADERS = [
        "summary", "profile", "professional summary", "about me", "objective",
        "education", "academic background", "qualifications", "academic history",
        "experience", "employment", "work history", "work experience", "professional experience",
        "projects", "personal projects", "academic projects", "key projects",
        "achievements", "certifications", "awards", "certificates", "honors",
        "skills", "technical skills", "core competencies", "technologies",
        "languages", "interests", "activities", "publications", "references", "contact",
    ]
    all_headers_pattern = r"|".join(re.escape(h) for h in ALL_SECTION_HEADERS)

    def extract_section_content(headers: list) -> str:
        target_pattern = r"|".join(re.escape(h) for h in headers)
        # Bắt đầu tại header mục tiêu, kết thúc tại header kế tiếp (có hoặc không có dấu hai chấm) hoặc cuối văn bản
        pattern = (
            rf"(?im)^[ \t]*(?:{target_pattern})\b[ \t]*:?[ \t]*\n+"
            rf"([\s\S]*?)"
            rf"(?=^[ \t]*(?:{all_headers_pattern})\b[ \t]*:?[ \t]*$|\Z)"
        )
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        # Fallback tìm kiếm inline/loose nếu không ở đầu dòng riêng
        loose_pattern = (
            rf"(?i)(?:^|\n)[ \t]*(?:{target_pattern})\b[:\s]*\n?"
            rf"(.*?)"
            rf"(?=\n[ \t]*(?:{all_headers_pattern})\b[:\s]*|\Z)"
        )
        loose_match = re.search(loose_pattern, text, re.DOTALL)
        return loose_match.group(1).strip() if loose_match else ""

    summary_content = extract_section_content(["summary", "profile", "professional summary", "about me"])
    if len(summary_content) >= 20:
        summary_score = 10
    elif len(summary_content) > 0:
        summary_score = 5
    elif re.search(r"(?i)\b(summary|profile|about me)\b", text):
        summary_score = 3
    else:
        summary_score = 0
    summary = min(10, max(0, summary_score))

    raw_skills = getattr(features, "skills", []) or []
    unique_skills: Set[str] = {s.strip().lower() for s in raw_skills if s and s.strip()}
    skills_score = len(unique_skills) * 3
    skills = min(15, max(0, skills_score))

    edu_content = extract_section_content(["education", "academic background", "qualifications"])
    if len(edu_content) >= 15:
        education_score = 10
    elif re.search(r"(?i)\b(education|university|bachelor|master|degree)\b", text):
        education_score = 5
    else:
        education_score = 0
    education = min(10, max(0, education_score))

    exp_content = extract_section_content(["experience", "employment", "work history", "work experience"])
    has_action_bullets = bool(re.search(r"[-•*]\s*\w+", exp_content))
    if len(exp_content) > 80 or has_action_bullets:
        experience_score = 20
    elif len(exp_content) > 0:
        experience_score = 10
    elif re.search(r"(?i)\b(experience|work history)\b", text):
        experience_score = 5
    else:
        experience_score = 0
    experience = min(20, max(0, experience_score))

    proj_content = extract_section_content(["projects", "personal projects", "academic projects"])
    if len(proj_content) >= 30:
        projects_score = 15
    elif len(proj_content) > 0:
        projects_score = 8
    elif re.search(r"(?i)\b(project|projects)\b", text):
        projects_score = 4
    else:
        projects_score = 0
    projects = min(15, max(0, projects_score))

    ach_content = extract_section_content(["achievements", "certifications", "awards", "certificates", "honors"])
    if len(ach_content) >= 15:
        achievements_score = 10
    elif re.search(r"(?i)\b(certification|certificate|award|achievement)\b", text):
        achievements_score = 5
    else:
        achievements_score = 0
    achievements = min(10, max(0, achievements_score))

    cleaned_text = re.sub(r"\b(19|20)\d{2}\b", "", text)
    cleaned_text = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "", cleaned_text)
    impact_matches = re.findall(
        r"\b(?:\d+(?:\.\d+)?%\b|\$\d+|\b\d+x\b|\+\d+%\b|\b\d+\s*(?:users|customers|clients|percent|ms|s)\b)",
        cleaned_text,
        re.IGNORECASE
    )
    unique_impacts = {m.lower() for m in impact_matches}
    impact_score = len(unique_impacts) * 5
    impact = min(15, max(0, impact_score))

    total = contact + summary + skills + education + experience + projects + achievements + impact
    total = min(100, max(0, total))

    return ScoreBreakdown(
        contact=contact,
        summary=summary,
        skills=skills,
        education=education,
        experience=experience,
        projects=projects,
        achievements_certifications=achievements,
        quantified_impact=impact,
        total=total
    )