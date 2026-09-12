from typing import TypedDict, Optional, List
from models import ResumeAnalysis, VerificationBatch

class PipelineState(TypedDict):
    resume_text: str
    job_description: str
    error: Optional[str]
    result: Optional[ResumeAnalysis]
    verification: Optional[VerificationBatch]
    warnings: List[str]

from guardrails import validate_extracted_text, detect_prompt_injection, validate_output_sanity
from analyzer import analyze_resume, verify_rewrites

def validate_node(state: PipelineState) -> dict:
    try:
        validate_extracted_text(state["resume_text"])
        detect_prompt_injection(state["resume_text"])
        return {"error": None}
    except ValueError as e:
        return {"error": str(e)}

def analyze_node(state: PipelineState) -> dict:
    result = analyze_resume(state["resume_text"], state["job_description"])
    return {"result": result}

def sanity_check_node(state: PipelineState) -> dict:
    warnings = validate_output_sanity(state["result"], state["resume_text"])
    return {"warnings": warnings}

def verify_rewrites_node(state: PipelineState) -> dict:
    verification = verify_rewrites(state["result"].rewritten_bullets)
    return {"verification": verification}

from langgraph.graph import StateGraph, START, END

def route_after_validation(state: PipelineState) -> str:
    if state["error"] is not None:
        return END
    return "analyze"

workflow = StateGraph(PipelineState)

workflow.add_node("validate", validate_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("verify_rewrites", verify_rewrites_node)
workflow.add_node("sanity_check", sanity_check_node)

workflow.add_edge(START, "validate")
workflow.add_conditional_edges("validate", route_after_validation, {"analyze": "analyze", END: END})
workflow.add_edge("analyze", "verify_rewrites")
workflow.add_edge("analyze", "sanity_check")
workflow.add_edge("sanity_check", END)

pipeline = workflow.compile()