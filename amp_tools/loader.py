from django.template import TemplateDoesNotExist
from django.template.loaders.cached import Loader as DjangoCachedLoader


from amp_tools import get_amp_detect
from amp_tools.settings import settings
from amp_tools.compat import BaseLoader, template_loader


class Loader(BaseLoader):
    is_usable = True
    _template_source_loaders = None

    def get_contents(self, origin):
        return origin.loader.get_contents(origin)

    def get_template_sources(self, template_name):
        template_name = self.prepare_template_name(template_name)
        for loader in self.template_source_loaders:
            if hasattr(loader, 'get_template_sources'):
                try:
                    for result in loader.get_template_sources(template_name):
                        yield result
                except UnicodeDecodeError:
                    # The template dir name was a bytestring that wasn't valid UTF-8.
                    raise
                except ValueError:
                    # The joined path was located outside of this particular
                    # template_dir (it might be inside another one, so this isn't
                    # fatal).
                    pass

    def prepare_template_name(self, template_name):
        template_name = u'%s/%s' % (get_amp_detect(), template_name)
        if settings.AMP_TOOLS_TEMPLATE_PREFIX:
            template_name = settings.AMP_TOOLS_TEMPLATE_PREFIX + template_name
        return template_name

    def load_template_source(self, template_name, template_dirs=None):
        template_name = self.prepare_template_name(template_name)
        for loader in self.template_source_loaders:
            if hasattr(loader, 'load_template_source'):
                try:
                    return loader.load_template_source(
                        template_name,
                        template_dirs)
                except TemplateDoesNotExist:
                    pass
        raise TemplateDoesNotExist("Tried %s" % template_name)

    @property
    def template_source_loaders(self):
        if not self._template_source_loaders:
            loaders = []
            for loader_name in settings.AMP_TOOLS_TEMPLATE_LOADERS:
                loader = template_loader(loader_name)
                if loader is not None:
                    loaders.append(loader)
            self._template_source_loaders = tuple(loaders)
        return self._template_source_loaders


class CachedLoader(DjangoCachedLoader):
    is_usable = True

    def cache_key(self, template_name, skip=None):
        key = super(CachedLoader, self).cache_key(template_name, skip)
        return '{0}:{1}'.format(get_amp_detect(), key)
