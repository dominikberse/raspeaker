from .types import boolean, enum, number

import threading
import logging


class State:
    """ 
    Stores the actual device state 

    A state consists of multiple elements, which stores a single value of arbitrary type.
    Every element has predefiend commands, that can be used to adjust the elements value.
    The commands can be overriden by the main component in order to inject additional logic,
    that is required to apply the change to the physical device.
    """

    def __init__(self, config, queue):
        self._state = {}
        self._event = threading.Event()

        for item in config.items():

            # register the state element
            element = item.switch('type', {
                "number": number.Number,
                "enum": enum.Enum,
                "boolean": boolean.Boolean,
            })(item)
            self._state[element.name] = element

            # auto-generate commands for the element
            element.register_commands(queue)

    @property
    def properties(self):
        return self._state.values()

    def _update(self, property, value):
        if property not in self._state:
            raise Exception(f'Unknown state {property}')
        return self._state[property].force(value)

    def get(self, property):
        if property not in self._state:
            raise Exception(f'Unknown state {property}')
        return self._state[property].value

    def clear(self):
        self._event.clear()

    def wait(self):
        self._event.wait()

    def _notify(self):
        self._event.set()
