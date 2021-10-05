import threading
import logging


class Queue:
    """ 
    Stores commands sent to the device 

    Whenever a module wants to change the state, it has to do so using commands.
    The command can be consumed by the main module in order to run further logic 
    that is required to control the physical device.

    The queue does provide a thread-lock that allows to wait for new commands.
    """

    class Command:
        def __init__(self, command, handler, args, kwargs):
            self._command = command
            self._handler = handler
            self._args = args
            self._kwargs = kwargs

        @property
        def name(self):
            return self._command

        def execute(self, override=None):
            if override is None:
                override = self._handler
            if override is None:
                raise Exception(f'No handler for {self._command}()')

            logging.info(
                f'execute {self._command}({self._args}, {self._kwargs})')
            derivate = override(*self._args, **self._kwargs)
            if derivate is None:
                return None

            # return derived command that is executed afterwards
            (command, args) = derivate
            logging.info(f'continue with {command}({args})')
            return Queue.Command(command, None, args, {})

    def __init__(self, config):
        self._commands = {}
        self._event = threading.Event()
        self._queue = []

        for item in config.values():
            self.register(item)

    @ property
    def commands(self):
        """Gets the list of registered commands """

        return self._commands

    @ property
    def drained(self):
        """ Checks whether the queue is empty """

        return not self._queue

    def register(self, command, handler=None):
        """ Register a new command """

        registered = self._commands.get(command)
        if registered is not None:
            raise Exception(f'Multiple handlers for {command}()')

        self._commands[command] = handler
        logging.debug(f'registered {command}()')

    def enqueue(self, command, *args, **kwargs):
        """ Enqueues a new command """

        if command not in self._commands:
            raise Exception(f'Unknown command {command}()')

        handler = self._commands[command]
        self._queue.append(Queue.Command(command, handler, args, kwargs))
        self._event.set()

    def dequeue(self):
        """ Dequeues the next command """

        if self._queue:
            return self._queue.pop(0)

    def clear(self):
        """ Clears the queue event """

        self._event.clear()

    def wait(self):
        """ Waits for a new command """

        self._event.wait()
