# app/research_parser.py

import re
from typing import Dict, List


SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "method": r"\bmethod(s)?\b",
    "dataset": r"\bdataset(s)?\b",
    "experiments": r"\bexperiment(s)?\b",
    "results": r"\bresult(s)?\b",
    "discussion": r"\bdiscussion\b",
    "limitations": r"\blimitation(s)?\b",
    "conclusion": r"\bconclusion(s)?\b"
}


def detect_section(text: str) -> str:
    """
    Identify which research section a chunk belongs to.
    """

    text_lower = text.lower()

    for section, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text_lower[:200]):
            return section

    return "general"


def extract_datasets(text: str) -> List[str]:
    """
    Detect common dataset mentions.
    """

    datasets = [
        "imagenet",
        "cifar-10",
        "cifar10",
        "mnist",
        "glue",
        "squad",
        "fashion-mnist",
        "mscoco",
        "coco"
    ]

    found = []

    lower = text.lower()

    for d in datasets:
        if d in lower:
            found.append(d)

    return list(set(found))


def extract_models(text: str) -> List[str]:
    """
    Detect ML model mentions.
    """

    models = [
        "transformer",
        "bert",
        "gpt",
        "resnet",
        "vit",
        "cnn",
        "lstm"
    ]

    found = []

    lower = text.lower()

    for m in models:
        if m in lower:
            found.append(m)

    return list(set(found))


def extract_paper_insights(text: str) -> Dict:
    """
    Extract structured research insights.
    """

    return {
        "datasets": extract_datasets(text),
        "models": extract_models(text)
    }