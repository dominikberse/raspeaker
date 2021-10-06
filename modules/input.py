from core.module import Module

import logging
import pigpio


class Input(Module):
    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)

        self._pin = config.pin('pin')
        self._mode = config.optional('mode', 'toggle').value
        self._set = config.optional('set').value
        self._edge = config.optional('edge', 'falling').value

        if self._mode == 'switch':
            mode = pigpio.EITHER_EDGE
        elif self._edge == 'falling':
            mode = pigpio.FALLING_EDGE
        elif self._edge == 'rising':
            mode = pigpio.RISING_EDGE

        # register callback for input pin
        self._callback = pi.callback(self._pin.number, mode, self._change)
        logging.info(f'pin {self._pin} {self._mode}')

    def _change(self, pin, level, tick):
        logging.debug(f'pin {pin} changed to {level}')

        if self._mode == 'switch':
            # switch has internal state
            self.command(self._set, level ^ self._pin.invert)
        else:
            # toggle does not have state
            self.command(self._set)
