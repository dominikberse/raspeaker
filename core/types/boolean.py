from .element import Element


class Boolean(Element):
    def __init__(self, config):
        super().__init__(config, False, {
            'set': self._set,
            'toggle': self._toggle,
        })

    def _toggle(self):
        return self._call('set', not self._value)

    def __str__(self):
        return f'{self._name}: boolean'
