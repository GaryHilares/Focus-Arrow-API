from abc import ABC, abstractmethod
from jinja2 import Environment, PackageLoader, select_autoescape


class AbstractTemplateRenderer(ABC):
    @abstractmethod
    def render(self, template_name, **kwargs) -> str:
        raise NotImplementedError


class JinjaTemplateRenderer(AbstractTemplateRenderer):
    def __init__(self, loader):
        self.env = Environment(loader=loader, autoescape=select_autoescape())

    def render(self, template_name: str, **kwargs) -> str:
        template = self.env.get_template(template_name)
        return template.render(**kwargs)
