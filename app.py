# encoding: utf-8

import os
import re

from bleach import Cleaner
from bleach.linkifier import LinkifyFilter
from flask import Flask, g, redirect, render_template, url_for


application = Flask(__name__, template_folder=".")
application.config.from_object("config")
try:
    application.config.from_object(f"config-{application.config['ENV']}")
except Exception as e:
    print(
        "Starting without specific configuration"
        f"file config-{application.config['ENV']}.py"
    )
application.jinja_env.trim_blocks = application.config["JINJA_ENV"]["TRIM_BLOCKS"]
application.jinja_env.lstrip_blocks = application.config["JINJA_ENV"]["LSTRIP_BLOCKS"]

LOG_PATTERN = re.compile(application.config["LOG_PATTERN"])


def get_archives():
    archives = []
    dates = {"years": [], "months": {}, "days": {}}
    for filename in sorted(os.listdir(application.config["LOG_PATH"])):
        date = filename[:-4].split("-")[1:]
        archives.append(date)
        if date[0] not in dates["years"]:
            dates["years"].append(date[0])
            dates["months"][date[0]] = []
        if date[1] not in dates["months"][date[0]]:
            dates["months"][date[0]].append(date[1])
            dates["days"]["%s%s" % tuple(date[:2])] = []
        if date[2] not in dates["days"]["%s%s" % tuple(date[:2])]:
            dates["days"]["%s%s" % tuple(date[:2])].append(date[2])
    return archives, dates


@application.route("/")
@application.route("/archives/<year>")
@application.route("/archives/<year>/<month>")
@application.route("/archives/<year>/<month>/<day>")
def archives(year=None, month=None, day=None):
    # Récupération des fichiers disponibles
    archives, g.dates = get_archives()
    # Récupération de la date souhaitée
    if (
        year is None
        or month is None
        or day is None
        or [year, month, day] not in archives
    ):
        # Si date mal ou non fournie ou inexistante, on prend la dernière
        year = archives[-1][0]
        month = archives[-1][1]
        day = archives[-1][2]
        # Et on redirige proprement
        return redirect(url_for("archives", year=year, month=month, day=day))
    # Ok, on charge et on affiche le contenu du fichier
    filename = "log-%s-%s-%s.txt" % (year, month, day)
    filepath = os.path.join(application.config["LOG_PATH"], filename)
    with open(filepath, encoding="utf-8") as f:
        lines = f.read().splitlines()
    g.lines = []
    g.year, g.month, g.day = year, month, day
    cleaner = Cleaner(tags=["b"], filters=[LinkifyFilter])
    for line in lines:
        result = LOG_PATTERN.match(line)
        if result is not None:
            message = cleaner.clean(result.group("message"))
            g.lines.append(
                {
                    "time": result.group("time"),
                    "nick": result.group("nick"),
                    "message": message,
                }
            )

    return render_template("template.html")
