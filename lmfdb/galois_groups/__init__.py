# -*- coding: utf-8 -*-
from base import app
from utils import make_logger
from flask import Blueprint

galois_groups_page = Blueprint("galois_groups", __name__, template_folder='templates', static_folder="static")
logger = make_logger(galois_groups_page)


@galois_groups_page.context_processor
def body_class():
    return {'body_class': 'galois_groups'}

import main

app.register_blueprint(galois_groups_page, url_prefix="/GaloisGroup")