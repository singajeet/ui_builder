from jinja2 import BaseLoader,TemplateNotFound,Template,Environment
import os
import init_log


init_log.config_logs()
logger = logging.getLogger(__name__)

class ComponentLoader(BaseLoader):

    """Docstring for ComponentLoader. """

    def __init__(self, path):
        """TODO: to be defined1. """
        BaseLoader.__init__(self)
        self.path = path

    def get_source(self, environment, template):
        """TODO: Docstring for get_source.

        :environment: TODO
        :returns: TODO

        """
        path = os.path.join('./', template)
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            with file(path) as f:
                source = f.read().decode('utf-8')
                return source, path, lambda: mtime == os.path.getmtime(path)


class Component(object):

    """Docstring for Component. """

    def __init__(self):
        """TODO: to be defined1. """
        self.template_env = Environment(loader = ComponentLoader(self.template_path))
