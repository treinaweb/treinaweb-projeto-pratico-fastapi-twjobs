from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


TemplateNames = Literal["email/welcome.html"]


def render_template(template_name: TemplateNames, context: dict) -> str:
    template = jinja_env.get_template(template_name)
    return template.render(context)
