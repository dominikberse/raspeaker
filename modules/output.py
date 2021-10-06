from core.module import Module

import logging
import pigpio


class Output(Module):
    """ Toggles a GPIO output pin """

    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)

        self._element = config.require('state').value
        self._pin = config.pin('pin')

        pi.set_mode(self._pin.number, pigpio.OUTPUT)
        logging.info(f'pin {self._pin} output')

    def update(self):
        level = self._state.get(self._element) ^ self._pin.invert
        logging.debug(f'set pin {self._pin.number} to {level}')
        self._pi.write(self._pin.number, level)
