#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, send_from_directory, redirect, request
from wlanpi_webui.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from wlanpi_webui.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from wlanpi_webui.speedtest import bp as speedtest_bp
    app.register_blueprint(speedtest_bp)

    from wlanpi_webui.profiler import bp as profiler_bp
    app.register_blueprint(profiler_bp)

    from wlanpi_webui.fpms import bp as fpms_bp
    app.register_blueprint(fpms_bp)

    @app.route("/cockpit")                          
    def cockpit():                                 
        cp_port = "9090"                           
        base = request.host.split(":")[0]          
        return redirect(f"http://{base}:{cp_port}")

    @app.route("/static/img/<path:filename>")
    def img(filename):
        try:
            return send_from_directory(f"{app.root_path}/static/img/", filename)
        except FileNotFoundError:
            abort(404)

    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/wlanpi_webui.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('wlanpi_webui startup')

    return app
