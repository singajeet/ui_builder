# Script: models.py
# Author: Ajeet Singh
import uuid
from os import path
from os import linesep
from __future__ import with_statement


class Visibility:
    VISIBLE = 0
    HIDDEN = 1
    COLLAPSED = 2

class BaseElement:
    def __init__(self, name):
        self._key = uuid.uuid4()
        self._name = name
        self._security_key = ''

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

class UIElement(BaseElement):
    CONTENT_CONTROL = 0
    ITEMS_CONTROL = 1
    CONTAINER_CONTROL = 2
    FLYOUT_CONTROL = 4
    INPUT_CONTROL = 8
    OUTPUT_CONTROL = 16

    def __init__(self, name):
        BaseElement.__init__(self, name)
        self._parent = None
        self._template = None
        self._style = None
        self._control_type = None
        self._is_visible = True
        self._visibility = Visibility.VISIBLE
        self._enabled = True
        self._can_accept_clicks = True
        self._child = True

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is not None:
            self._parent = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        if value is not None:
            self._template = value

    def style():
        doc = "The style property."
        def fget(self):
            return self._style
        def fset(self, value):
            self._style = value
        def fdel(self):
            del self._style
        return locals()
    style = property(**style())

    def control_type():
        doc = "The control_type property."
        def fget(self):
            return self._control_type
        def fset(self, value):
            self._control_type = value
        def fdel(self):
            del self._control_type
        return locals()
    control_type = property(**control_type())

    def is_visible():
        doc = "The is_viaible property."
        def fget(self):
            return self._is_visible
        def fset(self, value):
            self._is_visible = value
        def fdel(self):
            del self._is_visible
        return locals()
    is_viaible = property(**is_visible())

    def visibility():
        doc = "The visibility property."
        def fget(self):
            return self._visibility
        def fset(self, value):
            self._visibility = value
        def fdel(self):
            del self._visibility
        return locals()
    visibility = property(**visibility())

    def enabled():
        doc = "The enabled property."
        def fget(self):
            return self._enabled
        def fset(self, value):
            self._enabled = value
        def fdel(self):
            del self._enabled
        return locals()
    enabled = property(**enabled())

    def can_accept_clicks():
        doc = "The can_accept_clicks property."
        def fget(self):
            return self._can_accept_clicks
        def fset(self, value):
            self._can_accept_clicks = value
        def fdel(self):
            del self._can_accept_clicks
        return locals()
    can_accept_clicks = property(**can_accept_clicks())

    def child():
        doc = "The child property."
        def fget(self):
            return self._child
        def fset(self, value):
            self._child = value
        def fdel(self):
            del self._child
        return locals()
    child = property(**child())

    def __str__(self):
        return self._name

    def render(self, childs):
        self._template.render_template_start()
        if child.control_type == UIElement.CONTENT_CONTROL:
            child.process_element(self)
        elif child.control_type == UIElement.ITEMS_CONTROL:
            for item in child.items:
                item.process_item_element(self)
        else:
            raise NameError('Invalid control specified')
        self._template.render_template_end()

    def process_item_element(self, parent):
        self.setup_control()
        self.render(self._child)

    def setup_control(self):
        pass

class PlaceHolder:
    def __init__(self, name, ctrl=None):
        self._name = name
        self._control = ctrl

    def name():
        doc = "The name property."
        def fget(self):
            return self._name
        def fset(self, value):
            self._name = value
        def fdel(self):
            del self._name
        return locals()
    name = property(**name())

    def control():
        doc = "The control property."
        def fget(self):
            return self._control
        def fset(self, value):
            self._control = value
        def fdel(self):
            del self._control
        return locals()
    control = property(**control())

class ControlsHtml(object):

    """Docstring for ControlsHtml. """

    def __init__(self, file, ctrl=None):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self.control_id = None
        self.control = ctrl
        self._start_html = None
        self._end_html = None
        self._css = None
        self._file_path = self._validate_file(file)
        self.load()

    def load(self):
        """TODO: Docstring for load.
        :returns: TODO

        """
        self.load_html(self.file_path)
        self.load_css(self.file_path)

    def start_html():
        doc = "The start_html property."
        def fget(self):
            return self._start_html
        def fset(self, value):
            self._start_html = value
        def fdel(self):
            del self._start_html
        return locals()
    start_html = property(**start_html())

    def end_html():
        doc = "The end_html property."
        def fget(self):
            return self._end_html
        def fset(self, value):
            self._end_html = value
        def fdel(self):
            del self._end_html
        return locals()
    end_html = property(**end_html())

    def css():
        doc = "The css property."
        def fget(self):
            return self._css
        def fset(self, value):
            self._css = value
        def fdel(self):
            del self._css
        return locals()
    css = property(**css())

    def file_path():
        doc = "The file_path property."
        def fget(self):
            return self._file_path
        def fset(self, value):
            self._file_path = self._validate_file(value)
        def fdel(self):
            del self._file_path
        return locals()
    file_path = property(**file_path())

    def get_html_as_template(self):
        return self._start_html + '{0}' + self._end_html

    def _validate_file(self, file):
        """TODO: Docstring for _validate_file.

        :file: TODO
        :returns: TODO

        """
        if path.exists(file):
            if path.getsize(file) <= 0 or path.isfile(path)==False:
                raise IOError('Can''t open file {0}'.format(file))
        else:
            raise IOError('File not found {0}'.format(file))

    def load_html(self, file):
        """TODO: Docstring for load_html.

        :file: TODO
        :returns: TODO

        """
        self._validate_file(file)
        with open(file) as f:
            counter = 0
            break_found=False
            for line in f:
                if line == '--':
                    continue
                elif line == '' or line ==linesep:
                    break_found=True
                    counter += 1
                    if counter > 1:
                        break
                else:
                    if break_found:
                        self.end_html+=line
                    else:
                        self.start_html+=line

    def load_css(self, file):
        """TODO: Docstring for load_css.

        :file: TODO
        :returns: TODO

        """
        file += '.css'
        self._validate_file(file)
        with open(file) as f:
            for line in f:
                self.css += line


class Container(UIElement):
    def __init__(self, name):
        UIElement.__init__(self, name)

