""" Contains base interfaces for modules """


class Module:
    """ Base class for modules """

    def __init__(self, pi, state, queue, app, config):
        self._pi = pi
        self._state = state
        self._queue = queue
        self._app = app
        self._config = config

    def command(self, command, *args, **kwargs):
        """ Shorthand to fire a command """
        self._queue.enqueue(command, *args, **kwargs)

    def update(self):
        """ Called upon state changes """
        pass


class PollingModule(Module):
    """
    Base class for polling modules

    A polling module is added to the applications polling loop.
    It's poll() method is executed once every cycle.
    """

    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)

    def poll(self):
        """ Called in main polling loop"""
        pass


class ConsumingModule(Module):
    """
    Base class for the consuming module

    The consuming module is registered as the applications main module.
    It works the command queue and executes the incoming commands.
    """

    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)
        self._commands = {}

    def _register_commands(self, **kwargs):
        """
        Register handlers for all known commands

        The handlers will be automatically invoced, whenever a command is enqueued.
        TODO: Compare known handlers to commands provided in config.
        """
        self._commands = kwargs

    def _update_state(self, property, value):
        """ 
        Update state and notify about changes

        The consuming module is the only module that is allowed to write to the state.
        Therefore this method is hidden here.
        """

        if(self._state._update(property, value)):
            self._state._notify()
            return True

        return False

    def consume(self):
        """ Execute all commands from queue """

        while not self._queue.drained:
            command = self._queue.dequeue()

            while command is not None:
                override = self._commands.get(command.name)
                command = command.execute(override)
