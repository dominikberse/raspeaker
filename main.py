
from core.state import State
from core.queue import Queue
from core.service import Service
from core.config import Config
from core.module import Module

import logging
import pigpio
import flask
import os


# initialize logging
logging.basicConfig(level=logging.DEBUG)

# load config
yaml = os.environ.get('RASPEAKER_CONFIG', 'config.yaml')
config = Config.load(yaml)

# initialize webserver
app = flask.Flask(__name__)

# load GPIO
pi = pigpio.pi()
if not pi.connected:
    logging.error("GPIO not available")
    exit(0)

# initialize core
queue = Queue(config.optional('commands', {}))
state = State(config.require('states'), queue)

# initialize components
service = Service(state, queue)
for module in config.require('modules').items():
    type = module.single().oftype(Config.Key, 'modules', base=Module)
    instance = type(pi, state, queue, app, module.single())
    service.register(instance)

# run application
service.start()
app.run(host='0.0.0.0')
