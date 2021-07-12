#!/usr/bin/env python3

import configparser
from flask import Flask, Response
from flask_cors import CORS
from webapp import app


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    app_host = config["DEFAULT"]["WEB_HOST"]
    # app_host = "0.0.0.0"
    app_port = int(config["DEFAULT"]["WEB_PORT"])
    # app_port = 8080
    app.run(threaded=True, host=app_host, port=app_port)
    # app.run(threaded=True, host="0.0.0.0", port=8080)
