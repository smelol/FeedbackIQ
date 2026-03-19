from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path("src/reports/templates")
OUTPUT_DIR = Path("data/reports")


def render_weekly_report(context: dict) -> Path:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("weekly_report.html")
    html = template.render(**context)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "weekly_report.html"

    output_path.write_text(html, encoding="utf-8")
    return output_path