# Script: models.py
# Author: Ajeet Singh
import uuid

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

