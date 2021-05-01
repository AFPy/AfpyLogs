# encoding: utf-8

SECRET_KEY = "Choose a secret key"

JINJA_ENV = {
    "TRIM_BLOCKS": True,
    "LSTRIP_BLOCKS": True,
}

LOG_PATH = "/var/www/logs.afpy.org"

# IRSSI log pattern
DATE_FORMAT = "(\d+-\d+-\d+ )?(?P<time>\d\d:\d\d)"
LOG_PATTERN = r"^%s\s+[<*]\s*(?P<nick>[^> ]+)[> ]\s+(?P<message>.*)$" % DATE_FORMAT

BOLD_PATTERN = r"\*[^*\s]+\*"
BOLD_HTML = "<b>{text}</b>"