import os
import configparser
from flask import Flask, Response, request
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app)

# base landing
@app.route("/")
def index():
    return Response("Great job, you got here", status=200)


