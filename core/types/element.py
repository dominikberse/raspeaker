from core.config import Config

import logging


class Element:
    def __init__(self, config, default, templates):
        self._name = config.require(Config.Key).value
        self._value = config.optional('initial', default).value
        self._templates = templates

        logging.info(f'registered state.{self._name}={self._value}')

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def _command(self, name):
        return f'{self._name}_{name}'

    def _call(self, command, *args):
        return (self._command(command), args)

    def _set(self, value):
        self.force(value)

    def register_commands(self, queue):
        """ 
        Register all predefined commands for this element 
        """

        for name, handler in self._templates.items():
            queue.register(self._command(name), handler)

    def force(self, value):
        """ 
        Directly changes the state of the value

        Must only be called from the main component. Otherwise changes to the
        state might not be handled or recognized correctly.
        """

        if self._value != value:
            logging.info(f'state.{self._name}={value}')
            self._value = value
            return True

        return False
