from core.module import Module

import logging
import flask


class Api(Module):
    def __init__(self, pi, state, queue, app, config):
        super().__init__(pi, state, queue, app, config)

        # register all known endpoints
        self._app.add_url_rule(
            "/state",
            view_func=self._get_state,
            methods=['GET'])
        self._app.add_url_rule(
            "/command",
            view_func=self._post_command,
            methods=['POST'])

    def _get_state(self):
        """ Get device state """

        return flask.jsonify({
            property.name: property.value
            for property in self._state.properties
        })

    def _post_command(self):
        """ Execute arbitrary command """
        try:
            command = flask.request.json['command']
            params = flask.request.json.get('params', {})
            self._queue.enqueue(command, **params)

            # command can indicate to wait for actual state change
            # this can fail, if the command does not issue a change
            # TODO: add timeout
            if flask.request.json.get('wait') == True:
                self._state.wait()
                return self._get_state()

            return flask.jsonify({})

        except:
            logging.exception('invalid request')
            return flask.jsonify({}), 400
