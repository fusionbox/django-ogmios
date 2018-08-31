from django.template import TemplateDoesNotExist
from django.template.loader import engines


def get_template_source(template_name):
    for engine in engines.all():
        for loader in engine.engine.template_loaders:
            for origin in loader.get_template_sources(template_name):
                try:
                    return loader.get_contents(origin)
                except TemplateDoesNotExist:
                    pass
    raise TemplateDoesNotExist(template_name)
