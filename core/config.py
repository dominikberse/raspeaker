""" Contains a simple interface to work with YAML configs """
import importlib
import yaml


class Config:
    """ Represents a partial or full YAML configuration """
    Key = '__key__'
    Value = '__value__'

    def __init__(self, key=None, value=None):
        self._key = key
        self._value = value

    @staticmethod
    def load(filename):
        """ Load config from YAML file """
        with open(filename, 'r') as file:
            content = yaml.safe_load(file.read())
            return Config(value=content)

    @property
    def value(self):
        return self._value

    def require(self, key):
        if key is None:
            raise Exception('Parameter key must not be None')
        if key is Config.Key:
            return Config(value=self._key)
        if key is Config.Value:
            return Config(value=self._value)
        if key not in self._value:
            raise Exception(f'"{key}" is required for "{self._key}"')
        return Config(key, self._value[key])

    def optional(self, key=None, fallback=None):
        if key is None:
            raise Exception('Parameter key must not be None')
        return Config(key, self._value.get(key, fallback))

    def items(self):
        if isinstance(self._value, dict):
            return (Config(key, value) for key, value in self._value.items())
        elif isinstance(self._value, list):
            return (Config(value=value) for value in self._value)
        else:
            return [self._value]

    def values(self):
        return [option.value for option in self.items()]

    def single(self):
        if isinstance(self._value, dict):
            if len(self._value) != 1:
                raise Exception("Expected exactly one key")
            return Config(*next(iter(self._value.items())))
        elif isinstance(self._value, list):
            if len(self._value) != 1:
                raise Exception("Expected exactly one item")
            return Config(value=next(self._value))
        else:
            return self._value

    def switch(self, key, options):
        value = self.require(key).value
        if value not in options:
            raise Exception(f'Invalid value "{value}" for "{key}"')
        return options[value]

    def oftype(self, key, module, base):
        submodule = self.require(key).value
        try:
            library = importlib.import_module(f'{module}.{submodule}')
            type_name = submodule.split('.')[-1].capitalize()
            type = getattr(library, type_name)
            assert(issubclass(type, base))
        except:
            raise Exception(f'Invalid value "{submodule}" for "{key}"')
        return type
