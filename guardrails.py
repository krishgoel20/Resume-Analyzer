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
        skill for skill in result.matching_skills
        if skill.lower() not in lowered_resume
    ]
    if len(unverifiable_skills) > len(result.matching_skills) / 2:
        warnings.append(
            "Several 'matching skills' don't appear verbatim in the resume text — "
            "the analysis may be inaccurate or the resume used different terminology."
        )

    return warnings