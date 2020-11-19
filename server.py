# encoding: utf-8

from flask import Flask

app = Flask(__name__)
app.config.from_object("config")
app.jinja_env.trim_blocks = app.config["JINJA_ENV"]["TRIM_BLOCKS"]
app.jinja_env.lstrip_blocks = app.config["JINJA_ENV"]["LSTRIP_BLOCKS"]


@app.route("/")
def hello_world():
    return "Hello, World!"


# WSGI needs an "application" variable
application = app
