from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from clinical_trials.reporting.page_layout import build_page_context


def render_phase1_report(
    context: dict, template_dir: str = "src/clinical_trials/reporting/templates"
) -> None:
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("phase1.html.j2")
    html = template.render(
        **build_page_context(
            depth=1,
            page_title="Phase I Safety Review — NTX-101",
            page_kicker="Phase I",
            page_subtitle="Safety, tolerability, laboratory, and vital-sign review for NTX-101 early development assessment.",
        ),
        **context,
    )
    out = Path("docs/phase1/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
