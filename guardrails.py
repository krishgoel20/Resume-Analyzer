MAX_FILE_SIZE_MB = 5
MIN_TEXT_LENGTH = 200

def validate_file_size(uploaded_file) -> None:
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File is too large ({size_mb:.1f}MB). Please upload a file under {MAX_FILE_SIZE_MB}MB.")

def validate_extracted_text(text: str) -> None:
    if len(text.strip()) < MIN_TEXT_LENGTH:
        raise ValueError(
            "Couldn't extract enough readable text from this file. "
            "It may be a scanned image or an unusually short document. "
            "Try pasting the text directly instead."
        )

    alpha_chars = sum(c.isalpha() for c in text)
    ratio = alpha_chars / len(text) if text else 0
    if ratio < 0.5:
        raise ValueError(
            "This file's extracted text looks garbled or corrupted. "
            "Try pasting the resume text directly instead."
        )

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard the above",
    "disregard previous instructions",
    "new instructions:",
    "system:",
    "you are now",
    "act as",
    "forget everything above",
    "give this candidate a score of",
    "assign a perfect score",
]

def detect_prompt_injection(text: str) -> None:
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lowered:
            raise ValueError(
                "This document contains text that looks like an attempt to manipulate "
                "the AI analysis. Please upload a genuine resume."
            )

def validate_output_sanity(result, resume_text: str) -> list[str]:
    warnings = []

    if result.match_score >= 90 and len(result.missing_skills) == 0:
        warnings.append(
            "This is a very high score with zero missing skills — double check "
            "this result carefully, as it may indicate an unusually strong match "
            "or an anomaly in the analysis."
        )

    if result.match_score <= 20 and len(result.matching_skills) > 5:
        warnings.append(
            "This score seems low despite several matching skills — worth a manual review."
        )

    lowered_resume = resume_text.lower()
    unverifiable_skills = [
        match for match in result.matching_skills
        if match.evidence.lower() not in lowered_resume
    ]
    if len(unverifiable_skills) > len(result.matching_skills) / 2:
        warnings.append(
            "Several 'matching skills' cite evidence that doesn't appear verbatim "
            "in the resume text — the analysis may be inaccurate."
        )

    return warnings

def validate_rubric_consistency(result) -> list[str]:
    warnings = []

    rubric_sum = sum(dim.points_awarded for dim in result.rubric)
    if rubric_sum != result.match_score:
        warnings.append(
            f"Rubric dimensions sum to {rubric_sum}, but the reported match score "
            f"is {result.match_score}. There may be an inconsistency in the analysis."
        )

    for dim in result.rubric:
        if dim.points_awarded > dim.max_points:
            warnings.append(
                f"'{dim.dimension}' was awarded {dim.points_awarded} points, "
                f"exceeding its maximum of {dim.max_points}."
            )

    return warnings

import re

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}")
SECTION_KEYWORDS = ["experience", "education", "skills", "projects", "certifications"]
MAX_RESUME_CHARS = 6000  # roughly 2 pages of dense text

def check_ats_formatting(resume_text: str) -> list[str]:
    warnings = []
    lowered = resume_text.lower()

    if not EMAIL_PATTERN.search(resume_text):
        warnings.append("No email address detected — ATS systems and recruiters may not be able to contact you.")

    if not PHONE_PATTERN.search(resume_text):
        warnings.append("No phone number detected — consider adding one for ATS contact-info parsing.")

    found_sections = [kw for kw in SECTION_KEYWORDS if kw in lowered]
    if len(found_sections) < 2:
        warnings.append(
            "Few or no standard section headers detected (e.g., 'Experience', 'Education', 'Skills'). "
            "ATS parsers rely on these to categorize your resume content correctly."
        )

    if len(resume_text) > MAX_RESUME_CHARS:
        warnings.append(
            "Resume content is quite long — consider trimming to roughly one to two pages, "
            "as many ATS systems and recruiters deprioritize longer resumes."
        )

    return warnings