from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from clinical_trials.reporting.page_layout import build_page_context


def render_phase2_report(
    context: dict, template_dir: str = "src/clinical_trials/reporting/templates"
) -> None:
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("phase2.html.j2")
    html = template.render(
        **build_page_context(
            depth=1,
            page_title="Phase II Endpoint and Model Review — NTX-101",
            page_kicker="Phase II",
            page_subtitle="Week 24 efficacy, responder analysis, and benchmarked predictive modeling for NTX-101 proof-of-concept evaluation.",
        ),
        **context,
    )
    out = Path("docs/phase2/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
