"""
Compatibility layer for Django 1.7 and 1.8.

Django 1.8 introduced support for multiple templating engines, and
Ogmios needs to check each of the engines for the desired template.

In Django 1.7 Ogmios needs to check the loaders for the only engine
Django supports.
"""

from distutils.version import StrictVersion

import django
from django.template import Template, Context, TemplateDoesNotExist

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

def get_template_source_from_engine_module(engines, instance):
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

def get_template_source_from_loader_module(loader_module, instance):
    try:
        loader_module.find_template('') # Just to preload template_source_loader_module
    except TemplateDoesNotExist:
        pass

    for loader in loader_module.template_source_loaders:
        try:
            return get_template_source_from_loader(loader, instance)
        except TemplateDoesNotExist:
            pass

    raise TemplateDoesNotExist(instance.filename)

try:
    # Engines was introduced in Django 1.8
    from django.template import engines
    def get_template_source(instance):
        return get_template_source_from_engine_module(engines, instance)
except ImportError:
    # We have Django 1.7
    from django.template import loader as loader_module
    def get_template_source(instance):
        return get_template_source_from_loader_module(loader_module, instance)
