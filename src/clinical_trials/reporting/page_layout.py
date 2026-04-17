from __future__ import annotations


PAGE_DISCLAIMER = (
    "This review includes analyses derived from a combination of publicly available structural "
    "source data and documented synthetic continuity extensions for the fictional NTX-101 program. "
    "It is intended for internal methodological demonstration only and is not intended for external "
    "publication, regulatory submission, or treatment decision-making."
)


def build_nav(depth: int) -> list[tuple[str, str]]:
    prefix = "" if depth == 0 else "../"
    return [
        ("Home", f"{prefix}index.html"),
        ("Integrated report", f"{prefix}final_report/index.html"),
        ("Program overview", f"{prefix}program_overview/index.html"),
        ("Data lineage", f"{prefix}data_lineage/index.html"),
        ("Model review", f"{prefix}model_cards/index.html"),
        ("Phase I", f"{prefix}phase1/index.html"),
        ("Phase II", f"{prefix}phase2/index.html"),
        ("Phase III", f"{prefix}phase3/index.html"),
    ]


def build_page_context(
    *,
    depth: int,
    page_title: str,
    page_kicker: str,
    page_subtitle: str,
) -> dict:
    return {
        "nav": build_nav(depth),
        "page_title": page_title,
        "page_kicker": page_kicker,
        "page_subtitle": page_subtitle,
        "disclaimer": PAGE_DISCLAIMER,
    }
