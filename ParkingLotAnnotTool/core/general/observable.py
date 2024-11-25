from PyQt6.QtCore import QObject, pyqtSignal


class Observable(QObject):
    data_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def notify_observers(self, message):
        self.data_changed.emit(message)


class ObservableValue(Observable):
    def __init__(self, initial_value=None):
        super().__init__()
        self._value = initial_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if self._value != new_value:
            self._value = new_value
            self.notify_observers(new_value)


class ObservableList(Observable):
    def __init__(self, *args):
        super().__init__()
        self._list = list(*args)

    def __getattr__(self, name):
        attr = getattr(self._list, name)
        if callable(attr):
            def hooked(*args, **kwargs):
                result = attr(*args, **kwargs)
                self.notify_observers(f"Called {name} with args: {args}, kwargs: {kwargs}")
                return result
            return hooked
        else:
            return attr

    def __setitem__(self, index, value):
        self._list[index] = value
        self.notify_observers(f"Set index {index} to {value}")

    def __getitem__(self, index):
        return self._list[index]

    def __delitem__(self, index):
        del self._list[index]
        self.notify_observers(f"Deleted item at index {index}")

    def __len__(self):
        return len(self._list)


class ObservableDict(Observable):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)

    def __getattr__(self, name):
        attr = getattr(self._dict, name)
        if callable(attr):
            def hooked(*args, **kwargs):
                result = attr(*args, **kwargs)
                self.notify_observers(f"Called {name} with args: {args}, kwargs: {kwargs}")
                return result
            return hooked
        else:
            return attr

    def __setitem__(self, key, value):
        self._dict[key] = value
        self.notify_observers(f"Set key {key} to {value}")

    def __getitem__(self, key):
        return self._dict[key]

    def __delitem__(self, key):
        del self._dict[key]
        self.notify_observers(f"Deleted key {key}")

    def __len__(self):
        return len(self._dict)
