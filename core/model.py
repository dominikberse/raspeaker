
from .config import Config

import threading
import logging


class Queue:
    """ 
    Stores commands sent to the device 

    Whenever a module wants to change the state, it has to do so using commands.
    The command is then consumed by the main module, which adjusts the state 
    according to the response of the physical device.

    The queue does provide a thread-lock that allows to wait for new commands.
    """

    class Command:
        def __init__(self, config):
            self._name = config.require(Config.Key).value
            self._params = config.value or {}

        @property
        def name(self):
            return self._name

        def make(self, **kwargs):
            """ 
            Make an element for the command queue 

            Validates the given parameters according to configuration.
            """

            for name, value in kwargs.items():
                if name not in self._params:
                    raise Exception(f'Unknown parameter "{name}"')

            return self, kwargs

        def __str__(self):
            arguments = (
                f'{name}: {type}' for name,
                type in self._params.items()
            )
            return f'{self._name}({", ".join(arguments)})'

    def __init__(self, config):
        self._commands = {}
        self._event = threading.Event()
        self._queue = []

        for item in config.items():
            command = Queue.Command(item)
            self._commands[command.name] = command
            logging.debug(f'command {command}')

    @ property
    def commands(self):
        """Gets the list of commands """

        return self._commands

    @ property
    def drained(self):
        """ Checks whether the queue is empty """

        return not self._queue

    def enqueue(self, command, **kwargs):
        """
        Enqueues a new command

        TODO: Documentation of parameters
        """

        # convert string to corresponding Command
        if isinstance(command, str):
            if command not in self._commands:
                raise Exception(f'Unknown command "{command}"')
            command = self._commands[command]

        if not isinstance(command, Queue.Command):
            raise Exception(f'Invalid command "{command}"')

        # verify command and enqueue
        self._queue.append(command.make(**kwargs))
        self._event.set()

    def dequeue(self):
        """ Dequeue the next command """

        if self._queue:
            return self._queue.pop(0)

    def clear(self):
        """ Clear the queue event """

        self._event.clear()

    def wait(self):
        """ Wait for a new command """

        self._event.wait()


class State:
    """ Stores the actual device state """

    class Element:
        def __init__(self, config):
            self._name = config.require('name').value

        @property
        def name(self):
            return self._name

        @property
        def value(self):
            return self._value

    class Number(Element):
        def __init__(self, config):
            super().__init__(config)
            self._value = 0

        @property
        def number(self):
            return self._value

        def __str__(self):
            return f'{self._name}: number'

    class Float(Element):
        def __init__(self, config):
            super().__init__(config)
            self._value = 0.0

        @property
        def float(self):
            return self._value

        def __str__(self):
            return f'{self._name}: float'

    class Enum(Element):
        def __init__(self, config):
            super().__init__(config)
            self._options = config.require('options').values()
            self._value = next(self._options)

        @property
        def enum(self):
            return self._value

        def __str__(self):
            return f'{self._name}: enum({", ".join(self._options)})'

    class Boolean(Element):
        def __init__(self, config):
            super().__init__(config)
            self._value = False

        @property
        def boolean(self):
            return self._value

        def __str__(self):
            return f'{self._name}: boolean'

    def __init__(self, config):
        self._state = {}
        self._event = threading.Event()

        # initialize the dictionary
        for item in config.items():
            element = item.switch('type', {
                "number": State.Number,
                "float": State.Float,
                "enum": State.Enum,
                "boolean": State.Boolean,
            })(item)
            self._state[element.name] = element
            logging.debug(f'state {element}')

    @property
    def properties(self):
        return self._state.values()

    def _update(self, property, value):
        if property not in self._state:
            raise Exception(f'Unknown state {property}')
        self._state[property] = value
        self._event.set()

    def get(self, property):
        if property not in self._state:
            raise Exception(f'Unknown state {property}')
        return self._state[property]

    def clear(self):
        self._event.clear()

    def wait(self):
        self._event.wait()
