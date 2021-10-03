
from core.model import State, Queue
from core.service import Service
from core.config import Config
from core.module import Module

import logging
#import pigpio
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
pi = None  # pigpio.pi()
# if not pi.connected:
#    logging.error("GPIO not available")
#    exit(0)

# initialize core
state = State(config.require('states'))
queue = Queue(config.require('commands'))

# initialize components
service = Service(state, queue)
for module in config.require('modules').items():
    type = module.single().oftype(Config.Key, 'modules', base=Module)
    instance = type(pi, state, queue, app, module.single().items())
    service.register(instance)

# run application
service.start()
app.run(host='0.0.0.0')
