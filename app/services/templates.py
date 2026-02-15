from pathlib import PosixPath
from typing import Any

from fastapi.templating import Jinja2Templates


class TemplateFactory:
    _template_dir: PosixPath
    _jinja2_templates: Jinja2Templates

    def __init__(self, template_dir: PosixPath):
        self._template_dir = template_dir
        self._jinja2_templates = Jinja2Templates(
            directory=template_dir,
            enable_async=True,
        )

    async def render(self, template_path: str, context: dict[str, Any]) -> str:
        html_template = self._jinja2_templates.get_template(name=template_path)
        return await html_template.render_async(**context)
