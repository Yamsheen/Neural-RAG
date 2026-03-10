# app/query_classifier.py

from typing import Literal


QueryType = Literal[
    "qa",
    "summary",
    "comparison",
    "dataset",
    "method"
]


def classify_query(query: str) -> QueryType:
    """
    Classify research query type.
    """

    q = query.lower()

    if "compare" in q or "difference between" in q:
        return "comparison"

    if "summarize" in q or "summary" in q:
        return "summary"

    if "dataset" in q or "data used" in q:
        return "dataset"

    if "method" in q or "approach" in q:
        return "method"

    return "qa"


def is_research_question(query: str) -> bool:
    """
    Detect if question relates to research analysis.
    """

    keywords = [
        "dataset",
        "method",
        "experiment",
        "result",
        "paper",
        "model",
        "accuracy"
    ]

    q = query.lower()

    return any(k in q for k in keywords)