# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

# Registering blueprints.
from app.api.views import api
app.register_blueprint(api)

import sys
sys.path.append('..')


