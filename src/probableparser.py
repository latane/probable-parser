#!/usr/bin/env python3

import configparser
from flask import Flask, Response
from flask_cors import CORS
from webapp import app


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
        
    #app.run(threaded=True, host=config['DEFAULT']['WEB_HOST'], port=int(config['DEFAULT']['WEB_PORT']))
    app.run(threaded=True, host="0.0.0.0", port=8080)
