from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from clinical_trials.reporting.page_layout import build_page_context


def render_phase3_report(
    context: dict, template_dir: str = "src/clinical_trials/reporting/templates"
) -> None:
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("phase3.html.j2")
    html = template.render(
        **build_page_context(
            depth=1,
            page_title="Phase III Confirmatory Review — NTX-101",
            page_kicker="Phase III",
            page_subtitle="Confirmatory time-to-clinical-worsening analysis and integrated safety interpretation for NTX-101.",
        ),
        **context,
    )
    out = Path("docs/phase3/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
