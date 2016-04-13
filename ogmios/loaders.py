"""
Module for finding templates from configured loaders.
"""

from distutils.version import StrictVersion

import django
from django.template import Template, Context, TemplateDoesNotExist, engines

def get_template_source_from_loader(template_loader, instance):
    """
    Return the source for a file from the template loader.
    """
    try:
        # This should work for templates that are not the cached template loader
        return template_loader.load_template_source(instance.filename)[0]
    except NotImplementedError:
        # This might be the cached template loader. Its load_template_source()
        # method is not implemented

        for temp in template_loader.loaders:
            try:
                return temp.load_template_source(instance.filename)[0]
            except TemplateDoesNotExist:
                # There may be many wrapped loaders.
                # We need to get through the whole list before
                # throwing an exception.
                pass

    raise TemplateDoesNotExist(instance.filename)

def get_template_source_from_engine(engine, instance):
    """
    Attempt to find a specific template in the given engine.
    """
    for template_loader in engine.engine.template_loaders:
        try:
            return get_template_source_from_loader(template_loader, instance)
        except TemplateDoesNotExist:
            # Go through all the template loaders before throwing
            # an exception.
            pass

    raise TemplateDoesNotExist(instance.filename)

def get_template_source(instance):
    """
    Check all configured engines for a specific template.
    """
    if instance.template_loader is None:
        engine_list = engines.all()
    else:
        engine_list = [engines[instance.template_loader]]

    for engine in engine_list:
        try:
            return get_template_source_from_engine(engine, instance)
        except TemplateDoesNotExist:
            # Go through all the template engines before raising
            # an exception
            pass

    raise TemplateDoesNotExist(instance.filename)
