
from core.module import ConsumingModule
from core import pins

import logging
import pigpio


class Controller(ConsumingModule):
    """ Injects I2C communication between the AltecLansing main unit and satellite """

    I2C_ADDRESS = 0x45

    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)
        self._bus = config.require('i2c').value

        # register as I2C slave
        self._event = pi.event_callback(pigpio.EVENT_BSC, self._receive)
        self._pi.bsc_i2c(Controller.I2C_ADDRESS)

        # register as I2C master
        self._i2c = self._pi.i2c_open(self._bus, Controller.I2C_ADDRESS)

    def _receive(self, id, tick):
        """ Receive command from satellite """

        _, count, data = self._pi.bsc_i2c(Controller.I2C_ADDRESS)

        # parse command to update internal state
        if count == 2:
            pass

        # forward command to main unit
        self._pi.i2c_write_device(self._i2c, data)
