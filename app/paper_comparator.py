# app/paper_comparator.py

from typing import List, Dict


def group_chunks_by_paper(chunks: List[Dict]) -> Dict:
    """
    Organize retrieved chunks by paper title.
    """

    papers = {}

    for c in chunks:

        title = c.get("paper_title", "Unknown")

        if title not in papers:
            papers[title] = []

        papers[title].append(c)

    return papers


def summarize_paper_chunks(chunks: List[Dict]) -> Dict:
    """
    Extract summary features for comparison.
    """

    sections = set()
    pages = set()

    for c in chunks:

        if "section" in c:
            sections.add(c["section"])

        if "page" in c:
            pages.add(c["page"])

    return {
        "sections_present": list(sections),
        "pages_used": sorted(list(pages))
    }


def compare_papers(chunks: List[Dict]) -> Dict:
    """
    Generate structured comparison data.
    """

    papers = group_chunks_by_paper(chunks)

    comparison = {}

    for title, paper_chunks in papers.items():

        comparison[title] = summarize_paper_chunks(paper_chunks)

    return comparison


def format_comparison_table(comparison: Dict) -> str:
    """
    Format comparison as readable table.
    """

    output = "\nPaper Comparison\n"
    output += "-" * 50 + "\n"

    for paper, data in comparison.items():

        sections = ", ".join(data["sections_present"])

        output += f"\nPaper: {paper}\n"
        output += f"Sections Found: {sections}\n"
        output += f"Pages Referenced: {data['pages_used']}\n"

    return output