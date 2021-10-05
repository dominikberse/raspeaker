from .element import Element


class Enum(Element):
    def __init__(self, config):
        self._options = [config.require('options').values()]
        super().__init__(config, self._options[0], {
            'set': self._set,
            'toggle': self._toggle,
        })

    def _force(self, value):
        if value not in self._options:
            raise Exception('Invalid value {self._value} for {self._name}')
        return super()._force(value)

    def _toggle(self):
        next = (self._options.index(self._value) + 1) % len(self._options)
        return self._call('set', self._options[next])

    def __str__(self):
        return f'{self._name}: enum({", ".join(self._options)})'
