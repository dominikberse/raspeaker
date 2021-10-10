
from core.module import ConsumingModule
from core import pins

import logging
import pigpio
import time


class Controller(ConsumingModule):
    """ Injects I2C communication between the AltecLansing main unit and satellite """

    I2C_ADDRESS = 0x45

    CMD_POWER = 0xE0
    CMD_VOLUME = 0xE1
    CMD_BALANCE = 0xE2

    MIN_VOL = 111
    MAX_VOL = 26

    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)
        self._register_commands(
            power_set=self._cmd_power_set,
            volume_set=self._cmd_volume_set,
            treble_set=self._cmd_treble_set,
            bass_set=self._cmd_bass_set,
        )

        self._bus = config.require('i2c').value

        # register as I2C slave
        self._event = pi.event_callback(pigpio.EVENT_BSC, self._receive)
        pi.bsc_i2c(Controller.I2C_ADDRESS)

        # establish I2C master connection
        self._synchronize_i2c()

        # register known satellite commands
        self._satellite_commands = {
            Controller.CMD_POWER: self._handle_power,
            Controller.CMD_VOLUME: self._handle_volume,
            Controller.CMD_BALANCE: self._handle_balance,
            0xE4: self._pass,
            0xE6: self._pass,
        }

    def from_4bit(self, value):
        """ Convert from strange 4-bit format (inverted sign and magnitude) """
        return int(~value & 0b0111) if value & 0b1000 else ~int(~value & 0b0111)

    def from_packed_4bit(self, value):
        """ Convert two packed 4 bit values to integers """
        return self.from_4bit(value >> 4), self.from_4bit(value & 0b1111)

    def to_4bit(self, value):
        """ Convert to strange 4-bit format (inverted sign and magnitude) """
        return (value & 0b0111) if value < 0 else (~value & 0b1111)

    def to_packed_4bit(self, high, low):
        """ Convert two integers to packed 4 bit values """
        return (self.to_4bit(high) << 4) | self.to_4bit(low)

    def _synchronize_i2c(self):
        """ Ensure I2C is enabled by pulling SDA high """

        # send SDA high over I2C pins (for 300ms)
        logging.info(f'synchronizing i2c{self._bus}')
        self._pi.set_mode(2, pigpio.OUTPUT)
        self._pi.set_mode(3, pigpio.OUTPUT)
        self._pi.write(2, 1)
        self._pi.write(3, 0)
        time.sleep(0.3)

        # reset output pins to be available for I2C
        self._pi.set_mode(2, pigpio.ALT0)
        self._pi.set_mode(3, pigpio.ALT0)

        # register as I2C master
        logging.info(f'connecting over i2c{self._bus}')
        self._i2c = self._pi.i2c_open(self._bus, Controller.I2C_ADDRESS)

    def _send_command(self, command, value):
        """ Send a single command over I2C """
        try:
            logging.debug(f'sending {bytes([command, value])}')
            self._pi.i2c_write_device(self._i2c, [command, value])
        except Exception as e:
            logging.exception('failed to send')

    def _send_state(self):
        """ Transmit the current state to the main unit """
        volume = Controller.MIN_VOL - self._state.get('volume')
        treble = self._state.get('treble')
        bass = self._state.get('bass')
        balance = self.to_packed_4bit(bass, treble)

        if self._state.get('power'):
            self._send_command(Controller.CMD_VOLUME, volume)
            self._send_command(Controller.CMD_BALANCE, balance)
            self._send_command(0xE4, 0x00)
            self._send_command(0xE6, 0x00)
            self._send_command(Controller.CMD_POWER, 0x01)

    def _cmd_power_set(self, power):
        if self._update_state('power', power):
            self._send_state()

    def _cmd_volume_set(self, volume):
        if self._update_state('volume', volume):
            self._send_state()

    def _cmd_treble_set(self, treble):
        if self._update_state('treble', treble):
            self._send_state()

    def _cmd_bass_set(self, bass):
        if self._update_state('bass', bass):
            self._send_state()

    def _handle_power(self, value):
        self.command('power_set', value)

    def _handle_volume(self, value):
        self.command('volume_set', Controller.MIN_VOL - value)

    def _handle_balance(self, value):
        bass, treble = self.from_packed_4bit(value)
        self.command('treble_set', treble)
        self.command('bass_set', bass)

    def _pass(self, value):
        pass

    def _receive(self, id, tick):
        """ Receive command from satellite """

        _, count, data = self._pi.bsc_i2c(Controller.I2C_ADDRESS)
        logging.debug(f'received {count} bytes: {data}')

        # parse command and forward to handler to update state
        for i in range(0, count, 2):
            handler = self._satellite_commands.get(data[i], None)
            if handler is None:
                logging.warning(f'received unknown command {data[i]}')
                continue
            handler(data[i+1])
