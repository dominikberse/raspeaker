from .element import Element


class Number(Element):
    def __init__(self, config):
        super().__init__(config, 0, {
            'set': self._set,
            'inc': self._inc,
            'dec': self._dec,
        })

        self._range = config.optional('range', [0, 100]).value

    def _inc(self):
        if self._value < self._range[1]:
            return self._call('set', self._value + 1)

    def _dec(self):
        if self._value > self._range[0]:
            return self._call('set', self._value - 1)

    def __str__(self):
        return f'{self._name}: number'
