# Core fields to be used in the framework
# Author: Ajeet Singh
import uuid


class Field:
    def __init__(self, name):
        self._key = uuid.uuid4()
        self._field_name = name
        self._field_value = ''
        self._security_key = ''
        self.field_type = None
        self._required = False

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def field_name(self):
        return self._field_name

    @field_name.setter
    def field_name(self, value):
        if value is not None:
            self._field_name = value
        else:
            raise ValueError('Invalid value provided')

    @property
    def field_value(self):
        return self._field_value

    @field_value.setter
    def field_value(self, value):
        if value is not None:
            self._field_value = value
        else:
            raise ValueError('Invalid value passed')

    @property
    def security_key(self):
        return self._security_key

    @security_key.setter
    def security_key(self, value):
        if value is not None:
            self._security_key = value
        else:
            raise ValueError('Invalid value passed')

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, value):
        if value is not None:
            self._required = value
        else:
            raise ValueError('Invalid value provided')

    def __str__(self):
        return '{0}'.format(self.field_value)

    def __repr__(self):
        return repr(self.field_value)

class CharField(Field):
    def __init__(self, name, max_length=100, required=True, default=''):
        Field.__init__(self, name)
        self._max_length = max_length
        self._field_value = default if len(default) < max_length else default[1:max_length]
        self.required = required
        self.field_type = 'str'

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, value):
        if value is not None:
            self._max_length = value
        else:
            raise ValueError('Invalid value provided')

    @property
    def field_value(self):
        return self._field_value

    @field_value.setter
    def field_value(self, value):
        if value is None:
            raise ValueError('Invalid value provided')
        if len(value) > self.max_length:
            self.field_value = value[1:self.max_length]
        else:
            self.field_value = value

class TextField(CharField):
    MAX_ROWS = 100
    MAX_COLUMNS = 100

    def __init__(self, name, max_length=500, required=True, default='', rows=10, columns=50):
        CharField.__init__(self, name, max_length, required, default)
        self.field_type = 'text'
        self._rows = rows
        self._columns = columns

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        if value is None:
            raise ValueError('Invalid value passes')
        if value >= MAX_COLUMNS:
            raise ValueError('Value of rows can not be greater then {0}'.format(MAX_ROWS))
        else:
            self._rows = value

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        if value is None:
            raise ValueError('Invalid value passed')
        if value >= MAX_ROWS:
            raise ValueError('Value of columns can not be greater than {0}'.format(MAX_ROWS))
        else:
            self._columns = value

class IntegerField(Field):
    def __init__(self, name, required=True, default=0):
        Field.__init__(self, name)
        self.field_type = 'int'
        self._field_value = 0 if (default is None or default == '') else default

    @property
    def field_value(self):
        return self._field_value

    @field_value.setter
    def field_value(self, value):
        try:
            self._field_value = int(value)
        except:
            raise ValueError('Invalid value provided')

    def __add__(self, val):
        return (self.field_value + val.field_value)

    def __sub__(self, val):
        return (self.field_value - val.field_value)

    def __mul__(self, val):
        return (self.field_value * val.field_value)

    def __div__(self, val):
        if(val.field_value != 0):
            return (self.field_value / val.field_value)

        return 0

class BooleanField(Field):
    def __init__(self, name, required=True, default=False):
        Field.__init__(self, name)
        self.field_type = 'bool'
        self.required = required
        self._field_value = default

    @property
    def field_value(self):
        return _field_value

    @field_value.setter
    def field_value(self, value):
        if value is None:
            raise ValueError('Invalid value provided')
        if value == True or value == False:
            self._field_value = value
        else:
            raise ValueError('Invalid value passed')

class FloatField(IntegerField):
    def __init__(self, name, required=True, default=0.0):
        IntegerField.__init__(self, name, required, default)
        self.field_type = 'float'
        self._field_value = 0.0 if (default is None or default == '') else default

    @property
    def field_value(self):
        return self._field_value

    @field_value.setter
    def field_value(self, value):
        if value is None:
            raise ValueError('Invalid value provided')
        try:
            self._field_value = float(value)
        except:
            raise ValueError('Invalid value provided')

class SingleSelectionList(Field):
    def __init__(self, name, required=True, default=[]):
        Field.__init__(self, name)
        self.required = True
        self._list = []
        self._selected_index = -1
        self._selected_value = None
        self._field_value = ''
        self.field_type = 'ss_list'
        if len(default) > 0:
            for item in default:
                self._list.append(item)

    def get_list(self):
        return self._list

    def select(self, value):
        if self._list.__contains__(value):
            self._selected_index = self._list.index(value)
            self._selected_value = value
        else:
            raise ValueError('Provided value does not exists in list')

    @property
    def selected_index(self):
        return self._selected_index

    @selected_index.setter
    def selected_index(self, index):
        if index < len(self._list):
            self._selected_index = index
            self._selected_value = self._list[index]
        else:
            raise ValueError('Index provided is not in range')

    @property
    def selected_value(self):
        return self._selected_value

    @selected_value.setter
    def selected_value(self, value):
        self.select(value)

class MultiSelectionList(Field):
    def __init__(self, name, required=True, default=[]):
        Field.__init__(self, name)
        self.required = required
        self._list = {}
        self._selected_indices = []
        self._selected_values = []
        self._counter = -1
        self._field_value = ''
        if len(default) > 0:
            for item in default:
                _list[item] = _counter
                _counter += 1

    def select(self, values=[]):
        for val in values:
            if self._list.keys().contains(val):
                self._selected_values.append(val)
                self._selected_indices.append(self._list[val])

    def select_indices(self, indices=[]):
        for idx in indices:
            if idx < len(_list) and self._list.values().contains(idx):
                for key, val in self._list.iteritems():
                    if val == idx:
                        self._selected_values.append(key)
                        self._selected_indices.append(val)

    def unselect_indices(self, indices=[]):
        for idx in indices:
            if self._selected_indices.contains(idx):
                for key, val in self._list.iteritems():
                    if val == idx:
                        self._selected_values.remove(key)
                        self._selected_indices.remove(val)


    def unselect(self, values=[]):
        for val in values:
            if self._selected_values.contains(val):
                val_index = self._list[val]
                self._selected_values.remove(val)
                self._selected_indices.remove(val_index)

    def select_all(self):
        if len(self._list) > 0:
            self._selected_values = self._list.keys()
            self._selected_indices = self._list.values()

    def unselect_all(self):
        if len(self._selected_values) > 0:
            self._selected_values.clear()
        if len(self._selected_indices) > 0:
            self._selected_indices.clear()

    @property
    def selected_values(self):
        return self._selected_values

    @selected_values.setter
    def selected_values(self, values):
        self.select(values)

    @property
    def selected_indices(self):
        return self._selected_indices

    @selected_indices.setter
    def selected_indices(self, values):
        self.select_indices(values)

    def get_list(self):
        return self._list.keys()

    def get_dict(self):
        return self._list
